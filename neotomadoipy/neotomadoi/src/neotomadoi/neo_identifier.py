import psycopg2
import psycopg2.extras

def neo_identifier(con:psycopg2.connect, datasetid:int)->object:

    query = """
        SELECT doi as identifier,
        'DOI' as identifierType
        FROM doi.doimeta
        WHERE datasetid = %(datasetid)s
        LIMIT 1;
    """

    with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(query, {'datasetid': datasetid})
        response = cur.fetchone()
        doi = dict(response)
    return doi
