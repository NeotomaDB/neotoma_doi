SELECT CONCAT(sitename, ' ', datasettype, ' dataset') as dataset, 
       datasettype, datasetid 
FROM ndb.datasettypes
INNER JOIN (SELECT sitename, datasetid, datasettypeid from ndb.sites
         INNER JOIN
         (SELECT datasetid, jssi.collectionunitid, siteid, datasettypeid FROM ndb.datasets
         INNER JOIN (SELECT * FROM ndb.collectionunits
         WHERE collectionunits.siteid = 
         (SELECT siteid FROM ndb.collectionunits
         INNER JOIN (SELECT collectionunits.collectionunitid 
         FROM ndb.collectionunits
         INNER JOIN (SELECT * FROM ndb.datasets where datasetid = ?ds_id) as ds
         ON ds.collectionunitid = collectionunits.collectionunitid) as clu
         ON clu.collectionunitid = collectionunits.collectionunitid)) as jssi
         ON jssi.collectionunitid = datasets.collectionunitid) AS bigjoin
         ON sites.siteid = bigjoin.siteid) AS sitedstype
         ON datasettypes.datasettypeid = sitedstype.datasettypeid