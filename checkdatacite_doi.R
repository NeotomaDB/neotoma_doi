#!/usr/bin/Rscript

library(rdatacite)
library(RPostgreSQL)
library(stringr)
library(jsonlite)
library(dplyr)

con_string <- fromJSON("connect_remote.json")

con <- dbConnect(PostgreSQL(),
                 host = con_string$host,
                 port = con_string$port,
                 user = con_string$user,
                 password = con_string$password,
                 dbname = con_string$database)

rows <- 500

isDoiThere <- dbGetQuery(con, "SELECT COUNT(*) FROM ndb.datasetdoi")

if (is.null(isDoiThere)) {
  create <- "CREATE TABLE ndb.datasetdoi (
    datasetid integer REFERENCES ndb.datasets(datasetid),
    doi character varying,
    recdatecreated timestamp,
    recdatemodified timestamp
    CONSTRAINT good_doi CHECK (doi ~* '^10.\\d{4,9}/[-._;()/:A-Z0-9]+$')
  )"
  dbExecute(con, create)
}

existing_dois <- dbGetQuery(con, "SELECT * FROM ndb.datasetdoi")

check <- FALSE
doi_set <- list()
i <- 1

while (check == FALSE) {
  doi_set[[i]] <- dc_search(q = "publisher:[Neotoma]",
                            fl = c("doi", "title",
                                   "relatedIdentifier", "uploaded"),
                            rows = rows,
                            start = (i - 1) * rows)
  if (nrow(doi_set[[i]]) == rows) {
    i <- i + 1
  } else {
    check <- TRUE
  }
}

neotoma_dois <- do.call(rbind.data.frame, doi_set) %>% unique()

neotoma_dois$dataset <- str_match(neotoma_dois$relatedIdentifier,
  "downloads/([0-9]*)")[, 2]  %>%
  as.numeric()

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
