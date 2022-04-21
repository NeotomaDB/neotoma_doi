#' @title Fetch all records from a query
#' @description Wraps the send and fetch elements of a SQL query from R.
fetchall <- function(con, query, n = 100) {

  result <- dbSendQuery(con, query)

  output <- list()

  while (!dbHasCompleted(result)) {
    rows <- length(output) + 1
    output[[rows]] <- fetch(result, n = 100)
  }

  output <- output %>% bind_rows()

  return(output)
}