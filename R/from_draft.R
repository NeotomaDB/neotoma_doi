
library(dplyr, quietly = TRUE, verbose = FALSE)
library(RPostgreSQL, quietly = TRUE, verbose = FALSE)
library(httr, quietly = TRUE, verbose = FALSE)
library(XML, quietly = TRUE, verbose = FALSE)
library(jsonlite, quietly = TRUE, verbose = FALSE)

con_string <- fromJSON("connect_remote.json")

con <- dbConnect(PostgreSQL(),
                 host = con_string$host,
                 port = con_string$port,
                 user = con_string$user,
                 password = con_string$password,
                 dbname = con_string$database)

dc_pw <- jsonlite::fromJSON("datacite_auth.txt")

password <- dc_pw$prod$pw

url <- "https://api.datacite.org/dois?client-id=wisc.neotoma&page[size]=1000"

while(1 == 1) {
  aa <- httr::GET(url = url,
                 config = httr::authenticate(user = dc_pw$user,
                                             password = password))

  bb <- content(aa)

  if(exists('records')) {
    records <- append(records, bb$data)
  } else {
    records <- bb$data
  }

  if (url == bb$links$`next`) {
    stop()
  } else {
    url <- bb$links$`next`
  }

}

for(i in length(records):1) {
  if(records[[i]]$attributes$state == "findable") {
    records[[i]] <- NULL
  }
}

aa  <- data.frame(dlloc = rep(NA, length(records)),
                  doi =  rep(NA, length(records)))

for(i in 1:length(records)) {
  aa$dlloc[i] <- records[[i]]$attributes$relatedIdentifiers[[1]]$relatedIdentifier
  aa$doi[i] <- records[[i]]$attributes$doi[1]
}

aa$dsid <- stringr::str_extract(aa$dlloc, "\\d{1,10}$")

for(i in 1:length(records)) {

  doibody <- paste0("url=http://data-dev.neotomadb.org/", aa$dsid[i], "\ndoi=", aa$doi[i])

  publish <- httr::PUT(url=paste0("https://mds.datacite.org/doi/", aa$doi[i]),
                       config = httr::authenticate(user = dc_pw$user,
                                               password = dc_pw$prod$pw),
                       content_type('text/plain;charset=UTF-8'),
                       body=doibody,
                       encoding="raw")

  if(http_status(publish)$category == "Success") {

    insertQuery <- "INSERT INTO ndb.datasetdoi (datasetid, doi, recdatecreated)
                    VALUES ($1, $2, NOW()::timestamp)
                    RETURNING datasetid"
    rs <- try(dbSendQuery(con, insertQuery, c(aa$dsid[i], aa$doi[i])))
    if(!"try-error" %in% class(rs)) {
      rs_out <- dbFetch(rs)
      dbClearResult(rs)
    }
  }
  cat(i, ": doi:", aa$doi[i], " for dataset: ", aa$dsid[i], "\n")
}
