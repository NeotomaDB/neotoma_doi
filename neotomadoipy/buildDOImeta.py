"""_summary_
Push DOI metadata to the Neotoma Database Server (`neotoma`)
by: Simon Goring
date: 2022/03/16
This script is intended to connect to the Neotoma database, and to be run infrequently.
It simply pulls the DOI metadata and then pushes it into the database.  It will determine
which DOIs have been created, and what metadata DataCite has for the records.
"""
import json
import requests
import psycopg2
from psycopg2.extras import execute_values
import re

call = "https://api.datacite.org/dois"

doimeta = requests.get(call, params = {"query":"publisher:Neotoma*", 
                                  "page[cursor]": 1})

nextlink = ''
page = 1

with open('connect_remote.json') as f:
    data = json.load(f)

conn = psycopg2.connect(**data, connect_timeout=5)
cur = conn.cursor()

if doimeta.status_code == 200:
    pages = json.loads(doimeta.content)['meta']['totalPages']
    while 1:
        print("Getting page %d of %d." % (page, pages))
        content = json.loads(doimeta.content)
        results = content['data']
        meta = list(map(lambda x: (x['id'], json.dumps(x['attributes']), int(re.search(r'\d+', x['attributes']['url']).group(0))), results))
        execute_values(cur,
            """INSERT INTO doi.doimeta (doi, meta, datasetid) 
               VALUES %s
               ON CONFLICT (doi) DO 
               UPDATE 
               SET meta = EXCLUDED.meta, datasetid = EXCLUDED.datasetid;""", meta)
        conn.commit()
        if 'next' not in content['links'].keys():
            break
        else:
            if content['links']['next'] == nextlink:
                break
            else:
                page = page + 1
                nextlink = content['links']['next']
                doimeta = requests.get(nextlink)
