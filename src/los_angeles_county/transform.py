import csv
import json
import pathlib
import typing

import click
from slugify import slugify

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
            name=self.clean_name(self.raw["Name"]),
            party=self.raw["Party"],
            votes=self.raw["Votes"],
            votes_percent=self.raw["votes_percent"],
            incumbent=self.raw.get("incumbent", False),
        )

    def clean_name(self, name):
        """Clean name."""
        return name.lower().title()


class ContestTransformer(schema.BaseTransformer):
    """Map our raw contest data to the schema."""

    schema = schema.Contest

    def transform_data(self):
        """Create a new object."""
        # Start off a data dictionary
        data = dict(
            name=self.correct_name(),
            slug=self.get_slug(),
            description=self.correct_description(),
            geography=self.correct_geography(),
            precincts_reporting=None,
        )

        # Mark incumbents
        candidate_list = [c for c in self.correct_incumbent(self.raw["Candidates"])]

        # Set vote percentages
        vote_total = sum(c["Votes"] for c in candidate_list)
        for c in candidate_list:
            if vote_total > 0:
                c["votes_percent"] = round(c["Votes"] / vote_total, 4)
            else:
                c["votes_percent"] = 0.0

        # Validate candidate objects
        candidate_list = [CandidateResultTransformer(c).dump() for c in candidate_list]

        # Add to the data dictionary
        data["candidates"] = candidate_list

        # Return the transformed data
        return data

    def _get_correction(self):
        return self.corrections[self.raw["Title"]]

    def include(self):
        """Determine if we want to keep this record, based on our corrections."""
        correction = self._get_correction()
        return correction["include"].lower() == "yes"

    def get_slug(self):
        return slugify(f"{self.correct_geography()} {self.correct_name()}")

    def correct_name(self):
        """Correct the name field."""
        return self._get_correction()["clean_name"]

    def correct_description(self):
        """Correct the description field."""
        return self._get_correction()["clean_description"]

    def correct_geography(self):
        """Correct the geography field."""
        return self._get_correction()["clean_geography"]

    def correct_incumbent(
        self, candidate_list: typing.List[typing.Dict]
    ) -> typing.List[typing.Dict]:
        """Correct the incumbents field."""
        # Correct any incumbent candidates
        correction = self._get_correction()
        if correction and correction["incumbent"]:
            for c in candidate_list:
                c["incumbent"] = c["Name"] in correction["incumbent"]
        return candidate_list


if __name__ == "__main__":
    cli()
