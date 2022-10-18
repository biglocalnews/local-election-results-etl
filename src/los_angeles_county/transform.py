import csv
import json
import pathlib

import click

from .. import utils

THIS_DIR = pathlib.Path(__file__).parent.absolute()


@click.command()
def cli(electionid=4269):
    """Transform the raw data into something ready to publish."""
    # Read in the raw file
    raw_path = utils.RAW_DATA_DIR / str(electionid) / "latest.json"
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
                pass

            # Tidy
            contest["candidates"] = contest["Candidates"]

            # Kill cruft
            del contest["Candidates"]
            del contest["Title"]
            del contest["Type"]
            del contest["AdditionalText"]
            del contest["MeasureText"]
            del contest["MeasurePassRate"]
            del contest["VoteFor"]

            # Add to our master list
            transformed_list["races"].append(contest)

    # Write out a timestamped file
    timestamp_path = (
        utils.TRANSFORMED_DATA_DIR
        / str(electionid)
        / f"{transformed_list['scraped_datetime']}.json"
    )
    utils.write_json(transformed_list, timestamp_path)

    # Overwrite the latest file
    latest_path = utils.TRANSFORMED_DATA_DIR / str(electionid) / "latest.json"
    utils.write_json(transformed_list, latest_path)


if __name__ == "__main__":
    cli()
