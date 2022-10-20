import click

from . import utils


@click.command()
def cli():
    """Upload data directory to Amazon S3."""
    # Get all of the files
    file_list = utils.get_latest_paths()
    print(f"📨 Uploading {len(file_list)} files")

    # Loop through them
    for path in file_list:
        # Parse an object name
        object_name = str(path).split("/data/")[-1]

        # Upload
        utils.upload_to_s3(path, object_name)


if __name__ == "__main__":
    cli()
