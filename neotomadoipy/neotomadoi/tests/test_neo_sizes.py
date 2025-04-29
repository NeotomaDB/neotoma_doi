from neotomadoi import neotomaDOI, neo_connect, credentials, neo_size
from dotenv import load_dotenv
import os
from json import loads
from os import getenv

DATASETID = 10443

def test_size():

    load_dotenv()

    DCITE = loads(getenv('DCITE'))
    datacite_meta = credentials(DCITE)

    con = neo_connect()
    new_doi = neotomaDOI(datasetid = DATASETID, defaults = 'neotomadoi.yaml')
    aa = neo_size(con, new_doi)