# Diagho Toolkit

## What is Diagho Toolkit ?

Diagho Toolkit is a python library which will read and parse a genomic file and return a generator with a pydantic model.

## What database is used ?

- OMIM
- HGNC
- HPO
- gnomAD
- gnomAD constraint
- VCF
- Fasta
- GFF3

## What pydantic model is returned ?

- Clinvar
- Feature
- Gene
- GnomAD
- GnomAD_constraint
- Pathology
- Region
- Sequence
- Symptom
- Variant

## Installation

Install diagho-toolkit in pip

    pip install diagho-toolkit

In your app if you want to parse a GFF3 file and get regions, you just need to call this method 

    from diagho_toolkit.gff3 import get_regions

    get_regions(gff3_filename="gff3_file_path")


And this method will return a Generator with a list of RegionModel that you can easily save into your database.


## Customize diagho-toolkit

Clone the project from [github](https://github.com/DiaghoProject/python-diagho-toolkit)

Build and run the docker image

    make docker

Into the container update and install requirements

    make requirements
    make install

Customize the project in the repository `src/diagho_toolkit`

Create and run tests

    make tests

Update documentation in `README.md` and `CHANGELOG.md` and version in `pyproject.toml`

Leave the container and commit your release into github

    git commit -am 'New commit'
    git push 

Update the version in test-PyPI in [github-actions](https://github.com/DiaghoProject/python-diagho-toolkit/actions) with the workflow `Test PyPi`.

When all is ready, run the workflow `Pypi` to update the official new version
