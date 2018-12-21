WITH creation AS (
  SELECT MIN(ds.submissiondate)::date, 'Submitted'::text
  FROM ndb.datasetsubmissions AS ds
  WHERE ds.datasetid = $1
),
resub AS (
  SELECT ds.submissiondate, 'Updated'::text
  FROM ndb.datasetsubmissions AS ds
  WHERE ds.datasetid = $1
  ORDER BY ds.submissiondate
  OFFSET 1
)
SELECT *
FROM (
	(SELECT * FROM creation)
  UNION ALL
  (SELECT * FROM resub)) AS dates
