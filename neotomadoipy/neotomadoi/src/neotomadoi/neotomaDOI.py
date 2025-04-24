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


class neotomaDOI:
    def __init__(self, datasetid:int, defaults: str = None):
        if defaults:
            with open(defaults, 'r') as file:
                self.defaults = yaml.safe_load(file)
        else:
            self.defaults = {}
        self.datasetid = datasetid
        self.data = {
            "creators": None,
            "titles": None,
            "publisher": self.defaults.get("publisher")[0],
            "publicationYear": str(datetime.now().year),
            "types": self.defaults.get("types"),
            "schemaVersion": self.defaults.get("schemaVersion"),
            "language": self.defaults.get("language"),
            "rightsList": self.defaults.get("rightsList"),
            "formats": self.defaults.get("formats")
        }
        self.schema = None
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
                self.identifiers = [neo_identifier(con, self)]
                self.data['relatedIdentifiers'] = neo_relatedIdentifiers(con, self)
                self.data['dates'] = neo_dates(con, self)
                self.data['sizes'] = neo_size(con, self)
                self.data['descriptions'] = neo_description(con, self)
            except Exception as e:
                raise ValueError(f"Dataset {self.datasetid} is missing critical metadata values in the database.")
    def set_user(self, datacite_meta):
        self.client = datacite_meta
    def get_meta(self):
        self.meta = []
        if self.identifiers:
            dois = [i.get('identifier') for i in self.identifiers if i.get('identifierType') == 'DOI']
            for i in dois:
                doi_call = requests.get(f'https://api.test.datacite.org/dois/{i}')
                if doi_call.status_code == 200:
                    self.meta.append(doi_call.json().get('data').get('attributes'))
    def update_doi(self):
        outcome = None
        try:
            outcome = self.validate()
        except Exception as e:
            outcome = True
        if outcome:
            print('Validation error. Check with the `validate()` method.')
            return None
        for i in self.identifiers:
            self.get_meta()
            version = self.meta[0].get('version')
            if version:
                version = version.split('.')
                version[1] = int(version[1]) + 1
                version = '.'.join([str(i) for i in version])
            else:
                version = '1.1'
            payload = {
                'data': {
                    'type': 'dois',
                    'attributes': self.data,
                    'action': 'update',
                    'version': version
            }}
            try:
                modifier = requests.put(f'https://api.test.datacite.org/dois/{i.get("identifier")}',
                            headers = {'Content-Type': 'application/vnd.api+json'},
                            auth = (self.client.get('username'), self.client.get('password')),
                            json = payload)
                if modifier.status_code != 200:
                    raise requests.RequestException(f'Failed to modify DOI: {modifier.text}')
                else:
                    self.meta = modifier.json()
            except Exception as e:
                print(e)
    def mint_doi(self):
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
        payload['attributes']['event'] = "publish"
        payload['attributes']['prefix'] = self.client.get('prefix')
        payload['attributes']['url'] = f'https://data.neotomadb.org/datasets/{self.datasetid}'
        payload['attributes']['version'] = '1.0'
        try:
            created = requests.post(f'https://api.test.datacite.org/dois',
                                headers = {'Content-Type': 'application/vnd.api+json'},
                                auth = (self.client.get('username'), self.client.get('password')),
                                json = {'data': payload})
            if created.status_code != 201:
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