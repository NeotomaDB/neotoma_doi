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
    assert isinstance(new_doi.identifiers, dict)
    assert new_doi.identifiers.get('identifierType') == 'DOI'
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
    new_doi.get_meta()
    old_version = new_doi.meta.get('version')
    if not old_version:
        old_version = '1.0'
    else:
        old_version = old_version.split('.')
        old_version[1] = int(old_version[1]) + 1
        old_version = '.'.join([str(i) for i in old_version])
    new_doi.mint_doi()
    assert new_doi.meta.get('version') == old_version
    new_doi.data['titles'] = [{'title': 'This new phone.'}]
    assert new_doi.data.get('titles')[0] == {'title': 'This new phone.'}
    new_version = '1.1'
    new_doi.mint_doi()
    new_doi.get_meta()
    assert new_doi.meta.get('version') == new_version
    assert new_doi.meta.get('titles') == [{'title': 'This new phone.'}]
    assert new_doi
    
def test_draft_doi():
    new_doi = neotomaDOI(datasetid = DATASETID, defaults = 'neotomadoi.yaml')
    new_doi.update()
    new_doi.identifiers = None
    load_dotenv()
    DCITE = loads(getenv('DCITE'))
    new_doi.set_user(cred = credentials(DCITE))
    new_doi.test_mode()
    new_doi.mint_doi(publish = False)
    assert new_doi.identifiers
    assert new_doi.meta.get('isActive') is False
    new_doi.meta = None
    new_doi.get_meta()
    assert new_doi.meta.get('isActive') is False
    