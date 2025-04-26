import pytest
from neotomadoi import neotomaDOI, testMode, credentials
from random import choices
from string import digits, ascii_lowercase
from dotenv import load_dotenv
from json import loads
from os import getenv

DATASETID = 16

def test_user_cred():
    DCITE = {"user": ''.join(choices(ascii_lowercase + digits, k=6)),
             "mode": {"test": {"handle": ''.join(choices(ascii_lowercase + digits, k=6)),
                               "pw": ''.join(choices(ascii_lowercase + digits, k=6))},
                      "prod": {"handle": ''.join(choices(ascii_lowercase + digits, k=6)),
                               "pw": ''.join(choices(ascii_lowercase + digits, k=6))}}}
    user_cred = credentials(DCITE)
    assert isinstance(user_cred, credentials)
    with pytest.raises(Exception):
        credentials({})
    assert isinstance(user_cred.mode(testMode.test), dict)
    assert isinstance(user_cred.mode(testMode.prod), dict)
    assert all([i in ['username', 'pw', 'handle'] for i in user_cred.mode(testMode.prod)])
    assert all([i in ['username', 'pw', 'handle'] for i in user_cred.mode(testMode.test)])

def test_assign_creds():
    new_doi = neotomaDOI(datasetid = DATASETID, defaults = 'neotomadoi.yaml')
    DCITE = {"user": ''.join(choices(ascii_lowercase + digits, k=6)),
             "mode": {"test": {"handle": ''.join(choices(ascii_lowercase + digits, k=6)),
                               "pw": ''.join(choices(ascii_lowercase + digits, k=6))},
                      "prod": {"handle": ''.join(choices(ascii_lowercase + digits, k=6)),
                               "pw": ''.join(choices(ascii_lowercase + digits, k=6))}}}
    user_cred = credentials(DCITE)
    with pytest.raises(Exception):
        new_doi.set_user(cred = DCITE)
    new_doi.set_user(cred = user_cred)
    assert new_doi.mode.name == 'test'
    assert new_doi.mode.value == 'https://api.test.datacite.org/dois/'
    assert isinstance(new_doi.client, credentials)
    assert new_doi.client.data == DCITE

def test_change_mode():
    new_doi = neotomaDOI(datasetid = DATASETID, defaults = 'neotomadoi.yaml')
    with pytest.raises(Exception) as e_info:
        new_doi.prod_mode()
    DCITE = {"user": ''.join(choices(ascii_lowercase + digits, k=6)),
             "mode": {"test": {"handle": ''.join(choices(ascii_lowercase + digits, k=6)),
                               "pw": ''.join(choices(ascii_lowercase + digits, k=6))},
                      "prod": {"handle": ''.join(choices(ascii_lowercase + digits, k=6)),
                               "pw": ''.join(choices(ascii_lowercase + digits, k=6))}}}
    user_cred = credentials(DCITE)
    new_doi.set_user(user_cred)
    assert new_doi.mode.name == 'test'
    new_doi.prod_mode()
    assert new_doi.mode.name == 'prod'
    new_doi.test_mode()
    assert new_doi.mode.name == 'test'
