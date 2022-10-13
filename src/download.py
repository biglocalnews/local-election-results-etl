import click

import utils


@click.command()
def cli(electionid=4269):
    """Download JSON data posted by the L.A. County Registrar/Recorder."""
    # Get the latest data
    url = f"https://results.lavote.gov/electionresults/json?electionid={electionid}"
    data = utils.request_json(url)

    # Write out a timestamped file
    timestamp_path = utils.RAW_DATA_DIR / f"{utils.now().isoformat()}.json"
    utils.write_json(data, timestamp_path)

    # Overwrite the latest file
    latest_path = utils.RAW_DATA_DIR / "latest.json"
    utils.write_json(data, latest_path)


if __name__ == "__main__":
    cli()
