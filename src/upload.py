import click

from . import utils


@click.group()
def cli():
    """Upload data to Amazon S3."""
    pass


@cli.command()
def kpcc():
    """Upload data for KPCC."""
    # Get all of the files we want to upload
    file_list = [utils.OPTIMIZED_DATA_DIR / "kpcc" / "latest.json"]
    print(f"📨 Uploading {len(file_list)} files")

    # Loop through them
    for path in file_list:
        # Parse an object name
        object_name = str(path).split("/data/")[-1]

        # Upload
        utils.upload_to_s3(path, object_name)


if __name__ == "__main__":
    cli()
