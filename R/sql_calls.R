# SQL queries:

geoloc_call <- function(x) {
  paste0("Select CONCAT(LatitudeSouth, ' ',
                        LongitudeWest, ' ',
                        LatitudeNorth, ' ', LongitudeEast)
  FROM NDB.Sites
  INNER JOIN
  (SELECT SiteID
  FROM NDB.CollectionUnits
  INNER JOIN
  (SELECT datasets.CollectionUnitID FROM NDB.Datasets WHERE DatasetID = ", x, ") as ds
  ON collectionunits.CollectionUnitID = ds.CollectionUnitID) as scd
  ON sites.SiteID = scd.SiteID")
}

doi_call <- function(x) {
  paste0("SELECT DOI
  FROM NDB.Publications
  INNER JOIN (SELECT publicationID FROM NDB.DatasetPublications WHERE datasetID = ", x, ") as dpub
  ON publications.publicationID = dpub.publicationID")
}

pub_call <- function(x) {
  paste0("SELECT *
         FROM NDB.Publications
         INNER JOIN (SELECT publicationID FROM NDB.DatasetPublications WHERE datasetID = ", x, ") as dpub
         ON publications.publicationID = dpub.publicationID")
}

constdb_call <- function(x) {
  paste0("Select DatabaseName
FROM NDB.ConstituentDatabases
         INNER JOIN (SELECT DatabaseID FROM NDB.DatasetDatabases WHERE DatasetID = ", x, ") as dsdb
         ON dsdb.DatabaseID = constituentdatabases.DatabaseID")
}

sharedSite_call <- function(x) {
  paste0("SELECT CONCAT(SiteName, ' ', DatasetType, ' dataset') as Dataset, DatasetType, DatasetID FROM NDB.DatasetTypes
INNER JOIN (SELECT SiteName, DatasetID, DatasetTypeID from NDB.Sites
         INNER JOIN
         (SELECT DatasetID, jssi.CollectionUnitID, SiteID, DatasetTypeID FROM NDB.Datasets
         INNER JOIN (SELECT * FROM NDB.CollectionUnits
         WHERE collectionunits.SiteID =
         (SELECT SiteID FROM NDB.CollectionUnits
         INNER JOIN (SELECT collectionunits.CollectionUnitID
         FROM NDB.CollectionUnits
         INNER JOIN (SELECT * FROM NDB.Datasets where DatasetID = ", x, ") as ds
         ON ds.CollectionUnitID = collectionunits.CollectionUnitID) as clu
         ON clu.CollectionUnitID = collectionunits.CollectionUnitID)) as jssi
         ON jssi.CollectionUnitID = datasets.CollectionUnitID) AS bigjoin
         ON sites.SiteID = bigjoin.SiteID) AS SiteDSType
         ON datasettypes.DatasetTypeID = SiteDSType.DatasetTypeID")
}

sitedesc_call <- function(x) {
  paste0("")
}

agerange_call <- function(x){
  paste0("select smallage.AgeBoundYounger, smallage.AgeBoundOlder, agetypes.AgeType FROM NDB.AgeTypes
INNER JOIN
         (SELECT AgeBoundYounger, AgeBoundOlder, AgeTypeID FROM NDB.Chronologies
         INNER JOIN (SELECT CollectionUnitID as cuid FROM NDB.Datasets where DatasetID = ", x, ") as ds
         ON ds.cuid = chronologies.CollectionUnitID WHERE chronologies.IsDefault = 1) as smallage
         ON smallage.AgeTypeID = agetypes.AgeTypeID")
}
