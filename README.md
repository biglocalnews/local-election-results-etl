Extract, transform and load election results posted online by the Los Angeles County Registrar-Recorder/County Clerk

## Latest files

File | URL
:--- | :--
Latest raw | [./data/raw/latest.json](https://raw.githubusercontent.com/biglocalnews/los-angeles-county-election-results-etl/main/data/raw/latest.json)

## Getting started

Clone the repository and move into your code directory. Install the Python dependencies.

```bash
pipenv install --dev
```

Install [pre-commit](https://pre-commit.com/) hooks.

```bash
pipenv run pre-commit install
```

## Command pipeline

Download the raw data from the county website.

```bash
pipenv run python -m src.download
```
