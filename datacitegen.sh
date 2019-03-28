#!/bin/bash

Rscript R/checkdatacite_doi.R || echo Failed to connect to DataCite Server
Rscript R/run_freezing.R || echo Failed to properly freeze data.
Rscript R/scripted_doi.R
