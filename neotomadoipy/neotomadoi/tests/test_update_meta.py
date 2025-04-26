from neotomadoi import neotomaDOI

DATASETID = 16

def test_update_meta():
    new_doi = neotomaDOI(datasetid = DATASETID, defaults = 'neotomadoi.yaml')
    assert new_doi.data.get('creators') is None
    new_doi.update()
    assert isinstance(new_doi.data.get('creators'), list)
    assert isinstance(new_doi.identifiers, dict)
