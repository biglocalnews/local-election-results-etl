import csv
import json
import pathlib
import typing

import click

from .. import schema, utils


@click.command()
def cli():
    """Transform the raw data into something ready to publish."""
    # Read in the raw file
    raw_path = utils.RAW_DATA_DIR / "los_angeles_county" / "latest.json"
    raw_data = json.load(open(raw_path))

    corrections = get_corrections()

    # Flatten the list
    contest_list = []
    for contestgroup in raw_data["Election"]["ContestGroups"]:
        for contest in contestgroup["Contests"]:
            contest_list.append(contest)

    # Load it up
    transformed_list = {
        "scraped_datetime": utils.now().isoformat(),
        "updated_datetime": raw_data["Timestamp"],
        "races": [],
    }
    for contest in contest_list:
        # Tidy
        obj = ContestTransformer(contest, corrections)

        # Exclude records we don't want
        if not obj.include():
            continue

        # Add to our master list
        transformed_list["races"].append(obj.dump())

    # Write out a timestamped file
    output_dir = utils.TRANSFORMED_DATA_DIR / "los_angeles_county"
    timestamp_path = output_dir / f"{transformed_list['scraped_datetime']}.json"
    utils.write_json(transformed_list, timestamp_path)

    # Overwrite the latest file
    latest_path = output_dir / "latest.json"
    utils.write_json(transformed_list, latest_path)


def get_corrections() -> typing.Dict:
    """Open the lookup of corrections to the raw data."""
    this_dir = pathlib.Path(__file__).parent.absolute()
    correx_path = this_dir / "corrections.csv"
    correx_reader = csv.DictReader(open(correx_path))
    return {d["raw_name"]: d for d in correx_reader}


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
            name=self.correct_name(),
            description=self.correct_description(),
            geography=self.correct_geography(),
            candidates=[
                CandidateResultTransformer(c).dump() for c in self.raw["Candidates"]
            ],
        )

    def _get_correction(self):
        try:
            return self.corrections[self.raw["Title"]]
        except KeyError:
            return None

    def include(self):
        """Determine if we want to keep this record, based on our corrections."""
        correction = self._get_correction()
        if not correction:
            return True
        return correction["include"].lower() == "yes"

    def correct_name(self):
        """Correct the name field."""
        correction = self._get_correction()
        if not correction:
            return self.raw["Title"]
        return correction["clean_name"] or self.raw["Title"]

    def correct_description(self):
        """Correct the description field."""
        correction = self._get_correction()
        if not correction:
            return None
        return correction["clean_description"] or None

    def correct_geography(self):
        """Correct the geography field."""
        correction = self._get_correction()
        if not correction:
            return None
        return correction["clean_geography"] or None


if __name__ == "__main__":
    cli()
