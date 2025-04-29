import yaml
from datetime import datetime
import jsonschema
from json import load
from .neo_connect import neo_connect
from .neo_contributors import neo_contributors
from .neo_creators import neo_creators
from .neo_title import neo_title
from .neo_subjects import neo_subjects
from .neo_location import neo_location
from .neo_identifier import neo_identifier
from .neo_relatedIdentifiers import neo_relatedIdentifiers
from .neo_dates import neo_dates
from .neo_size import neo_size
from .neo_description import neo_description
from datacite import schema45
import requests
import psycopg2
import psycopg2.extras
import deepdiff.diff as dd
from json import dumps
from enum import Enum
from typing import Literal

class testMode(Enum):
    test = 'https://api.test.datacite.org/dois/'
    prod = 'https://api.datacite.org/dois/'


class credentials:
    def __init__(self, datacite_meta:dict):
        assert isinstance(datacite_meta, dict), 'You must pass a `dict` as the metatdata.'
        assert all([i in datacite_meta.keys() for i in ['user', 'mode']]), 'Your client metadata must be a dict with the keys `user`, and `mode`.'
        assert all([i in datacite_meta.get('mode').keys() for i in ['test', 'prod']]), 'You must have production and test data in your client credentials.'
        self.data = datacite_meta
    def mode(self, mode: testMode = testMode.test):
        output = self.data.get('mode').get(mode.name)
        output['username'] = self.data.get('user')
        return output

class neotomaDOI:
    def __init__(self, datasetid:int, defaults: str = None):
        if defaults:
            with open(defaults, 'r') as file:
                self.defaults = yaml.safe_load(file)
        else:
            self.defaults = {}
        self.datasetid = datasetid
        self.mode = testMode.test
        self.data = {
            "creators": None,
            "titles": None,
            "publisher": self.defaults.get("publisher"),
            "publicationYear": str(datetime.now().year),
            "types": self.defaults.get("types"),
            "schemaVersion": self.defaults.get("schemaVersion"),
            "language": self.defaults.get("language"),
            "rightsList": self.defaults.get("rightsList"),
            "formats": self.defaults.get("formats")
        }
        self.meta = {}
        self.schema = None
        self.client = None
        self.datacite_url = testMode.test
    def __str__(self):
        return dumps(self.data)
    def add_schema(self, schema):
        with open(schema, 'r', encoding = 'UTF-8') as f:
            self.schema = load(f)
    def validate(self, schema:str = None):
        if schema is not None:
            self.add_schema(schema)
        if self.schema is not None:
            return jsonschema.validate(instance=self.data, schema=self.schema)
        else:
            return schema45.validator.validate(self.data)
    def update(self):
        if self.datasetid:
            con = neo_connect()
            try:
                self.data['creators'] = neo_creators(con, self)
                self.data['contributors'] = neo_contributors(con, self)
                self.data['titles'] = [neo_title(con, self)]
                self.data['subjects'] = neo_subjects(con, self)
                self.data['geoLocations'] = neo_location(con, self)
                self.identifiers = neo_identifier(con, self)
                self.data['relatedIdentifiers'] = neo_relatedIdentifiers(con, self)
                self.data['dates'] = neo_dates(con, self)
                self.data['sizes'] = neo_size(con, self)
                self.data['descriptions'] = neo_description(con, self)
            except Exception as e:
                raise ValueError(f"Dataset {self.datasetid} is missing critical metadata values in the database.")
    def set_user(self, cred:credentials, mode: testMode = testMode.test):
        if not isinstance(cred, credentials):
            raise TypeError('Credentials must be of type neotomadoi.credential')
        self.client = cred
        self.mode = mode
    def test_mode(self):
        self.mode = testMode.test
    def prod_mode(self):
        if self.client is None:
            raise ValueError("You cannot use production mode without credentials.")
        self.mode = testMode.prod
    def get_mode(self):
        return print(f'mode: {self.mode.name}; URL: {self.mode.value}')
    def get_meta(self):
        if self.identifiers:
            dois = self.identifiers.get('identifier')
            doi_call = requests.get(self.mode.value + dois)
            if doi_call.status_code == 200:
                self.meta = doi_call.json().get('data').get('attributes')
    def update_doi(self):
        outcome = None
        try:
            outcome = self.validate()
        except Exception as e:
            outcome = True
        if outcome:
            print('Validation error. Check with the `validate()` method.')
            return None
        doi = self.identifiers.get('identifier')
        self.get_meta()
        version = self.meta.get('version')
        if version:
            version = version.split('.')
            version[1] = int(version[1]) + 1
            self.data['version'] = '.'.join([str(i) for i in version])
        else:
            self.data['version'] = '1.1'
        payload = {
            'data': {
                'type': 'dois',
                'attributes': self.data,
                'action': 'update'
        }}
        try:
            modifier = requests.put(self.mode.value + self.identifiers.get("identifier"),
                        headers = {'Content-Type': 'application/vnd.api+json'},
                        auth = (self.client.mode(self.mode).get('username'),
                                self.client.mode(self.mode).get('pw')),
                        json = payload)
            if modifier.status_code != 200:
                raise requests.RequestException(f'Failed to modify DOI: {modifier.text}')
            else:
                self.meta = self.get_meta()
        except Exception as e:
            print(e)
    def mint_doi(self):
        if self.identifiers:
            self.update_doi()
        else:
            outcome = None
            try:
                self.data['version'] = '1.0'
                outcome = self.validate()
            except Exception as e:
                outcome = True
            if outcome:
                print('Validation error. Check with the `validate()` method.')
                return None
        payload = {
            "type": "dois",
            "attributes": self.data
        }
        payload['attributes']['event'] = "publish"
        payload['attributes']['prefix'] = self.client.mode(self.mode).get('handle')
        payload['attributes']['url'] = f'https://data.neotomadb.org/datasets/{self.datasetid}'
        payload['attributes']['version'] = '1.0'
        try:
            created = requests.post(self.mode.value,
                                headers = {'Content-Type': 'application/vnd.api+json'},
                                auth = (self.client.mode(self.mode).get('username'),
                                        self.client.mode(self.mode).get('pw')),
                                json = {'data': payload})
            if created.status_code != 201:
                raise requests.RequestException(f'Failed to create DOI: {created.text}')
            else:
                #self.meta = created.json().get('data').get('attributes')
                self.identifiers = {'identifier': created.json().get('data').get('id'),
                                     'identifierType': 'DOI'}
                self.get_meta()
                insertQuery = """INSERT INTO ndb.datasetdoi (datasetid, doi, recdatecreated)
                                 VALUES (%(datasetid)s, %(identifier)s, NOW()::timestamp)
                                 RETURNING datasetid"""
                con = neo_connect()
                with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    cur.execute(insertQuery, {'datasetid': self.datasetid,
                                              'identifier': self.identifiers[0].get('identifier')})
        except Exception as e:
            print(e)
    def meta_diff(self):
        current = self.data
        old = self.meta[0]
        self.meta_diff = dd.DeepDiff(old, current, ignore_order = True)
    def deactivate(self):
        if self.identifiers:
            self.update_doi()
        else:
            outcome = None
            try:
                outcome = self.validate()
            except Exception as e:
                outcome = True
            if outcome:
                print('Validation error. Check with the `validate()` method.')
                return None
        payload = {
            "type": "dois",
            "attributes": self.data
        }
        payload['attributes']['event'] = "hide"
        payload['attributes']['prefix'] = self.client.get('prefix')
        payload['attributes']['url'] = f'https://data.neotomadb.org/datasets/{self.datasetid}'
        payload['attributes']['version'] = '1.0'
        try:
            created = requests.put(self.mode.value,
                                headers = {'Content-Type': 'application/vnd.api+json'},
                                auth = (self.client.get('username'), self.client.get('password')),
                                json = {'data': payload})
            if created.status_code != 200:
                raise requests.RequestException(f'Failed to create DOI: {created.text}')
            else:
                self.meta = created.json().get('data').get('attributes')
                self.identifiers = [{'identifier': created.json().get('data').get('id'),
                                     'identifierType': 'DOI'}]
                insertQuery = """INSERT INTO ndb.datasetdoi (datasetid, doi, recdatecreated)
                                 VALUES (%(datasetid)s, %(identifier)s, NOW()::timestamp)
                                 RETURNING datasetid"""
                con = neo_connect()
                with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    cur.execute(insertQuery, {'datasetid': self.datasetid,
                                              'identifier': self.identifiers[0].get('identifier')})
        except Exception as e:
            print(e)
    def freeze_data(self, con, force:bool = False):
        if self.datasetid:
            con = neo_connect()
            query = """
                SELECT * FROM doi.frozen
                WHERE datasetid = %(datasetid)s"""
            with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(query, {'datasetid': self.datasetid})
                result = cur.fetchone()
            if not result:
                freeze = """
                    INSERT INTO doi.frozen (datasetid, download, recdatecreated)
                    SELECT df.datasetid,
                           df.record AS download,
                        current_timestamp AS recdatecreated
                    FROM doi.doifreeze(ARRAY[%(datasetid)s]) as df
                    ON CONFLICT DO NOTHING;
                """
                with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    cur.execute(freeze, {'datasetid': self.datasetid})
                    cur.execute("SELECT * FROM doi.frozen WHERE datasetid = %(datasetid)s;",
                                {'datasetid': self.datasetid})
                    frozen_result = cur.fetchall()
                if len(frozen_result) > 0:
                    print("Dataset frozen.")
            else:
                raise ValueError("This dataset has already been frozen in the database. You must override manually.")
        else:
            raise ValueError("Dataset must have a valid datasetid and be in Neotoma to freeze the dataset.")