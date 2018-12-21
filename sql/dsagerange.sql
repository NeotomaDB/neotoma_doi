select smallage.ageboundyounger, 
       smallage.ageboundolder, 
       agetypes.agetype 
FROM ndb.agetypes INNER JOIN
         (SELECT ageboundyounger, 
         	     ageboundolder, agetypeid FROM ndb.chronologies INNER JOIN
         (SELECT collectionunitid as cuid FROM ndb.datasets where datasetid = ?ds_id) as ds
         ON ds.cuid = chronologies.collectionunitid WHERE chronologies.isdefault = 1) as smallage
         ON smallage.agetypeid = agetypes.agetypeid