import neotomadoi
import dotenv
import os
import json
import psycopg2
import psycopg2.extras

dotenv.load_dotenv()

DCITE = json.loads(os.getenv('DCITE'))

datacite_meta = neotomadoi.credentials(DCITE)

con = neotomadoi.neo_connect()

query = """SELECT ds.datasetid
           FROM ndb.datasets AS ds
           LEFT JOIN doi.doimeta AS dom ON dom.datasetid = ds.datasetid
           WHERE dom.datasetid IS NULL
           AND NOT ds.datasettypeid = 1;"""

with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
    cur.execute(query)
    datasetids = cur.fetchall()
    datasetids = [i[0] for i in datasetids]

dotenv.load_dotenv()

DCITE = json.loads(os.getenv('DCITE'))

datacite_meta = neotomadoi.credentials(DCITE)

for i in datasetids:
    print(f'Working on {i}')
    new_doi = neotomadoi.neotomaDOI(datasetid = i, defaults = 'neotomadoi.yaml')
    new_doi.set_user(datacite_meta)
    new_doi.test_mode()
    try:
        new_doi.update()
        new_doi.validate()
        new_doi.mint_doi()
        with open('minting_dois.log', 'a', encoding='UTF-8') as f:
            json.dump({'datasetid': i,
                        'doi': new_doi.identifiers,
                        'meta': new_doi.meta}, f)
            a = f.write('\n')
        print(f'  Minted new DOI: {new_doi.identifiers.get('identifier')}')
    except Exception as e:
        print('Whoops.')
        print(e)
        with open('testing_dois.log', 'a', encoding='UTF-8') as f:
            json.dump({'datasetid': i,
                        'error': str(e)}, f)
            a = f.write('\n')

# Removing Datasets from the DOI public set:
query = """SELECT doi.* FROM doi.doimeta AS doi
           LEFT join ndb.datasets AS ds ON ds.datasetid = doi.datasetid
           WHERE ds.datasetid IS NULL;"""

