Extract, transform and load election results posted online by the Los Angeles County Registrar-Recorder/County Clerk

## Latest files

File | URL
:--- | :--
Latest raw | [latest.json](https://raw.githubusercontent.com/biglocalnews/los-angeles-county-election-results-etl/main/data/raw/4269/latest.json)

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
AWS_ACCESS_KEY_SECRET=
AWS_REGION=
AWS_BUCKET=
```

If you want a common prefix on all objects uploaded to your bucket, add this optional variable.

```
AWS_PATH_PREFIX=your-prefix/
```

## Command pipeline

Download the raw data from the county website.

```bash
pipenv run python src/download.py
```

Upload data to the Amazon S3 bucket.

```bash
pipenv run python src/upload.py
```
