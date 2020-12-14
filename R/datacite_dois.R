#' @title Get Neotoma DOIs from DataCite
#' @description Uses the DataCite API to call for Neotoma Datasets
#' @returns data.frame
datacite_dois <- function() {

  naNull <- function(x) { ifelse(is.null(x), NA, x) }

  check <- FALSE
  doi_set <- list()
  i <- 1

  # Keep running through the returned DataCite DOIs using the R package.
  # The API may actually have a better solution to this in `fromdraft`.
  # Drops out of the while loop when less than the total number of rows
  # are returned.

  finished <- TRUE
  first <- TRUE

  while(finished) {

    if(first) {
      result <- httr::GET('https://api.datacite.org/dois',
                          query=list(query='publisher:Neotoma*',
                                     'page[cursor]' = 1))

      newLink <- content(result)$links$`next`
      oldLink <- ''
      first <- FALSE

    } else {

        if(!newLink == oldLink) {

          oldLink <- newLink
          result <- httr::GET(newLink)

        } else {
          finished <- FALSE
        }
    }

    inserter <- content(result)
    newLink <- inserter$links$`next`

    if (is.null(newLink)) {
      finished <- TRUE
    }

    i <- i + 1
    doi_set[[(length(doi_set) + 1)]] <- inserter$data

    cat(i, 'of', inserter$meta$totalPages, '\n')

  }

  neotoma_dois <- doi_set %>%
    unlist(recursive = FALSE) %>%
    map(function(x) {

      id <- naNull(x$id)
      title <- naNull(x$attributes$titles[[1]]$title)
      created <- naNull(x$attributes$created)
      related <- naNull(x$attributes$relatedIdentifiers[[1]]$relatedIdentifier)

      data.frame(doi = id,
                 title = title,
                 relatedIdentifier = related,
                 uploaded = created)
    }) %>%
    bind_rows() %>%
    unique() %>%
    mutate(dataset = stringr::str_match(relatedIdentifier, "(downloads/)(\\d*)")[,3])

  return(neotoma_dois)
}
