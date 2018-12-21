assign_doi <- function(ds_id, post = FALSE) {

  doi_sens <- readr::read_lines('doi_sens.txt')

  library(dplyr, quietly = TRUE, verbose = FALSE)
  library(RPostgreSQL, quietly = TRUE, verbose = FALSE)
  library(httr, quietly = TRUE, verbose = FALSE)
  library(XML, quietly = TRUE, verbose = FALSE)
  library(jsonlite, quietly = TRUE, verbose = FALSE)

  con <- dbConnect(drv = "PostgreSQL",
                  host = doi_sens[1],
                  port = doi_sens[2],
                dbname = doi_sens[3],
                  user = doi_sens[4],
              password = doi_sens[5])

  frozen <- fromJSON(paste0('http://api-dev.neotomadb.org/v2.0/data/download/',
                            ds_id), simplifyVector = FALSE)$data[[1]]
  assertthat::are_equal(frozen$datasetid, ds_id)

  contact <- fromJSON(paste0('http://api-dev.neotomadb.org/v2.0/data/datasets/',
                             ds_id, '/contacts'),
                      simplifyVector = FALSE)$data[[1]]$contact

  schema <- XML::xmlSchemaParse("data//metadata.xsd")

  # Generating the new XML framework and associated namespaces:
  doc <- XML::newXMLDoc()

  root <- XML::newXMLNode("resource",
                          namespaceDefinitions = c("http://datacite.org/schema/kernel-4",
                                                   "xsi" = "http://www.w3.org/2001/XMLSchema-instance"),
                          attrs = c("xsi:schemaLocation" = "http://datacite.org/schema/kernel-4 http://schema.datacite.org/meta/kernel-4/metadata.xsd"),
                          doc = doc)

  # This is the empty shoulder for assigning DOIs:
  XML::newXMLNode("identifier", "10.21233/N3",
                  attrs = c("identifierType" = "DOI"),
                  parent = root)

  # This creator stuff is just done one at a time.
  # Using the dataset PIs.
  XML::newXMLNode("creators", parent = root)

  lapply(contact,
         function(x) {
           if(length(x) > 0) {
             XML::addChildren(root[["creators"]],
                              XML::newXMLNode("creator",
                        .children = list(XML::newXMLNode("creatorName",
                                                    x$fullName),
                                         XML::newXMLNode("affiliation",
                                                    gsub(pattern = '\r\n', ', ', x$address)))))
           }
          })

  #' Add Titles:
  title <- paste0(frozen$frozendata$data$dataset$site$sitename, ' ',
                  frozen$frozendata$data$dataset$dataset$datasettype, ' dataset')

  XML::newXMLNode("titles", parent = root)
  XML::newXMLNode("title",
                  title,
                  attrs = c("xml:lang" = "en-us"),
                  parent = root[["titles"]])

  #' Add publisher information:
  XML::newXMLNode("publisher", "Neotoma Paleoecological Database", parent = root)

  #' Add publication year:
  XML::newXMLNode("publicationYear", format(Sys.Date(), "%Y"), parent = root)

  #' Add dataset "Subject" index:
  XML::newXMLNode("subjects",
                  XML::newXMLNode("subject",
                                  "Paleoecology",
                                  attrs = c("subjectScheme" = "Library of Congress",
                                            "schemeURI" = "http://id.loc.gov/authorities/subjects")),
                  parent = root)

  #' Add in the resource type:
  XML::newXMLNode("resourceType", "Dataset/Paleoecological Sample Data",
                  attrs = c("resourceTypeGeneral" = "Dataset"),
                  parent = root)

  #' Language information.  We assume english at this point.
  XML::newXMLNode("language", "English", parent = root)

  #' Get & add contributor information
  query <- readr::read_file('sql/contact_ids.sql')
  contacts <- dbGetQuery(con, query, ds_id)

  XML::newXMLNode("contributors", parent = root)

  lapply(1:nrow(contacts),
         function(x) {
           newXMLNode("contributor",
                      attrs = c("contributorType" = contacts$contributortype[x]),
                      .children = list(XML::newXMLNode("contributorName",
                                                  contacts$creatorname[x])),
                      parent = root[["contributors"]])
           })

  # Adding the dates in one at a time, we use the lapply to insert them
  # into the `dates` node.
  query <- readr::read_file('sql/mod_dates.sql')
  dates <- dbGetQuery(con, query, ds_id)

  XML::newXMLNode("dates", parent = root)
  lapply(1:nrow(dates),
         function(x) {
           XML::newXMLNode("date",
                      format(as.Date(dates[1,1]), "%Y-%m-%d"),
                             attrs = c("dateType" = dates[x, 2]),
                      parent = root[["dates"]])
           })

  #' Link to the JSON:
  XML::newXMLNode("relatedIdentifiers", parent = root)

  XML::newXMLNode("relatedIdentifier",
                  paste0("api-dev.neotomadb.org/v2.0/data/downloads/", ds_id),
                  attrs = list(relationType = "IsMetadataFor",
                               relatedIdentifierType = "URL",
                               relatedMetadataScheme = "json"),
                  parent = root[["relatedIdentifiers"]])
  XML::newXMLNode("relatedIdentifier",
                  paste0("data-dev.neotomadb.org/datasets/", ds_id),
                  attrs = list(relationType = "IsMetadataFor",
                               relatedIdentifierType = "URL",
                               relatedMetadataScheme = "json"),
                  parent = root[["relatedIdentifiers"]])

  # Add DOI tags for the publications as related identifiers:
  pubs <- fromJSON(paste0("http://api-dev.neotomadb.org/v2.0/data/datasets/", ds_id, "/publications"))
  dois <- na.omit(unlist(pubs$data$doi))

  if (length(dois) == 0) {
    # There's no current DOI
  } else {
    lapply(dois, function(x){
      XML::newXMLNode("relatedIdentifier", paste0("doi:", x),
                      attrs = list(relationType = "IsDocumentedBy",
                                   relatedIdentifierType = "DOI"),
                      parent = root[["relatedIdentifiers"]])
    })
  }

  # Number 13: size
  size <- as.numeric(object.size(httr::GET(paste0("api-dev.neotomadb.org/v2.0/data/downloads/", ds_id))))
  XML::newXMLNode("sizes",
                  XML::newXMLNode("size", paste0(ceiling(size / 1000), " KB")),
                  parent = root)

  # Number 14 (Adding Formats)
  XML::newXMLNode("formats",
                  parent = root)
  XML::newXMLNode("format",
                  "JSON",
                  parent = root[["formats"]])

  # Description
  newXMLNode("descriptions", parent  = root)
  newXMLNode("description",
             paste0("Raw data for the ",
                    title,
                    " obtained from the Neotoma Paleoecological Database."),
             parent = root[["descriptions"]],
             attrs = list("descriptionType" = "Abstract",
                          "xml:lang" = "EN"))

  # Number 16
  XML::addChildren(XML::newXMLNode("rightsList", parent = root),
                   children = XML::newXMLNode("rights", "CC-BY4",
                   attrs = c("rightsURI" = "http://creativecommons.org/licenses/by/4.0/deed.en_US")))

  # Locations
  loc <- fromJSON(frozen$frozendata$data$dataset$site$geography)

  XML::newXMLNode("geoLocations", parent = root)

  if (loc$type == "Point") {
    XML::newXMLNode("geoLocation",
                    XML::newXMLNode("geoLocationPoint",
                      .children = list(XML::newXMLNode("pointLatitude", loc$coordinates[2]),
                                       XML::newXMLNode("pointLongitude", loc$coordinates[1]))
                      , parent = root),
                    parent = root[["geoLocations"]])
  } else if (loc$type == "Polygon") {
    if(length(dim(loc$coordinates)) == 3) {
      coords <- loc$coordinates[1,,]
      assertthat::assert_that(nrow(coords) > 2 & ncol(coords) == 2)
      XML::newXMLNode("geoLocation",
                    XML::newXMLNode("geoLocationPolygon",
                                    .children = lapply(1:nrow(coords),
                                                       function(x){ XML::newXMLNode("polygonPoint",
                                                                   .children=list(XML::newXMLNode("pointLatitude", coords[x,2]),
                                                                                  XML::newXMLNode("pointLongitude", coords[x,1]))) })),
                    parent = root[["geoLocations"]])
    }
  }

  schema_test <- XML::xmlSchemaValidate("data/metadata.xsd", doc)

  if (!schema_test$status == 0) {

    # There's an error
    message("There was a validation error for this dataset.")

    return(schema_test)

  } else {

    XML::saveXML(doc = doc,
                 file = paste0('xml_files/', ds_id, "_output.xml"),
                 prefix = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>")

  }

  if (post == TRUE) {

    dc_pw <- readr::read_lines('datacite_auth.txt')

    urlbase <- 'https://mds.test.datacite.org/metadata'

    # See documentation at https://support.datacite.org/docs/mds-api-guide

    r = httr::PUT(url = urlbase,
                   # url = paste0(urlbase, "/10.21233/N3"),
                   config = httr::authenticate(user = dc_pw[1], password = dc_pw[2]),
                   httr::add_headers(c("Content-Type" = "application/xml;charset=UTF-8",
                                       "Accept" = "text/plain")),
                   body = upload_file(paste0('xml_files/', ds_id, '_output.xml'), type ="xml"))

  } else {

    out_doi <- NA

  }

  list(doc, out_doi)
}