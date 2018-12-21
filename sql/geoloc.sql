Select CONCAT(latitudesouth, ' ', 
                        longitudewest, ' ',
                        latitudenorth, ' ', longitudeeast)
  FROM ndb.sites
  INNER JOIN
  (SELECT siteid
  FROM ndb.collectionunits
  INNER JOIN
  (SELECT datasets.collectionunitid FROM ndb.datasets WHERE datasetid = ?ds_id) as ds
  ON collectionunits.collectionunitid = ds.collectionunitid) as scd 
  ON sites.siteid = scd.siteid