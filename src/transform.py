import json

import click
from rich import print

import utils


@click.command()
def cli(electionid=4269):
    """Transform the raw data into something ready to publish."""
    # Read in the raw file
    raw_path = utils.RAW_DATA_DIR / str(electionid) / "latest.json"
    data = json.load(open(raw_path))

    print(data)


if __name__ == "__main__":
    cli()
