#!/usr/bin/Rscript

suppressMessages(library(RPostgreSQL, quietly = TRUE))
suppressMessages(library(stringr))
suppressMessages(library(jsonlite))
suppressMessages(library(dplyr))

con_string <- fromJSON("connect_remote.json")

con <- dbConnect(PostgreSQL(),
                 host = con_string$host,
                 port = con_string$port,
                 user = con_string$user,
                 password = con_string$password,
                 dbname = con_string$database)

# Does the "Frozen" table exist in the current Database:

if (!RPostgreSQL::dbExistsTable(con, c("doi","frozen"))) {
   create <- "CREATE TABLE IF NOT EXISTS
                       doi.frozen(datasetid integer CONSTRAINT goodds CHECK (doi.inds(datasetid)),
                       download jsonb NOT null,
                       recdatecreated TIMESTAMP DEFAULT NOW(),
                       recmodified TIMESTAMP DEFAULT NOW());
              GRANT SELECT, INSERT ON doi.frozen TO doiwriter;"

   result <- try(dbExecute(con, create))
   if (! ("try-error" %in% class(result))) {
     print("Created frozen table.")
   } else {
     stop("Could not create the table for freezing records.")
   }

}

# All datasets that have been created and submitted more than
# one week ago, without any frozen entry.

datalength <- "
  SELECT DISTINCT ds.datasetid
	FROM ndb.datasets as ds
	LEFT OUTER JOIN ndb.datasetdoi AS dsdoi ON  ds.datasetid = dsdoi.datasetid
	JOIN    ndb.datasetsubmissions AS dss   ON dss.datasetid = ds.datasetid
  WHERE (ds.datasetid) NOT IN (SELECT datasetid FROM doi.frozen) AND
      	ds.recdatecreated < NOW() - INTERVAL '1 week' AND
		    dss.submissiondate < NOW() - INTERVAL '1 week' AND
        ds.datasettypeid > 1
"

source('R/fetchall.R')

howmany <- fetchall(con, datalength) %>%
  unlist() %>%
  length() %>%
  as.numeric()

cat(sprintf("There are %d datasets that need to be frozen.\n", howmany))

# Might be slow.  Generates the "frozen" records for the datasets.
if (howmany > 0) {
  run_freeze <- dbExecute(con, readr::read_file("sql/generatingFrozen.sql"))
  howmany_after <- dbGetQuery(con, datalength) %>%
    unlist() %>%
    length() %>%
    as.numeric()

  cat(sprintf("There are %d datasets that could not be frozen:\n",
              howmany_after))

  if (howmany_after > 0) {
    cat("Adding unfrozen dataset IDs to the log file at `freeze.log`.\n")
    unfrozen <- dbGetQuery(con, datalength) %>%
      unlist()  %>%
      paste0(collapse = ",") %>%
      paste0(Sys.time(), ", [", ., "]")

    readr::write_lines(unfrozen,
      path="freeze.log",
      append = TRUE)
  }

}

# Now with "frozen" records and the list of datasets without
# DOIs we can then generate the neccessary DOIs.

RPostgreSQL::dbDisconnect(con)
