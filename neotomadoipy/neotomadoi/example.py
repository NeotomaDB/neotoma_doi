import neotomadoi
from dotenv import load_dotenv
import os
import json
import psycopg2
import psycopg2.extras

load_dotenv()

DCITE = json.loads(os.getenv('DCITE'))

datacite_meta = neotomadoi.credentials(DCITE)

con = neotomadoi.neo_connect(test = False)

# All datasets that are between two months and two days old.
# Datasets cannot be geochronologic datasets.
query = """SELECT DISTINCT ds.datasetid
           FROM ndb.datasets AS ds
           LEFT JOIN ndb.datasetdoi AS dsdoi ON dsdoi.datasetid = ds.datasetid
           WHERE NOT ds.datasettypeid = 1;"""

with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
    cur.execute(query)
    datasetids = cur.fetchall()
    datasetids = [i[0] for i in datasetids]

for i in datasetids:
    print(f'Working on {i}')
    new_doi = neotomadoi.neotomaDOI(datasetid = i, defaults = 'neotomadoi.yaml')
    new_doi.set_user(datacite_meta)
    new_doi.prod_mode()
    try:
        try:
            new_doi.update()
        except ValueError as e:
            if 'critical' in str(e):
                new_doi.freeze_data(con)
                new_doi.update()
        new_doi.validate()
        new_doi.get_activity()
        old_activity = len(new_doi.activity)  
        new_doi.mint_doi(publish = True)
        if old_activity == 0:
            with open('minting_dois.log', 'a', encoding='UTF-8') as f:
                new_doi.get_meta()
                json.dump({'datasetid': i,
                            'doi': new_doi.identifiers,
                            'meta': new_doi.meta}, f)
                a = f.write('\n')
            print(f'  Minted new DOI: {new_doi.identifiers.get('identifier')}')
        elif old_activity > 0:
            with open('updating_dois.log', 'a', encoding='UTF-8') as f:
                new_doi.get_meta()
                json.dump({'datasetid': i,
                            'doi': new_doi.identifiers,
                            'meta': new_doi.meta}, f)
                a = f.write('\n')
            print(f'  Updated DOI: {new_doi.identifiers.get('identifier')}')
    except Exception as e:
        print('Whoops.')
        print(e)
        with open('failing_dois.log', 'a', encoding='UTF-8') as f:
            json.dump({'datasetid': i,
                        'error': str(e)}, f)
            a = f.write('\n')

