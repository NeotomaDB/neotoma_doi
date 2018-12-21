SELECT databasename 
FROM ndb.constituentdatabases
         INNER JOIN (SELECT databaseid FROM ndb.datasetdatabases WHERE datasetid = ?ds_id) as dsdb 
         ON dsdb.databaseid = constituentdatabases.databaseid