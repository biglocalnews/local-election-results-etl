Extract, transform and load election results posted online by the California election officials.

## Supports

- California Secretary of State
- Los Angeles County Registrar-Recorder/County Clerk

## Latest files

File | URL
:--- | :--
Secretary of State | [secretary_of_state/latest.json](https://mt-legacy-projects.s3.amazonaws.com/vgp-general-election-results-2022/data/transformed/secretary_of_state/latest.json)
Los Angeles County | [los_angeles_county/latest.json](https://mt-legacy-projects.s3.amazonaws.com/vgp-general-election-results-2022/data/transformed/los_angeles_county/latest.json)

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
pipenv run python -m src.secretary_of_state.download
```

Transform the data into something we want to publish.

```bash
pipenv run python -m src.los_angeles_county.transform
pipenv run python -m src.secretary_of_state.transform
```

Upload data to the Amazon S3 bucket.

```bash
pipenv run python -m src.upload
```
