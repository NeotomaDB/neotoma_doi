from neotomadoi import neotomaDOI, activity

DATASETID = 16

def test_activity():
    new_doi = neotomaDOI(datasetid = DATASETID, defaults = 'neotomadoi.yaml')
    new_doi.update()
    assert len(new_doi.activity) > 0
    assert isinstance(new_doi.activity, activity)
