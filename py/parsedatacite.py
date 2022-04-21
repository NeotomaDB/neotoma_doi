"""_summary_
date: March 23, 2022
by: Simon Goring
Clean Neotoma DOI Records.
As the datacite metadata schema changes, or Neotoma properties change, it may
be useful to update Neotoma DOI metadata on DataCite.
This function calls data from Neotoma and then updates metadata to ensure that
the datacite metadata reflects the current best-practices and most up-to-date
Neotoma metadata.

Returns:
    _type_: _description_
"""

import json
import copy
import re
import requests
import psycopg2
from psycopg2.extras import execute_values
import re
from datacite import DataCiteMDSClient, schema42, schema40

with open('connect_remote.json') as f:
    data = json.load(f)

conn = psycopg2.connect(**data, connect_timeout=5)
cur = conn.cursor()

## The file `buildDOImeta.py` can be used to pull all stored DataCite metadata into
## Neotoma.  We will use Postgres queries on the doi.doimeta table to pull records we 
## want to fix.  We use Postgres JSON operators here.

## This query is intended to pull all records where there are potential errors in the
## structure of the DataCite metadata:

query = """
    WITH doiset AS (
        SELECT dm.doi, dm.meta, (jsonb_array_elements(dm.meta->'contributors') ? 'contributorType') AS missingCont
        FROM doi.doimeta AS dm
        WHERE dm.meta->>'url' ILIKE '%data-dev.neotomadb%' 
           OR  dm.meta->'creators' ? 'contributorType'
           OR dm.meta-> 'relatedIdentifiers' ->> 'relatedIdentifier' ILIKE '%-dev.neotoma%')
    SELECT DISTINCT dm.doi, dm.meta
    FROM doi.doimeta AS dm
    INNER JOIN doiset AS ds ON ds.doi = dm.doi       
"""

records = cur.execute(query)
brokendois = [rec for rec in cur]

def changeAff(x):
    x['affiliation']=['']
    if 'contributorType' not in x.keys():
        x['contributorType'] = 'Researcher'
    if 'nameType' not in x.keys():
        x['nameType'] = 'Organizational'
    z = {k: y for k, y in x.items() if len(y) > 0}
    return z


def noneorempty(x):
    if x is None:
        return False
    elif type(x) is list:
        if len(x) == 0:
            return False
        else:
            return True
    else:
        return True


def cleanEmpty(obj):
    if type(obj) is dict:
        outobj = copy.deepcopy(obj)
        z = {k: y for k, y in outobj.items() if not noneorempty(y)}
        for k in z.items():
            if type(k) is dict:
                k = cleanEmpty(k)
        return z
    else:
        return(obj)


counter = 0

for i in brokendois:
    out = copy.deepcopy(i[1])
    # Replace references to the dev servers:
    hasUrl = re.match('.*data-dev.*', out['url'])
    if hasUrl:
        out['url'] = out['url'].replace('-dev','')
    out['url'] = out['url'].replace('http:', 'https:')
    # We often seem to be missing the `identifiers` key:
    out['identifiers'] = [{"identifierType": "DOI", "identifier": out['doi']}]
    # The published key has been replaced by publicationYear:
    if 'published' in out.keys():
        if out['published'] == None:
            out['publicationYear'] = out['dates'][0]['date']
        else:    
            out['publicationYear'] = out['published']
        out.pop('published')
    else:
        out['publicationYear'] = out['dates'][0]['date']
    # Want to fix up the affiliations:
    out['contributors'] = list(map(lambda x: changeAff(x), out['contributors'])) 
    out['creators'] = list(map(lambda x: changeAff(x), out['creators']))
    # A sneaky way to remove duplicate objects:
    out['creators'] = list(map(lambda x: json.loads(x), set(map(lambda x: json.dumps(x), out['creators']))))
    out['contributors'] = list(map(lambda x: json.loads(x), set(map(lambda x: json.dumps(x), out['contributors']))))
    # Want to make sure that the `schemaVersion` is recorded:
    out['schemaVersion'] = "http://datacite.org/schema/kernel-4"
    # Sometimes there's not the documentation?  Might be the place to add the publications.
    out['relatedIdentifiers'] = list(filter(lambda x: 'relatedIdentifier' in x.keys(), out['relatedIdentifiers']))
    for j in out['relatedIdentifiers']:
        j['relatedIdentifier'] = j['relatedIdentifier'].replace('-dev', '')
    assert schema42.validate(out)
    # Now push up to datacite:
    url = "https://api.datacite.org/dois/" + out['doi']
    object = {"data": {
            "attributes": out
            }}
    headers = {
        "Content-Type": "application/vnd.api+json",
        "Authorization": "Basic V0lTQy5ORU9UT01BOjFrWGttdE8yclM1ZQ=="
    }
    response = requests.request("PUT", url, json = object, headers = headers)
    if response.status_code == 200:
        contenttest = json.loads(response.content)['data']
        meta = [(contenttest['id'], 
                json.dumps(contenttest['attributes']),
                int(re.search(r'\d+', contenttest['attributes']['url']).group(0)))]
        print('Adding record:')
        execute_values(cur,
            """INSERT INTO doi.doimeta (doi, meta, datasetid) 
               VALUES %s
               ON CONFLICT (doi) DO 
               UPDATE 
               SET meta = EXCLUDED.meta, datasetid = EXCLUDED.datasetid;""", meta)
        conn.commit()
        responseurl = contenttest['attributes']['url']
        print('Success for dataset %s; doi:%s' % (out['url'], out['doi']))
        if responseurl != out['url']:
            break
    else:
        print('Error for dataset %s; doi:%s' % (out['url'], out['doi']))
        print(response.content)
        with open('doierrors.log', 'a') as f:
            close = f.write(json.dumps(x) + '\n')
    counter = counter + 1
    if counter % 300 == 0:
        print('Updating %d of %s DOIs' % (counter, len(brokendois)), end = '\r')
