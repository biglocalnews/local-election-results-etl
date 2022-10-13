import click

import utils


@click.command()
def cli():
    """Upload data directory to Amazon S3."""
    # Get all of the files
    obj_list = utils.DATA_DIR.glob("**/*")
    file_list = [o for o in obj_list if o.is_file()]

    # Loop through them
    for path in file_list:
        # Parse an object name
        object_name = str(path).split("/data/")[-1]

        # Upload
        utils.upload_to_s3(path, object_name)


if __name__ == "__main__":
    cli()
