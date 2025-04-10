"""
A commandline script to perform several actions to sync Neotoma and DataCite records.
Date: April 21, 2022
by: Simon Goring

1. Refresh the datacite metadata within Neotoma with all records on DataCite
    to ensure that the data is similar on both platforms.
2. Repair DataCite data where Neotoma metadata may have been updated.
3. Mint a single new Neotoma DOI
4. Bulk update Neotoma records older than a certain age.
"""

import json
import os
import psycopg2
import argparse
import copy
import re
import sys

parser = argparse.ArgumentParser(
    description='Check Neotoma DOI records within DataCite against ' +
                'records stored within Neotoma.')

parser.add_argument('-fetch', dest='getDS', default=False,
                    help='Fetch all DataCite records and update Neotoma database.',
                    nargs = '+')

parser.add_argument('-o', dest='isDS', default=False,
                    help='Mint a new DOI for one or more dataset IDs (listed)',
                    nargs = '+')

parser.add_argument('-m', dest='isAll', default=False,
                    help='Mint DOIs for all records older than 1 week.')

args = parser.parse_args()

with open('connect_remote.json') as f:
    data = json.load(f)
    data.pop('test')

conn = psycopg2.connect(**data, connect_timeout=5)
cur = conn.cursor()

if args.isDS:
    t = list(map(lambda x: x.split(',') ,args.isDS))
    datasets = list(set([int(item) for sublist in t for item in sublist]))
    print('Minting for datasets ' + str(datasets))

if args.isAll:
    query = '''
    SELECT DISTINCT ds.datasetid
	FROM ndb.datasets as ds
	  LEFT OUTER JOIN       ndb.datasetdoi AS dsdoi ON  ds.datasetid = dsdoi.datasetid
	  INNER JOIN    ndb.datasetsubmissions AS dss   ON dss.datasetid = ds.datasetid
    WHERE ds.datasetid NOT IN (SELECT datasetid FROM doi.frozen) AND
      	  ds.recdatecreated < NOW() - INTERVAL '2 days' AND
		  dss.submissiondate < NOW() - INTERVAL '2 days' AND
          ds.datasettypeid > 1;
    '''
    records = cur.execute(query)
    datasets = list(set([res[0] for res in cur]))
    
