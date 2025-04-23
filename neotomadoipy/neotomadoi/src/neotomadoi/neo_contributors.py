import psycopg2
import psycopg2.extras

def neo_contributors(con:psycopg2.connect, self)->object:
    query = """
        WITH chronfolk AS (
        SELECT DISTINCT  contactid,
                'Researcher'::text AS contributorType
        FROM     ndb.datasets AS d
        JOIN ndb.chronologies AS chron ON d.collectionunitid = chron.collectionunitid
        WHERE d.datasetid = %(datasetid)s
        ),
        collfolk AS (
        SELECT DISTINCT  contactid, 'DataCollector'::text AS contributortype
        FROM     ndb.datasets AS d
        JOIN   ndb.collectors AS coll ON d.collectionunitid = coll.collectionunitid
        WHERE d.datasetid = %(datasetid)s
        ),
        dpi AS (
        SELECT DISTINCT  contactid,
                'ProjectLeader'::text AS contributortype
        FROM ndb.datasetpis WHERE datasetpis.datasetid = %(datasetid)s
        ),
        curator AS (
        /* In the DB stuff this should be a 'DataSteward' */
        SELECT DISTINCT  contactid, 'DataCurator'::text AS contributortype
        FROM ndb.datasetsubmissions
        WHERE datasetsubmissions.datasetid = %(datasetid)s
        ),
        coauth AS (
        SELECT DISTINCT contactid,
                'Researcher'::text AS contributortype
        FROM ndb.datasetpublications AS d
        JOIN ndb.publicationauthors AS paut ON d.publicationid = paut.publicationid
        WHERE d.datasetid = %(datasetid)s
        ),
        analyst AS (
            SELECT DISTINCT sana.contactid,
        /* In the DB stuff this should be a 'DataAnalyst' */
                    'DataCollector'::text AS contributortype
        FROM        ndb.samples AS samp
        JOIN ndb.sampleanalysts AS sana ON samp.sampleid = sana.sampleid
        WHERE samp.datasetid = %(datasetid)s
        )
        SELECT DISTINCT cts.contactname AS name,
                        -- cts.address AS affiliation,
                        lister.contributortype as "contributorType",
                        jsonb_agg(DISTINCT 
                                jsonb_build_object('nameIdentifier', exct.identifier,
                                                   'nameIdentifierScheme', exdb.extdatabasename, 
                                                   'schemeUri', exdb.url)) AS "nameIdentifiers"
        FROM (SELECT * FROM analyst
        UNION ALL
        (SELECT * FROM coauth)
        UNION ALL
        (SELECT * FROM curator)
        UNION ALL
        (SELECT * FROM dpi)
        UNION ALL
        (SELECT * FROM collfolk)
        UNION ALL
        (SELECT * FROM chronfolk)) AS lister
        JOIN ndb.contacts AS cts ON cts.contactid = lister.contactid
        LEFT JOIN ndb.externalcontacts AS exct ON exct.contactid = cts.contactid
        LEFT JOIN ndb.externaldatabases AS exdb ON exdb.extdatabaseid = exct.extdatabaseid
        GROUP BY cts.contactid, lister.contributortype;
    """
    with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(query, {'datasetid': self.datasetid})
        response = cur.fetchall()
        contributors = []
        for i in response:
            creator = dict(i)
            if not all([i.get('nameIdentifier') for i in creator.get('nameIdentifiers')]):
                out = creator.pop('nameIdentifiers', None)
            contributors.append(creator)
    return contributors
