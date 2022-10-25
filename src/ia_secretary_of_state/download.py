import io

import click
import pandas as pd

from .. import utils


@click.group()
def cli():
    """Download data posted by the Iowa Secretary of State."""
    pass


@cli.command()
def statewide():
    """Download statewide data."""
    # Get the latest data
    url = "https://electionresults.iowa.gov/IA/115641/304799/reports/summary.zip"
    zip_obj = utils.request_zip(url)

    # Parse the CSV into JSON
    unzipped_obj = next(
        zip_obj.read(name) for name in zip_obj.namelist() if name == "summary.csv"
    )
    unzipped_df = pd.read_csv(io.StringIO(unzipped_obj.decode("latin-1")))
    data = unzipped_df.to_dict(orient="records")

    # Write out a timestamped file
    raw_dir = utils.RAW_DATA_DIR / "ia_secretary_of_state" / "statewide"
    timestamp_path = raw_dir / f"{utils.now().isoformat()}.json"
    utils.write_json(data, timestamp_path)

    # Overwrite the latest file
    latest_path = raw_dir / "latest.json"
    utils.write_json(data, latest_path)


if __name__ == "__main__":
    cli()
