import json

import click
from slugify import slugify

from .. import schema, utils


@click.command()
def cli():
    """Transform the raw data into something ready to publish."""
    # Read in the raw file
    raw_path = utils.RAW_DATA_DIR / "ny_state_board_of_elections" / "latest.json"
    raw_data = json.load(open(raw_path))

    # Load it up
    transformed_list = {
        "scraped_datetime": utils.now().isoformat(),
        "races": [],
    }
    for contest in raw_data["races"]:
        # Tidy
        obj = ContestTransformer(contest)

        # Add to our master list
        transformed_list["races"].append(obj.dump())

    # Write out a timestamped file
    output_dir = utils.TRANSFORMED_DATA_DIR / "ny_state_board_of_elections"
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
            name=self.raw["name"],
            party=self.raw["party"],
            votes=self.raw["votes"],
            votes_percent=self.raw["votes_percent"],
            incumbent=None,
        )


class ContestTransformer(schema.BaseTransformer):
    """Map our raw contest data to the schema."""

    schema = schema.Contest

    def transform_data(self):
        """Create a new object."""
        # Start off a data dictionary
        data = dict(
            name=self.raw["race_name"],
            slug=slugify(self.raw["race_name"]),
            description=None,
            geography=None,
            precincts_reporting=self.raw["precincts_reporting"],
        )
        candidate_list = self.raw["candidates"]

        # Set vote percentages
        vote_total = sum(c["votes"] for c in candidate_list)
        for c in candidate_list:
            if vote_total > 0:
                c["votes_percent"] = round(c["votes"] / vote_total, 4)
            else:
                c["votes_percent"] = 0.0

        # Validate candidate objects
        candidate_list = [CandidateResultTransformer(c).dump() for c in candidate_list]

        # Add to the data dictionary
        data["candidates"] = candidate_list

        # Return the transformed data
        return data


if __name__ == "__main__":
    cli()
