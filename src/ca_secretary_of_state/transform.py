import csv
import json
import pathlib
import typing

import click
from rich import print
from slugify import slugify

from .. import schema, utils


@click.command()
def cli():
    """Transform the raw data into something ready to publish."""
    # Read in the raw file
    raw_dir = utils.RAW_DATA_DIR / "ca_secretary_of_state"

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
        if slug == "courts-of-appeal":
            for division in raw_data["races"]:
                division_name = division["raceTitle"].split("-")[0].strip()
                for race in division["courts-of-appeal"]:
                    race_data = {
                        "raceTitle": f"{division_name}: {race['Name']}",
                        "Reporting": division["Reporting"],
                        "candidates": [
                            {"Name": "Yes", "Votes": race["yesVotes"]},
                            {"Name": "No", "Votes": race["noVotes"]},
                        ],
                    }
                    contest_list.append(race_data)
        elif "races" in raw_data:
            contest_list.extend(raw_data["races"])
        elif slug == "supreme-court":
            for race in raw_data["supreme-court"]:
                race_data = {
                    "raceTitle": f"Retain Supreme Court Justice {race['Name']}",
                    "Reporting": raw_data["Reporting"],
                    "candidates": [
                        {"Name": "Yes", "Votes": race["yesVotes"]},
                        {"Name": "No", "Votes": race["noVotes"]},
                    ],
                }
                contest_list.append(race_data)
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

    corrections = get_corrections()

    for contest in contest_list:
        # print(contest)
        # Tidy
        obj = ContestTransformer(contest, corrections)

        # Exclude records we don't want
        if not obj.include():
            continue

        # Add to our master list
        transformed_list["races"].append(obj.dump())

    # Write out a timestamped file
    output_dir = utils.TRANSFORMED_DATA_DIR / "ca_secretary_of_state"
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
            party=self.raw.get("Party", None),
            votes=self.clean_votes(self.raw["Votes"]),
            votes_percent=self.raw["votes_percent"],
            incumbent=self.raw.get("incumbent", None),
        )

    def clean_votes(self, value):
        """Clean votes value."""
        s = value.strip().replace(",", "")
        return int(s)

    def clean_name(self, name):
        """Clean name."""
        return name.lower().title()


class ContestTransformer(schema.BaseTransformer):
    """Map our raw contest data to the schema."""

    schema = schema.Contest

    def transform_data(self):
        """Create a new object."""
        data = dict(
            name=self.correct_name(),
            slug=self.get_slug(),
            description=self.correct_description(),
            geography=self.correct_geography(),
            level=self.correct_level(),
            precincts_reporting=self.raw["Reporting"],
            sort_order=self.correct_sort_order(),
        )

        # Mark incumbents
        candidate_list = [c for c in self.correct_incumbent(self.raw["candidates"])]

        # Set vote percentages
        vote_total = sum(self.clean_votes(c["Votes"]) for c in candidate_list)
        for c in candidate_list:
            if vote_total > 0:
                c["votes_percent"] = round(self.clean_votes(c["Votes"]) / vote_total, 4)
            else:
                c["votes_percent"] = 0.0

        # Validate candidate objects
        candidate_list = [CandidateResultTransformer(c).dump() for c in candidate_list]

        # Add to the data dictionary
        data["candidates"] = candidate_list

        # Return the transformed data
        return data

    def clean_votes(self, value):
        """Clean votes value."""
        s = value.strip().replace(",", "")
        return int(s)

    def get_slug(self):
        """Get a unique slug."""
        slug_name = self.correct_name()
        if "court" not in self.correct_geography().lower():
            slug_name = slug_name.split(":")[0].strip()
        return slugify(slug_name)

    def _get_correction(self):
        lookup = self.raw["raceTitle"].split("-")[0].strip()
        return self.corrections[lookup]

    def include(self):
        """Determine if we want to keep this record, based on our corrections."""
        return self._get_correction()["include"].lower() == "yes"

    def correct_name(self):
        """Correct the name field."""
        return self._get_correction()["clean_name"]

    def correct_description(self):
        """Correct the description field."""
        return self._get_correction()["clean_description"]

    def correct_geography(self):
        """Correct the geography field."""
        return self._get_correction()["clean_geography"]

    def correct_level(self):
        """Correct the level field."""
        return self._get_correction()["clean_level"]

    def correct_sort_order(self):
        """Correct the sort_order field."""
        return self._get_correction()["sort_order"] or None

    def correct_incumbent(
        self, candidate_list: typing.List[typing.Dict]
    ) -> typing.List[typing.Dict]:
        """Correct the incumbents field."""
        # Correct any incumbent candidates
        correction = self._get_correction()
        if correction and correction["incumbent"]:
            for c in candidate_list:
                c["incumbent"] = c["Name"].upper() in correction["incumbent"].upper()
            try:
                assert len([c for c in candidate_list if c["incumbent"]]) == 1
            except AssertionError:
                print(candidate_list, correction)
        return candidate_list


if __name__ == "__main__":
    cli()
