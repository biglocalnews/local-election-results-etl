import json

import click
import pandas as pd
from rich import print

from . import utils


@click.command()
def cli():
    """Export latest results as CSV files."""
    # Get all of the files
    file_list = [f for f in utils.get_latest_paths() if "raw" not in str(f)]
    print(f"📨 Uploading {len(file_list)} files")

    # Loop through them
    for path in file_list:
        # Parse an source
        source = str(path.parent).split("/")[-1]

        # Open the data
        data = json.load(open(path))

        # Transform it
        race_list = data.pop("races")
        flat_list = []
        for race in race_list:
            race["race_name"] = race.pop("name")
            candidates = race.pop("candidates")
            for cand in candidates:
                cand["candidate_name"] = cand.pop("name")
                cand.update(race)
                cand.update(data)
                cand["source"] = source
                flat_list.append(cand)

        # Parse and export it
        df = pd.DataFrame(flat_list)
        export_path = path.parent / "latest.csv"
        print(f"✏️ Writing CSV to {export_path}")
        df.to_csv(export_path, index=False)


if __name__ == "__main__":
    cli()
