import psycopg2
import psycopg2.extras

def neo_relatedIdentifiers(con:psycopg2.connect, self)->object:
    
    relatedIdentifiers = []

    ds_query = """
        SELECT doi as identifier,
        'DOI' as identifierType
        FROM doi.doimeta
        WHERE datasetid = %(datasetid)s
        LIMIT 1;
    """

    with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(ds_query, {'datasetid': self.datasetid})
        response = cur.fetchone()
        doi = dict(response)

    pub_query = """
        SELECT DISTINCT pub.doi as doi
        FROM ndb.datasetpublications AS dsp
        INNER JOIN ndb.publications AS pub ON dsp.publicationid = pub.publicationid
        WHERE dsp.datasetid = %(datasetid)s
        AND pub.doi IS NOT NULL;"""
    
    with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(pub_query, {'datasetid': self.datasetid})
        response = cur.fetchone()
        if response:
            pubdoi = dict(response)
            for i in pubdoi:
                relatedIdentifiers.append({'relatedIdentifierType': 'DOI',
                                        'relationType': 'IsSupplementTo',
                                        #'relatedItemType': 'JournalArticle',
                                        'relatedIdentifier': pubdoi['doi']})

    geochron_query = """
        SELECT DISTINCT egc.identifier as identifier,
               edb.extdatabasename as name
        FROM ndb.datasets AS ds
        inner join ndb.collectionunits as cu on ds.collectionunitid = cu.collectionunitid
        inner join ndb.chronologies as ch on ch.collectionunitid = cu.collectionunitid
        inner join ndb.chroncontrols as cc on cc.chronologyid = ch.chronologyid
        inner join ndb.geochroncontrols as gcc on gcc.chroncontrolid = cc.chroncontrolid
        inner join ndb.externalgeochronology as egc on egc.geochronid = gcc.geochronid
        inner join ndb.externaldatabases as edb on edb.extdatabaseid = egc.extdatabaseid
        WHERE ds.datasetid = %(datasetid)s AND edb.extdatabasename = 'ARK';"""

    with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(geochron_query, {'datasetid': self.datasetid})
        response = cur.fetchall()
        if response:
            gc_ark = [dict(i) for i in response]
            for i in gc_ark:
                relatedIdentifiers.append({'relatedIdentifierType': 'ARK',
                                        'relationType': 'HasMetadata',
                                        #'relatedItemType': 'Dataset',
                                        'relatedIdentifier': i['identifier']})

    return relatedIdentifiers
