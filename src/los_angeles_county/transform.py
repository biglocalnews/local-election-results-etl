import csv
import json
import pathlib

import click

from .. import schema, utils

THIS_DIR = pathlib.Path(__file__).parent.absolute()


class CandidateResultTransformer(schema.BaseTransformer):
    """Map our raw candidate results to the schema."""

    schema = schema.CandidateResult

    def transform_data(self):
        """Create a new object."""
        return dict(
            name=self.raw["Name"],
            party=self.raw["Party"],
            votes=self.raw["Votes"],
            incumbent=self.raw.get("incumbent", False),
        )


class ContestTransformer(schema.BaseTransformer):
    """Map our raw contest data to the schema."""

    schema = schema.Contest

    def transform_data(self):
        """Create a new object."""
        return dict(
            name=self.raw["name"],
            description=self.raw["description"],
            geography=self.raw["geography"],
            candidates=[
                CandidateResultTransformer(c).dump() for c in self.raw["Candidates"]
            ],
        )


@click.command()
def cli(electionid=4269):
    """Transform the raw data into something ready to publish."""
    # Read in the raw file
    raw_path = (
        utils.RAW_DATA_DIR / "los_angeles_county" / str(electionid) / "latest.json"
    )
    raw_data = json.load(open(raw_path))

    # Read in the contest corrections
    correx_list = list(csv.DictReader(open(THIS_DIR / f"corrections/{electionid}.csv")))
    correx_lookup = {d["raw_name"]: d for d in correx_list}

    # Flatten the list
    transformed_list = {
        "scraped_datetime": utils.now().isoformat(),
        "updated_datetime": raw_data["Timestamp"],
        "races": [],
    }
    for contestgroup in raw_data["Election"]["ContestGroups"]:
        contest_list = contestgroup["Contests"]
        for contest in contest_list:
            # Pull any corrections
            try:
                correx = correx_lookup[contest["Title"]]
                # If we're excluding this record, skip out now
                if correx["include"].lower() == "no":
                    continue

                # Apply corrections
                contest["name"] = correx["clean_name"]
                contest["description"] = correx["clean_description"]
                contest["geography"] = correx["clean_geography"]

                # Mark incumbents
                for c in contest["Candidates"]:
                    if c["Name"] in correx["incumbent"]:
                        c["incumbent"] = True
                    else:
                        c["incumbent"] = False
            except KeyError:
                # For now we will let it run when there are errors.
                # We should consider removing this once we have a real feed
                contest["name"] = contest["Title"]
                contest["description"] = ""
                contest["geography"] = ""
                pass

            # Tidy
            obj = ContestTransformer(contest).dump()

            # Add to our master list
            transformed_list["races"].append(obj)

    # Write out a timestamped file
    output_dir = utils.TRANSFORMED_DATA_DIR / "los_angeles_county" / str(electionid)
    timestamp_path = output_dir / f"{transformed_list['scraped_datetime']}.json"
    utils.write_json(transformed_list, timestamp_path)

    # Overwrite the latest file
    latest_path = output_dir / "latest.json"
    utils.write_json(transformed_list, latest_path)


if __name__ == "__main__":
    cli()
