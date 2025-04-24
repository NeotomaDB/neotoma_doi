import psycopg2
import psycopg2.extras

def neo_dates(con:psycopg2.connect, self)->object:

    query = """
        WITH creation AS (
            SELECT MIN(ds.submissiondate)::date as date, 'Submitted'::text
            FROM ndb.datasetsubmissions AS ds
            WHERE ds.datasetid = %(datasetid)s
        ),
        resub AS (
            SELECT ds.submissiondate as date, 'Updated'::text
            FROM ndb.datasetsubmissions AS ds
            WHERE ds.datasetid = %(datasetid)s
            ORDER BY ds.submissiondate
            OFFSET 1
        )
        SELECT DISTINCT *
        FROM (
            (SELECT * FROM creation)
        UNION ALL
        (SELECT * FROM resub)) AS dates
        WHERE date is not NULL;
    """

    with con.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(query, {'datasetid': self.datasetid})
        response = cur.fetchall()
        dates = []
        for i in response:
            dates.append(dict(i))
        date_out = []
        for i in dates:
            date_out.append({"dateType": i.get('text'), "date": i.get('date').strftime('%Y-%m-%d')})
    return date_out
