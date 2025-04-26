import pytest
from neotomadoi import neotomaDOI, credentials
from dotenv import load_dotenv
from json import loads
from os import getenv

DATASETID = 16

def test_mint_test_doi():
    new_doi = neotomaDOI(datasetid = DATASETID, defaults = 'neotomadoi.yaml')
    new_doi.update()
    new_doi.identifiers = None
    load_dotenv()
    DCITE = loads(getenv('DCITE'))
    new_doi.set_user(cred = credentials(DCITE))
    new_doi.test_mode()
    new_doi.mint_doi()
    assert isinstance(new_doi.identifiers, list)
    assert new_doi.identifiers[0].get('identifierType') == 'DOI'
    try:
        new_doi.meta = []
        new_doi.get_meta()
    except Exception:
        pytest.fail(f"Cannot recover the minted DOI for dataset {DATASETID}")
    
def test_update_doi():
    new_doi = neotomaDOI(datasetid = DATASETID, defaults = 'neotomadoi.yaml')
    new_doi.update()
    new_doi.identifiers = None
    load_dotenv()
    DCITE = loads(getenv('DCITE'))
    new_doi.set_user(cred = credentials(DCITE))
    new_doi.test_mode()
    new_doi.mint_doi()
    new_doi.data['titles'] = [{'title': 'This new phone.'}]