import psycopg2
import psycopg2.extras
import pyalex
from pyalex import Works, config
import json

config.max_retries = 0
config.retry_backoff_factor = 0.1
config.retry_http_codes = [429, 500, 503]
config.email = "goring@wisc.edu"

def neo_subjects(con:psycopg2.connect, self)->object:
    pubs = []
    topics = []
    subjects = []
    pub_query = """
        SELECT DISTINCT TRIM(pub.doi) as doi
        FROM ndb.datasetpublications AS dsp
        INNER JOIN ndb.publications AS pub ON dsp.publicationid = pub.publicationid
        WHERE dsp.datasetid = %(datasetid)s
        AND pub.doi IS NOT NULL;"""
    with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(pub_query, {'datasetid': self.datasetid})
        response = cur.fetchall()
        for i in response:
            pubs.append(dict(i))
    if len(pubs) > 0:
        for i in pubs:
            try:
                open_record = Works()['https://doi.org/' + i.get('doi')]
                topics = [j for j in open_record.get('topics') if j.get('score') > 0.5]
                topics.append(open_record.get('primary_topic'))
                subjects = [{'subjectScheme': 'OpenAlex Topic',
                            'schemeUri': 'https://openalex.org',
                            'subject': top.get('display_name'),
                            'valueUri': top.get('id')} for top in topics]
            except Exception as e:
                print(e)
    if self.defaults:
        subjects = subjects + self.defaults['subjects']
    subjects = [json.loads(i) for i in set([json.dumps(i) for i in subjects])]
    return subjects
