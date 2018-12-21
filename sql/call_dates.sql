SELECT 
             ds.datasetid, 
       ds.recdatemodified AS dataset, 
     dspi.recdatemodified AS dspi, 
 contacts.recdatemodified AS contact, 
       cu.recdatemodified AS collunit, 
      sts.recdatemodified AS sites,
      dst.recdatemodified AS datatype, 
      dss.recdatemodified AS ds_sub, 
      dsp.recdatemodified AS datapub, 
      chr.recdatemodified AS chron 
FROM 
           ndb.datasets AS ds  LEFT JOIN 
         ndb.datasetpis AS dspi ON        ds.datasetid = dspi.datasetid LEFT JOIN
           ndb.contacts         ON       dspi.contactid = contacts.contactid INNER JOIN 
    ndb.collectionunits AS cu   ON  ds.collectionunitid = cu.collectionunitid INNER JOIN
              ndb.sites AS sts  ON            cu.siteid = sts.siteid INNER JOIN
       ndb.datasettypes AS dst  ON     ds.datasettypeid = dst.datasettypeid INNER JOIN 
 ndb.datasetsubmissions AS dss  ON        dss.datasetid = ds.datasetid LEFT JOIN 
ndb.datasetpublications AS dsp  ON        dsp.datasetid = ds.datasetid LEFT JOIN 
       ndb.chronologies AS chr  ON chr.collectionunitid = cu.collectionunitid
WHERE ds.datasetid = ?ds_id