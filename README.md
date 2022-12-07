Extract, transform and load election results posted online by local U.S. election officials.

## Supports

- California Secretary of State
- Los Angeles County Registrar-Recorder/County Clerk
- New York State Board of Elections
- Iowa Secretary of State

## Latest files

File | S3 URL | Pages URL |
:--- | :----- | :--------
California Secretary of State | | [ca_secretary_of_state/latest.json](https://biglocalnews.github.io/local-election-results-etl/transformed/ca_secretary_of_state/latest.json)
Los Angeles County |  | [los_angeles_county/latest.json](https://biglocalnews.github.io/local-election-results-etl/transformed/los_angeles_county/latest.json)
KPCC | [kpcc/latest.json](https://mt-legacy-projects.s3.amazonaws.com/vgp-general-election-results-2022/data/optimized/kpcc/latest.json) | [kpcc/latest.json](https://biglocalnews.github.io/local-election-results-etl/optimized/kpcc/latest.json)

## Getting started

Clone the repository and move into your code directory. Install the Python dependencies.

```bash
pipenv install --dev
```

Install [pre-commit](https://pre-commit.com/) hooks.

```bash
pipenv run pre-commit install
```

Create a `.env` file and fill it with the following Amazon Web Services services, which will authorize you to upload your files to an S3 bucket.

```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=
AWS_BUCKET=
```

If you want a common prefix on all objects uploaded to your bucket, add this optional variable.

```
AWS_PATH_PREFIX=your-prefix/
```

## Command pipeline

Download the raw data from the source websites.

```bash
pipenv run python -m src.los_angeles_county.download
pipenv run python -m src.ca_secretary_of_state.download
```

Transform the data into something we want to publish.

```bash
pipenv run python -m src.los_angeles_county.transform
pipenv run python -m src.ca_secretary_of_state.transform
```

Merge the common files

```bash
pipenv run python -m src.optimize kpcc
```

Export results to CSV.

```bash
pipenv run python -m src.export
```

Upload data to Amazon S3.

```bash
pipenv run python -m src.upload kpcc
```
