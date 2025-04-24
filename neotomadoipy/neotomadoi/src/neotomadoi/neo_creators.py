import psycopg2
import psycopg2.extras

def neo_creators(con:psycopg2.connect, self)->list:
    """_Obtain a list of Neotoma dataset PIs for a dataset._

    Args:
        con (psycopg2.connect): _description_

    Returns:
        list: _A list of dataset PIs, including any external identifiers._
    """    

    query = """
        SELECT DISTINCT cts.contactname AS name,
                        -- cts.address AS affiliation,
                        jsonb_agg(DISTINCT 
                                jsonb_build_object('nameIdentifier', exct.identifier,
                                                   'nameIdentifierScheme', exdb.extdatabasename, 
                                                   'schemeUri', exdb.url)) AS "nameIdentifiers"
        FROM ndb.datasetpis AS dspi
        INNER JOIN ndb.contacts AS cts ON cts.contactid = dspi.contactid
        LEFT JOIN ndb.externalcontacts AS exct ON exct.contactid = cts.contactid
        LEFT JOIN ndb.externaldatabases AS exdb ON exdb.extdatabaseid = exct.extdatabaseid
        WHERE dspi.datasetid = %(datasetid)s
        GROUP BY cts.contactid;
    """

    with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(query, {'datasetid': self.datasetid})
        response = cur.fetchall()
        creators = []
        if len(response) == 0:
            creators = [{'name': 'None listed'}]
        for i in response:
            creator = dict(i)
            if creator.get('name') is None:
                creator['name'] = 'None listed'
            if not all([i.get('nameIdentifier') for i in creator.get('nameIdentifiers')]):
                out = creator.pop('nameIdentifiers', None)
            creators.append(creator)
    return creators
