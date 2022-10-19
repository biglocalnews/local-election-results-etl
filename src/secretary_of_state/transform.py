import json

import click
from rich import print

from .. import schema, utils


@click.command()
def cli():
    """Transform the raw data into something ready to publish."""
    # Read in the raw file
    raw_dir = utils.RAW_DATA_DIR / "secretary_of_state"

    # Get all of the files
    obj_list = raw_dir.glob("**/*")
    file_list = [o for o in obj_list if o.is_file() and "latest.json" in str(o)]
    print(f"Transforming {len(file_list)} raw files")

    # Flatten the race list
    contest_list = []
    for file_path in file_list:
        # Open the file
        raw_data = json.load(open(file_path))
        # Handle the file, based on its structure
        slug = file_path.parent.stem
        if "races" in raw_data:
            contest_list.extend(raw_data["races"])
        elif slug == "supreme-court":
            raw_data["candidates"] = raw_data.pop("supreme-court")
            contest_list.append(raw_data)
        elif slug == "ballot-measures":
            for race in raw_data["ballot-measures"]:
                race_data = {
                    "raceTitle": f"Proposition {race['Number']}: {race['Name']}",
                    "Reporting": raw_data["Reporting"],
                    "candidates": [
                        {"Name": "Yes", "Votes": race["yesVotes"]},
                        {"Name": "No", "Votes": race["noVotes"]},
                    ],
                }
                contest_list.append(race_data)
        else:
            contest_list.append(raw_data)

    # Load it up
    transformed_list = {
        "scraped_datetime": utils.now().isoformat(),
        "races": [],
    }

    for contest in contest_list:
        # Tidy
        obj = ContestTransformer(contest)

        # Add to our master list
        transformed_list["races"].append(obj.dump())

    # Write out a timestamped file
    output_dir = utils.TRANSFORMED_DATA_DIR / "secretary_of_state"
    timestamp_path = output_dir / f"{transformed_list['scraped_datetime']}.json"
    utils.write_json(transformed_list, timestamp_path)

    # Overwrite the latest file
    latest_path = output_dir / "latest.json"
    utils.write_json(transformed_list, latest_path)


class CandidateResultTransformer(schema.BaseTransformer):
    """Map our raw candidate results to the schema."""

    schema = schema.CandidateResult

    def transform_data(self):
        """Create a new object."""
        return dict(
            name=self.raw["Name"],
            party=self.raw.get("Party", None),
            votes=self.clean_votes(self.raw["Votes"]),
            incumbent=self.raw.get("incumbent", None),
        )

    def clean_votes(self, value):
        """Clean votes value."""
        s = value.strip().replace(",", "")
        return int(s)


class ContestTransformer(schema.BaseTransformer):
    """Map our raw contest data to the schema."""

    schema = schema.Contest

    def transform_data(self):
        """Create a new object."""
        return dict(
            name=self.raw["raceTitle"].split("-")[0].strip(),
            precincts_reporting=self.raw["Reporting"],
            candidates=[
                CandidateResultTransformer(c).dump() for c in self.raw["candidates"]
            ],
        )


if __name__ == "__main__":
    cli()
