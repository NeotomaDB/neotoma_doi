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

source("R/assign_doi.R")

missingdoi <- "SELECT fr.datasetid
               FROM          doi.frozen AS fr
               LEFT JOIN ndb.datasetdoi AS dsdoi ON dsdoi.datasetid = fr.datasetid
               WHERE doi IS NULL"

dsids <-  dbGetQuery(con, missingdoi)

for(i in unlist(dsids)) {
  assign_doi(i, con, post = TRUE, dbpost = FALSE, sandbox = TRUE)
  if((which(i == dsids) %% 79) == 0) {
    cat("\n.")
  } else {
    cat (".")
  }
}

RPostgreSQL::dbDisconnect(con)
