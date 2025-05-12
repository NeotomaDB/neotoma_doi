import pytest
from neotomadoi import neotomaDOI

DATASETID = 16

def test_meta():
    # Putting in a junk identifier, should raise an exception.
    new_doi = neotomaDOI(datasetid = DATASETID, defaults = 'neotomadoi.yaml')
    new_doi.update()
    new_doi.identifiers = {'identifier': '10/e8sa-w766', 'identifierType': 'DOI'}
    with pytest.raises(Exception):
        new_doi.get_meta()