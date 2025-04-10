import neotomadoi

new_doi = neotomadoi.neotomaDOI(datasetid = 1, defaults = 'neotomadoi.yaml')
new_doi.update()
print(new_doi.data)
new_doi.validate('../data/datacite_schema.json')


""" 
"dates"
"relatedIdentifiers"
"sizes"
"formats"
"descriptions"
"identifier"

new_doi = neotomaDOI()

new_doi['identifiers'] = []

with open('../data/datacite_schema.json', 'r', encoding = 'UTF-8') as f:
    doi_schema = load(f)

jsonschema.validate(instance=new_doi, schema=doi_schema)
 """