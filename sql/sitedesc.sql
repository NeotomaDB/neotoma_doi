SELECT sitedescription FROM ndb.sites
INNER JOIN (SELECT *
         FROM ndb.collectionunits
         INNER JOIN (SELECT collectionunitid as cuid FROM ndb.datasets where datasetid = ?ds_id) as ds
         ON ds.cuid = collectionunits.collectionunitid) as cu
         ON cu.siteid = sites.siteid