import pytest
from neotomadoi import neotomaDOI
from datetime import datetime
from psycopg2.extensions import connection

DATASETID = 16

def test_schema_validate():
    new_doi = neotomaDOI(datasetid = DATASETID, defaults = 'neotomadoi.yaml')
    with pytest.raises(Exception, match = "Failed validating 'type' in schema"):
        new_doi.validate() 
    try:
        new_doi.update()
    except Exception:
        pytest.fail(f"Unexpected validation error with dataset {DATASETID}")
    new_doi.data['descriptions'][0]['lang'] = 50
    with pytest.raises(Exception, match = "Failed validating 'type' in schema"):
        new_doi.validate()
