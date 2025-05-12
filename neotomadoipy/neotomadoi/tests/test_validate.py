from neotomadoi import neotomaDOI
from pytest import raises, fail
from jsonschema.exceptions import ValidationError

DATASETID = 16

def test_schema_validate():
    new_doi = neotomaDOI(datasetid = DATASETID, defaults = 'neotomadoi.yaml')
    with raises(ValidationError, match = "There is an issue"):
        new_doi.validate() 
    try:
        new_doi.update()
    except Exception:
        fail(f"Unexpected validation error with dataset {DATASETID}")
    new_doi.data['descriptions'][0]['lang'] = 50
    with raises(ValidationError, match = "There is an issue"):
        new_doi.validate()

def test_duplicate_dois():
    # When we have a dataset with a DOI already, that DOI shouldn't show up in the related identifiers.
    dsid = 1
    new_doi = neotomaDOI(datasetid = dsid, defaults = 'neotomadoi.yaml')
    new_doi.update()
    new_doi.validate()
    identifiers = [i.get('relatedIdentifier') for i in new_doi.data.get('relatedIdentifiers')]
    assert new_doi.identifiers.get('identifier') not in identifiers

def test_crap_dois():
    # We expect this one to fail because currently there is no polygon/spatial data associated with it.
    dsid = 4662
    new_doi = neotomaDOI(datasetid = dsid, defaults = 'neotomadoi.yaml')
    with raises(ValueError, match = 'missing critical'):
        new_doi.update()
