import neotomadoi
import dotenv
import os
import json
import psycopg2
import psycopg2.extras

new_doi = neotomadoi.neotomaDOI(datasetid = 16, defaults = 'neotomadoi.yaml')
new_doi.update()
#new_doi.validate('../data/datacite_schema.json')
new_doi.validate()

dotenv.load_dotenv()

DCITE = json.loads(os.getenv('DCITE'))

datacite_meta = {"username": DCITE.get('user'),
                 "password": DCITE.get('test').get('pw'),
                 "prefix":  DCITE.get('test').get('handle'),
                 "test_mode": True}

new_doi.set_user(datacite_meta)
# new_doi.identifiers = None
# new_doi.mint_doi()

con = neotomadoi.neo_connect()

query = """SELECT doi.* FROM doi.doimeta AS doi
           inner join ndb.datasets AS ds ON ds.datasetid = doi.datasetid;"""

with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
    cur.execute(query)
    datasetids = cur.fetchall()

for i in datasetids:
    print(f'Working on {i[2]}, DOI: {i[0]}')
    new_doi = neotomadoi.neotomaDOI(datasetid = i[2], defaults = 'neotomadoi.yaml')
    new_doi.set_user(datacite_meta)
    try:
        new_doi.update()
        new_doi.validate()
        print(f'✔ Works for {i[2]}, DOI: {i[0]}')
    except ValueError as e:
        print('Whoops.')
        print(e)
        break

# Removing Datasets from the DOI public set:
query = """SELECT doi.* FROM doi.doimeta AS doi
           LEFT join ndb.datasets AS ds ON ds.datasetid = doi.datasetid
           WHERE ds.datasetid IS NULL;"""

