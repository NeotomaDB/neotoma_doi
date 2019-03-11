# Neotoma Data DOI Generation

This repository is intended to act as the central management point for a variety of related repositories.  These repositories include:

*   [Neotoma Postgres Functions](https://github.com/neotomadb/Neotoma_SQL)
*   [Neotoma Landing Pages](https://github.com/NeotomaDB/ndbLandingPage)
*   [Neotoma API](https://github.com/NeotomaDB/api_nodetest)
*   [Neotoma DOI Technical Paper](https://github.com/NeotomaDB/AssignDOIs)
*   [Tilia API Endpoints](https://github.com/NeotomaDB/tilia_api)

## Contributors

*   [Simon Goring](http://goring.org)

This is currently a project under development.  All participants are expected to follow the [code of conduct](https://github.com/NeotomaDB/neotoma_doi/blob/master/code_of_conduct.md) for this project.

**NOTE**: The DataCite XML validation files in the `data/` folder (and `include` subfolder) were obtained from the [DataCite GitHub Schema repository](https://github.com/datacite/schema/tree/master/source/meta/kernel-4).

## Background

### DOIs and Frozen records in neotoma

Neotoma has three data access elements related to the atomic "dataset":
  * The live record (accessed from the various APIs)
  * The frozen record (saved one week from dataset submission)
  * The DOI metadata (posted to DataCite)

The live record lives as the relationship between elements in the database, [linked to the `datasets` table](http://open.neotomadb.org/dbschema/tables/datasets.html#Relationships).  This means that the *live* record can change over time, as taxonomies or linked chronologies change.

The *frozen* record is generated within a week of dataset submission.  It represents the state of the record at the time of upload.  This is to align with data-management best practices.  The frozen record lives in the `doi` schema of the database and is stored as a (Postgres) `jsonb` data type, along with the `datasetid`, the date created and date modified (if neccessary

The DOI metadata is stored with DataCite and is generated from [a script in this repository](https://github.com/NeotomaDB/neotoma_doi/blob/master/R/assign_doi.R).  When a new DOI is minted the DOI and related datasetid is added to [the `datasetdoi` table](http://open.neotomadb.org/dbschema/tables/datasetdoi.html).

## Work Flow For DOI Assignment

1.  A Neotoma data steward uploads a dataset to Neotoma (Tilia -> Tilia API -> NeotomaDB)

2.  Chron job running in `data-dev` checks daily for all records generated at least one week ago, without a "frozen" version (query in the [neotoma_doi repository](https://github.com/NeotomaDB/neotoma_doi/blob/master/sql/generatingFrozen.sql))
*   The script generates a frozen version of the dataset in the table `doi.frozen` in the database.
*   The function returns a list of aggregated datasetids along with the contact information for the dataset PI.
*   DOIs will be reserved for all datasets that have been generated.
*   DOIs will be added to the `ndb.datasetdoi` table *but* the `doi.frozen` entry will not be generated.
*   [**not currently implemented**] An email will be sent to each dataset PI with a listed email address.  The email will confirm that a DOI or a set of DOIs have been reserved, and that the PI has one week to review the relevant data.  It will also indicate that certain metadata (ORCIDs, email, site notes or descriptions) would assist in improving the usefulness of the data.  Provide a link to the Explorer and Landing Pages for the data record and a link to (?something?) to facilitate adding the required metadata.

3.  The PI of record can contact the steward to update the metadata (or a token can be generated to allow the PI to update things?)

4.  The same chron job in #2 will identify records where the `ndb.dataset` entry is older than 7 days, the dataset has an entry in `ndb.datasetdoi` and no entry in `doi.frozen`.  This assumes that PIs and stewards have had an opportunity to revise their datasets.
*   For each entry generate the frozen dataset using `doi.doifreeze()`.
*   For each entry run the function `assign_doi()` to build the DataCite XML file, and post the DOI metadata
*   Send a second email to each dataset PI indicating the DOIs have been successfully minted.

## Funding

This work is funded in part by grants from the National Science Foundation 1541002, 1550855 and 1550707.
