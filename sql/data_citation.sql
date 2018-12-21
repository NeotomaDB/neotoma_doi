SELECT 
  CONCAT(sitename, ' ', datasettype, ' dataset') AS sitename,
                                         'Title' AS titleType, 
                                     contactname AS creatorName, 
                                         'ORCID' AS nameidentifierscheme, 
                              'http://orcid.org' AS schemeuri, 
                                         address AS affiliation, 
            EXTRACT(YEAR FROM ds.recdatecreated) AS publicationyear
FROM
           (SELECT * FROM ndb.datasets WHERE datasetid = ?ds_id) AS ds   LEFT JOIN
           ndb.datasetPIs  ON         ds.datasetid = datasetpis.datasetid LEFT JOIN
             ndb.contacts  ON datasetpis.contactid = contacts.contactid   INNER JOIN
ndb.collectionunits AS cu  ON  ds.collectionunitid = cu.collectionunitid  INNER JOIN
          ndb.sites AS sts ON            cu.siteid = sts.siteid           INNER JOIN
   ndb.datasettypes AS dst ON     ds.datasettypeid = dst.datasettypeid