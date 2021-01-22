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
source('R/fetchall.R')

missingdoi <- "SELECT fr.datasetid AS datasetid
               FROM          doi.frozen AS fr
               LEFT JOIN ndb.datasetdoi AS dsdoi ON dsdoi.datasetid = fr.datasetid
               LEFT JOIN ndb.datasets AS ds ON ds.datasetid = fr.datasetid
               LEFT JOIN ndb.datasettypes AS dst ON dst.datasettypeid = ds.datasettypeid
               WHERE doi IS NULL
                 AND NOT dst.datasettype = 'geochronologic'"

dsid_test <-  fetchall(con, missingdoi) %>% unlist()

for(i in dsid_test) {
  output <- try(assign_doi(ds_id = i, con = con, 
                           post = TRUE, dbpost = TRUE, 
                           sandbox = FALSE))

  if ("try-error" %in% class(output)) {
    doids <- paste0(Sys.time(), ", ",
                         i, ", ",
                          TRUE, ", ",
                        FALSE, ", ",
                       TRUE, ",",
                       as.character(attr(output, "condition")))

    readr::write_lines(doids,
      file = "minting.log",
      append = TRUE)

  } else {
    cat(paste0(which(dsid_test == i)," of ", length(dsid_test), ": ",
               i, "; doi: ", output[[2]][1], "\n"))
  }

}

RPostgreSQL::dbDisconnect(con)
