#!/usr/bin/Rscript

suppressMessages(library(rdatacite, quietly = TRUE))
suppressMessages(library(RPostgreSQL, quietly = TRUE))
suppressMessages(library(stringr, quietly = TRUE))
suppressMessages(library(jsonlite, quietly = TRUE))
suppressMessages(library(dplyr, quietly = TRUE))
suppressMessages(library(purrr, quietly = TRUE))
suppressMessages(library(httr, quietly = TRUE))

con_string <- fromJSON("./connect_remote.json")

con <- dbConnect(PostgreSQL(),
                 host = con_string$host,
                 port = con_string$port,
                 user = con_string$user,
                 password = con_string$password,
                 dbname = con_string$database)

# Make the datasetdoi table in the current connected Database.
# This isn't in the Postgres DB migration, so may need to be added de novo.
if (!RPostgreSQL::dbExistsTable(con, c('ndb','datasetdoi'))) {

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
    message("Created the ndb.doidataset table.")
  } else {
    stop("Failed to create the ndb.doidataset table.")
  }
}

fetchall <- function(con, query) {
  
  result <- dbSendQuery(con, query)
  
  output <- list()
  
  while (!dbHasCompleted(result)) {
    rows <- length(output) + 1
    output[[rows]] <- fetch(result, n = 100)  
  }
  
  output <- output %>% bind_rows()
  
  return(output)
}

existing_dois <- fetchall(con, "SELECT * FROM ndb.datasetdoi")
existing_dtst <- fetchall(con, "SELECT * FROM ndb.datasets")

# Check datacite for any Neotoma records.  We're paging through the DataCite
# records, with 500 records per page.

cat("Checking existing datasets from DataCite")
source('R/datacite_dois.R')

neotoma_dois <- datacite_dois()

cat(sprintf("Found a total of %d records\n", nrow(neotoma_dois)))

# The record is not in the existing Neotoma ndb.datasetdoi table:
missing_dois <- neotoma_dois %>%
  filter(!(dataset %in% existing_dois$datasetid &
           doi %in% existing_dois$doi))

# Are there any datasets with DOIs in DataCite returned that aren't in
# the existing list of Neotoma DOIs?

if (nrow(missing_dois) > 0) {
  unarchived <- data.frame(datasetid = neotoma_dois$dataset,
                       doi = neotoma_dois$doi)

  missingds <- unarchived %>%
    filter(!datasetid %in% existing_dtst$datasetid)

  if(nrow(missingds) > 0) {
    warning("There are a number of records for DOIs without associated dataset IDs.  These have been written to file.")
    readr::write_csv(missingds, file = paste0("missingdatasets", Sys.Date(), ".csv"))
  }
  
  upload <- unarchived %>%
    filter(!datasetid %in% existing_dois$datasetid) %>% 
    filter(datasetid %in% existing_dtst$datasetid)
  
  if(nrow(upload) > 0) {
    cat(sprintf("There are %d records that have not been archived in Neotoma.\n", nrow(upload)))
    
    dbWriteTable(con,
      name = c("ndb", "datasetdoi"),
      value = upload,
      row.names = FALSE, append = TRUE)
  
    cat("Added ", nrow(upload), " DOIs to Neotoma.\n")
  } else {
    cat("No datasets to add.\n")
  }
} else {
  cat("No datasets to add.\n")
}

RPostgreSQL::dbDisconnect(con)
