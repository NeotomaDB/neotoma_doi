import psycopg2
import psycopg2.extras

def neo_creators(con:psycopg2.connect, datasetid:int)->object:

    query = """
        SELECT DISTINCT cts.contactname AS name,
                        -- cts.address AS affiliation,
                        jsonb_agg(DISTINCT 
                                jsonb_build_object('nameIdentifier', exct.identifier,
                                                   'nameIdentifierScheme', exdb.extdatabasename, 
                                                   'schemeUri', exdb.url)) AS nameIdentifiers
        FROM ndb.datasetpis AS dspi
        INNER JOIN ndb.contacts AS cts ON cts.contactid = dspi.contactid
        LEFT JOIN ndb.externalcontacts AS exct ON exct.contactid = cts.contactid
        LEFT JOIN ndb.externaldatabases AS exdb ON exdb.extdatabaseid = exct.extdatabaseid
        WHERE dspi.datasetid = %(datasetid)s
        GROUP BY cts.contactid;
    """

    with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(query, {'datasetid': datasetid})
        response = cur.fetchall()
        creators = []
        for i in response:
            creator = dict(i)
            creators.append(creator)
    return creators
