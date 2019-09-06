# Neotoma Data DOI Generation

## Overview

This repository acts as the central management point for a set of repositories that are used to generate digital object identifiers (DOIs) for  datasets in the Neotoma Paleoecology Database.

DOIs are generated at the level of a dataset, which in Neotoma consists of all measurements of a given data type for a single collection unit at a site (e.g. all vertebrate fossils from a bone pile in a cave; all fossil pollen samples from a core in a lake; etc.)  All DOIs are associated with a landing page.

Linked repositories include:

*   [Neotoma Postgres Functions](https://github.com/neotomadb/Neotoma_SQL)
*   [Neotoma Landing Pages](https://github.com/NeotomaDB/ndbLandingPage)
*   [Neotoma API](https://github.com/NeotomaDB/api_nodetest)
*   [Neotoma DOI Technical Paper](https://github.com/NeotomaDB/AssignDOIs)
*   [Tilia API Endpoints](https://github.com/NeotomaDB/tilia_api)

## Contributors

*   [Simon Goring](http://goring.org)

This project is currently under development.  All participants are expected to follow the [code of conduct](https://github.com/NeotomaDB/neotoma_doi/blob/master/code_of_conduct.md) for this project.

**NOTE**: The DataCite XML validation files in the `data/` folder (and `include` subfolder) were obtained from the [DataCite GitHub Schema repository](https://github.com/datacite/schema/tree/master/source/meta/kernel-4).

## Background

### DOIs, Dataset Versioning, and Frozen Records in Neotoma

For any single dataset, its DOI provides access to three related elements:
  * The live record (accessed from NeotomaDB via the various APIs)
  * The frozen record (saved one week from dataset submission)
  * The DOI metadata (posted to DataCite)

The live record lives as the relationship between elements in the database, [linked to the `datasets` table](http://open.neotomadb.org/dbschema/tables/datasets.html#Relationships).  Thus, the *live* record can change over time, as taxonomies or linked chronologies change.  This

The *frozen* record is generated within a week of dataset submission.  It represents the state of the record at the time of upload.  This version supports journal requirements for data submissions and align with data-management best practices.  The frozen record lives in the `doi` schema of the database and is stored as a (Postgres) `jsonb` data type, along with the `datasetid`, the date created and date modified (if neccessary

The DOI metadata is stored with DataCite and is generated from [a script in this repository](https://github.com/NeotomaDB/neotoma_doi/blob/master/R/assign_doi.R).  When a new DOI is minted the DOI and related datasetid is added to [the `datasetdoi` table](http://open.neotomadb.org/dbschema/tables/datasetdoi.html).

## Workflow For DOI Assignment

1.  A Neotoma data steward uploads a dataset to Neotoma (Tilia -> Tilia API -> NeotomaDB)

2.  Chron job running in `data-dev` checks for all records generated at least one week ago, without a "frozen" version (query in the [neotoma_doi repository](https://github.com/NeotomaDB/neotoma_doi/blob/master/sql/generatingFrozen.sql))
  *   The script generates a frozen version of the dataset in the table `doi.frozen` in the database.
  *   The function returns a list of aggregated datasetids along with the contact information for the dataset PI.
  *   [**not currently implemented**] [An email](https://github.com/NeotomaDB/neotoma_doi/blob/master/data/email_text.txt) will be sent to each dataset PI with a listed email address. The email will confirm that a DOI or a set of DOIs have been reserved, and that the PI has one week to review the relevant data. It will also indicate that certain metadata (ORCIDs, email, site notes or descriptions) would assist in improving the usefulness of the data. Provide a link to the Explorer and Landing Pages for the data record and a link to (?something?) to facilitate adding the required metadata.

3.  The PI of record can contact the steward to update the metadata (or a token can be generated to allow the PI to update things?)

4.  The same chron job in #2 will identify records where the `ndb.dataset` entry is older than 14 days, the dataset has an entry in `doi.frozen` and no entry in `ndb.datasetdoi`.  This assumes that PIs and stewards have had an opportunity to revise their datasets.
  *   For each entry `UPDATE` the frozen dataset using `doi.doifreeze()`.
  *   For each entry run the function `assign_doi()` to build the DataCite XML file, and post the DOI metadata
  *   Send an email to each dataset PI indicating the DOIs have been successfully minted.

## NeotomaDB Backend Transition
The Neotoma backend relational database is in the process of being migrated from SQL Server to PostgreSQL.  During this transitional stage, new data are being entered into the SQL Server version via Tilia, while the DOIs are being generated for the datasets in the PostgreSQL version.  Data tables in the SQL Server version are periodically migrated to PostreSQL during this transitional stage and DOIs are minted then. This transitional stage will end when Tilia is tested and repointed to the PostgreSQL version.

## Funding

This work has been supported in part by grants from the National Science Foundation 1541002, 1550855 and 1550707.
