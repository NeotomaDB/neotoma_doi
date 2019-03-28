#!/usr/bin/Rscript

library(RPostgreSQL, quietly = TRUE)
library(stringr)
library(jsonlite)
suppressMessages(library(dplyr))

con_string <- fromJSON("connect_remote.json")

con <- dbConnect(PostgreSQL(),
                 host = con_string$host,
                 port = con_string$port,
                 user = con_string$user,
                 password = con_string$password,
                 dbname = con_string$database)

if (RPostgreSQL::dbExistsTable(con, "doi.frozen")) {
   create <- "CREATE TABLE IF NOT EXISTS
                       doi.frozen(datasetid integer CONSTRAINT goodds CHECK (doi.inds(datasetid)),
                       download jsonb NOT null,
                       recdatecreated TIMESTAMP DEFAULT NOW(),
                       recmodified TIMESTAMP DEFAULT NOW());
              GRANT SELECT, INSERT ON doi.frozen TO doiwriter;"

   result <- try(dbExecute(con, create))
   if (! ("try-error" %in% class(result))) {
     print("Created frozen table.")
   }

}

# All datasets that have been created and submitted more than
# one week ago, without any frozen entry.
datalength <- "
  SELECT COUNT(DISTINCT ds.datasetid)
	FROM ndb.datasets as ds
	LEFT OUTER JOIN ndb.datasetdoi AS dsdoi ON  ds.datasetid = dsdoi.datasetid
	JOIN    ndb.datasetsubmissions AS dss   ON dss.datasetid = ds.datasetid

  WHERE (ds.datasetid) NOT IN (SELECT datasetid FROM doi.frozen) AND
      	ds.recdatecreated < NOW() - INTERVAL '1 week' AND
		    dss.submissiondate < NOW() - INTERVAL '1 week' AND
        ds.datasettypeid > 1
"

howmany <- dbGetQuery(con, datalength) %>%
  unlist() %>%
  as.numeric()

cat(sprintf("There are %d datasets that need to be frozen.\n", howmany))

# Might be slow.  Generates the "frozen" records for the datasets.

run_freeze <- dbExecute(con, readr::read_file("sql/generatingFrozen.sql"))

# Now with "frozen" records and the list of datasets without
# DOIs we can then generate the neccessary DOIs.
