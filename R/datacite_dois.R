datacite_dois <- function() {
  check <- FALSE
  while (check == FALSE) {
    doi_set[[i]] <- try(rdatacite::dc_search(q = "publisher:[Neotoma]",
                              fl = c("doi", "title",
                                     "relatedIdentifier", "uploaded"),
                              rows = rows,
                              start = (i - 1) * rows))

    if ("try-error" %in% class(doi_set[[i]])) {
      stop("Could not connect to DataCite.")
    }

    if (nrow(doi_set[[i]]) == rows) {
      i <- i + 1
    } else {
      check <- TRUE
    }
  }
  neotoma_dois <- do.call(rbind.data.frame, doi_set) %>%
    unique() %>%
    mutate(dataset = stringr::str_match(relatedIdentifier, "(downloads/)(\\d*)")[,3])

  return(neotoma_dois)
}
