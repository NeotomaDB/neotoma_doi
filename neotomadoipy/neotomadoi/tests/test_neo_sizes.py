from neotomadoi import neotomaDOI, neo_connect, neo_size
from dotenv import load_dotenv
from pytest import raises


def test_size():
    DATASETID = 10443
    load_dotenv()

    con = neo_connect()
    new_doi = neotomaDOI(datasetid = DATASETID, defaults = 'neotomadoi.yaml')
    aa = neo_size(con, new_doi)
    assert isinstance(aa, list)
    new_doi = neotomaDOI(datasetid = 700000, defaults = 'neotomadoi.yaml')
    with raises(Exception, match = "no frozen version"):
        neo_size(con, new_doi)
