import neotomadoi
import dotenv
import os
import json
import psycopg2
import psycopg2.extras

dotenv.load_dotenv()

DCITE = json.loads(os.getenv('DCITE'))

datacite_meta = neotomadoi.credentials(DCITE)

new_doi = neotomadoi.neotomaDOI(datasetid = 16, defaults = 'neotomadoi.yaml')
new_doi.set_user(datacite_meta)

new_doi.update()
new_doi.validate()

con = neotomadoi.neo_connect()

query = """SELECT ds.datasetid
           FROM ndb.datasets AS ds
           LEFT JOIN doi.doimeta AS dom ON dom.datasetid = ds.datasetid
           WHERE dom.datasetid IS NULL
           AND NOT ds.datatypeid = 1;"""

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

