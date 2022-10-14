import json

import click

import utils


@click.command()
def cli(electionid=4269):
    """Transform the raw data into something ready to publish."""
    # Read in the raw file
    raw_path = utils.RAW_DATA_DIR / str(electionid) / "latest.json"
    raw_data = json.load(open(raw_path))

    # Flatten the list
    transformed_list = {
        "scraped_datetime": utils.now().isoformat(),
        "updated_datetime": raw_data["Timestamp"],
        "races": [],
    }
    for contestgroup in raw_data["Election"]["ContestGroups"]:
        contest_list = contestgroup["Contests"]
        for contest in contest_list:
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
