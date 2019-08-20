#!/bin/bash
echo Checking existing records in DataCite. . .
Rscript R/checkdatacite_doi.R || echo Failed to connect to DataCite Server
echo Freezing unfrozen records. . .
Rscript R/run_freezing.R || echo Failed to properly freeze data.
echo Running script on required DOIs.
Rscript R/scripted_doi.R
