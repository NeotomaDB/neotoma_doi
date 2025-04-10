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

class neotomaDOI:
    def __init__(self, datasetid:int, defaults: str = None):
        if defaults:
            with open(defaults, 'r') as file:
                self.defaults = yaml.safe_load(file)
        else:
            self.defaults = {}
        self.datasetid = datasetid
        self.data = {
            "identifiers": [{'identifier': "1", 'identifierType':"DOI"}],
            "creators": None,
            "titles": None,
            "publisher": self.defaults.get("publisher"),
            "publicationYear": str(datetime.now().year),
            "types": self.defaults.get("types"),
            "schemaVersion": self.defaults.get("schemaVersion"),
            "language": self.defaults.get("language"),
            "rightsList": self.defaults.get("rightsList")
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
            raise ValueError('No schema has been defined. Use neotomaDOI.add_scheme()')
    def update(self):
        if self.datasetid:
            con = neo_connect()
            self.data['creators'] = neo_creators(con, self.datasetid)
            self.data['contributors'] = neo_contributors(con, self.datasetid)
            self.data['titles'] = [neo_title(con, self.datasetid)]
            self.data['subjects'] = neo_subjects(con, self)
            self.data['geoLocations'] = neo_location(con, self)
            self.data['identifier'] = neo_identifer(con, self)
