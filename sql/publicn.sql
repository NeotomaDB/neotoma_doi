SELECT *
  FROM ndb.publications INNER JOIN
  (SELECT publicationid 
  	FROM ndb.datasetpublications WHERE datasetid = ?ds_id) as dpub 
  ON publications.publicationid = dpub.publicationid