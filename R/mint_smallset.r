library(purrr)
library(dplyr)
library(RPostgreSQL, quietly = TRUE)
library(stringr)
library(jsonlite)

con_string <- fromJSON("connect_remote.json")

con <- dbConnect(PostgreSQL(),
                 host = con_string$host,
                 port = con_string$port,
                 user = con_string$user,
                 password = con_string$password,
                 dbname = con_string$database)

ds <- fromJSON('https://api.neotomadb.org/v2.0/data/sites/28174/datasets',
               flatten = FALSE, simplifyDataFrame = FALSE)[[2]]

freezequery <= "SELECT doi.doifreeze(ARRAY[52309,52310,52312,52313,52315,52316,52318,52319,52321,52322,52324,52325,52327,52328,52330,52331,52333,52334,52336,52337,52339,52340,52342,52343,52345,52346,52348,52349,52351,52352,52354,52355,52357,52358,52360,52361,52363,52364,52366,52367,52369,52370,52372,52373,52375,52376,52378,52379,52381,52382,52384,52385,52387,52388,52390,52391,52393,52394,52396,52397,52399,52400]);"

ds_table <- purrr::map(ds, function(x) {
    temptable <- purrr::map(x$site$datasets, function(y) {
      data.frame(datasetid = y$datasetid,
                 datasettype = y$datasettype,
                 doi = paste0(y$doi, collapse = ","))
    }) %>% bind_rows()
    temptable <- temptable %>%
        mutate(collectionunit = x$site$collectionunit,
               sitename = x$site$sitename) %>%
        select(sitename, collectionunit, datasetid, datasettype, doi)
    return(temptable)
}) %>%
bind_rows() %>%
filter(!datasettype == 'geochronologic')

out <- map(ds_table[,1], function(x) {
    assign_doi(ds_id = x,  con = con, post = TRUE, dbpost = TRUE, 
                           sandbox = FALSE)
})
