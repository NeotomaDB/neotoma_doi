import pytest
from neotomadoi import neotomaDOI, neo_connect, testMode, credentials
from datetime import datetime
from psycopg2.extensions import connection

DATASETID = 16

def test_init_empty():
    new_doi = neotomaDOI(datasetid = DATASETID)
    assert all([i in ['creators', 'titles', 'publisher', 'publicationYear', 'types', 'schemaVersion', 'language', 'rightsList', 'formats'] for i in new_doi.data.keys()])
    assert new_doi.datasetid == DATASETID
    assert new_doi.data.get('publicationYear') == str(datetime.now().year)
    assert new_doi.mode == testMode.test

def test_init_defaults():
    new_doi = neotomaDOI(datasetid = DATASETID, defaults = 'neotomadoi.yaml')
    assert all([i in ['creators', 'titles', 'publisher', 'publicationYear', 'types', 'schemaVersion', 'language', 'rightsList', 'formats'] for i in new_doi.data.keys()])
    assert new_doi.datasetid == DATASETID
    assert isinstance(new_doi.data.get('types'), dict)
    assert new_doi.mode == testMode.test

def test_conn():
    con = neo_connect()
    assert isinstance(con, connection)
    assert con.status == 1
    assert con.closed == 0
    con.close()
    assert con.closed == 1
