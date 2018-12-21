INSERT INTO doi.frozen (datasetid, doi, record, recdatecreated)
WITH ds AS (
	SELECT ds.datasetid
	FROM ndb.datasets as ds
	LEFT OUTER JOIN ndb.datasetdoi as dsdoi ON ds.datasetid = dsdoi.datasetid
	WHERE (ds.datasetid, dsdoi.doi) NOT IN (SELECT datasetid, doi FROM doi.frozen)
)
SELECT df.datasetid,
        dsdoi.doi,
		df.frozendata AS record,
		current_timestamp AS recdatecreated
FROM doi.doifreeze((SELECT array_agg(datasetid) FROM ds)) as df
LEFT OUTER JOIN ndb.datasetdoi as dsdoi ON dsdoi.datasetid = df.datasetid
