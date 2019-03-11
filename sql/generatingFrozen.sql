INSERT INTO doi.frozen (datasetid, download, recdatecreated)
WITH ds AS (
	SELECT DISTINCT ds.datasetid
	FROM ndb.datasets as ds
	LEFT OUTER JOIN ndb.datasetdoi as dsdoi ON ds.datasetid = dsdoi.datasetid
	JOIN ndb.datasetsubmissions AS dss ON dss.datasetid = ds.datasetid
	WHERE (ds.datasetid) NOT IN (SELECT datasetid FROM doi.frozen) AND
      	ds.recdatecreated < NOW() - INTERVAL '1 week' AND
		    dss.submissiondate < NOW() - INTERVAL '1 week'
)
SELECT df.datasetid,
		df.download AS download,
		current_timestamp AS recdatecreated
FROM doi.doifreeze((SELECT array_agg(datasetid) FROM ds)) as df;
