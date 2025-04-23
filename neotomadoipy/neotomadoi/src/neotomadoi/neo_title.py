import psycopg2
import psycopg2.extras

def neo_title(con:psycopg2.connect, self)->object:
    query = """
        SELECT st.sitename || ' ' || dst.datasettype || ' dataset' AS title
        FROM
        ndb.datasets AS ds
        INNER JOIN ndb.datasettypes AS dst ON dst.datasettypeid = ds.datasettypeid
        INNER JOIN ndb.collectionunits AS cu ON cu.collectionunitid = ds.collectionunitid
        INNER JOIN ndb.sites AS st ON st.siteid = cu.siteid
        WHERE ds.datasetid = %(datasetid)s; 
    """
    with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(query, {'datasetid': self.datasetid})
        response = cur.fetchone()
        title = {'title': response[0]}
    return title
