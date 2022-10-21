import json

import click
from rich import print

from . import utils


@click.group()
def cli():
    """Create custom outputs for different clients."""
    pass


@cli.command()
def kpcc():
    """Create a custom output for KPCC."""
    # Get all of the files
    file_list = utils.get_latest_paths()
    kpcc_list = [
        f
        for f in file_list
        if "transformed" in str(f)
        and ("los_angeles_county" in str(f) or "ca_secretary_of_state" in str(f))
    ]
    print(f"📨 Combining {len(kpcc_list)} files")

    # Combine them
    combined_list = {
        "scraped_datetime": utils.now().isoformat(),
        "races": [],
    }
    for f in kpcc_list:
        data = json.load(open(f))
        combined_list["races"].extend(data["races"])

    # Write out a timestamped file
    output_dir = utils.OPTIMIZED_DATA_DIR / "kpcc"
    timestamp_path = output_dir / f"{combined_list['scraped_datetime']}.json"
    utils.write_json(combined_list, timestamp_path)

    # Overwrite the latest file
    latest_path = output_dir / "latest.json"
    utils.write_json(combined_list, latest_path)


if __name__ == "__main__":
    cli()
