import psycopg2
import psycopg2.extras
from sys import getsizeof
from json import dumps

def neo_size(con:psycopg2.connect, self)->object:

    query = """
        SELECT download
        FROM doi.frozen
        WHERE datasetid = %(datasetid)s;
    """

    with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(query, {'datasetid': self.datasetid})
        response = cur.fetchone()
        download = getsizeof(dumps(response))
        size = [f'{round(download/1000)} kB']
    return size
