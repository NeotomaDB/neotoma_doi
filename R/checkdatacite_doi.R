#!/usr/bin/Rscript

library(rdatacite, quietly = TRUE)
library(RPostgreSQL, quietly = TRUE)
library(stringr, quietly = TRUE)
library(jsonlite, quietly = TRUE)
suppressMessages(library(dplyr, quietly = TRUE))

con_string <- fromJSON("./connect_remote.json")

con <- dbConnect(PostgreSQL(),
                 host = con_string$host,
                 port = con_string$port,
                 user = con_string$user,
                 password = con_string$password,
                 dbname = con_string$database)

if (RPostgreSQL::dbExistsTable(con, 'ndb.datasetdoi')) {
  # Make the datasetdoi table.  This isn't in the Postgres DB
  # migration, so may need to be added de novo.
  create <- "CREATE TABLE ndb.datasetdoi (
    datasetid integer REFERENCES ndb.datasets(datasetid),
    doi character varying,
    recdatecreated timestamp,
    recdatemodified timestamp
    CONSTRAINT good_doi CHECK (doi ~* '^10.\\d{4,9}/[-._;()/:A-Z0-9]+$')
  );
  "

  result <- try(dbExecute(con, create))
  if (! ("try-error" %in% class(result))) {
    print("Created doi dataset table.")
  }
}

existing_dois <- dbGetQuery(con, "SELECT * FROM ndb.datasetdoi")

check <- FALSE
doi_set <- list()
i <- 1
rows <- 500

# Check datacite for any Neotoma records.  We're paging through the DataCite
# records, with 500 records per page.

source('R/datacite_dois.R')

neotoma_dois <- datacite_dois()

cat(sprintf("Found a total of %d records\n", nrow(neotoma_dois)))

neotoma_dois <- neotoma_dois %>%
  filter(!(dataset %in% existing_dois$datasetid & doi %in% existing_dois$doi))

if (nrow(neotoma_dois) > 0) {
  upload <- data.frame(datasetid = neotoma_dois$dataset,
                       doi = neotoma_dois$doi,
                       recdatecreated = neotoma_dois$uploaded,
                       recdatemodified = Sys.time())

  dbWriteTable(con,
    c("ndb", "datasetdoi"),
    upload,
    row.names = FALSE, append = TRUE)
  cat("Added ", nrow(upload), " DOIs to Neotoma.\n")
} else {
  cat("No datasets to add.\n")
}
