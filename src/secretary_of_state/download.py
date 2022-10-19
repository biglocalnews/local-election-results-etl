import click

from .. import utils


@click.command()
def cli():
    """Download JSON data posted by the California Secretary of State."""
    slug_list = [
        "governor",
        "lieutenant-governor",
        "secretary-of-state",
        "controller",
        "treasurer",
        "attorney-general",
        "insurance-commissioner",
        "superintendent-of-public-instruction",
        "us-senate",
        "us-senate-unexpired-term",
        # "supreme-court",
        "ballot-measures",
        "board-of-equalization/district/all",
        "us-rep/district/all",
        "state-senate/district/all",
        "state-assembly/district/all",
    ]

    # Get the latest data
    for slug in slug_list:
        url = f"https://api.sos.ca.gov/returns/{slug}"
        data = utils.request_json(url)
        now = utils.now().isoformat()
        if isinstance(data, list):
            data = {"slug": slug, "url": url, "scraped_datetime": now, "races": data}
        else:
            data["slug"] = slug
            data["url"] = url
            data["scraped_datetime"] = now

        # Write out a timestamped file
        folder_name = f"{slug.split('/')[0]}"
        timestamp_path = (
            utils.RAW_DATA_DIR
            / "secretary_of_state"
            / folder_name
            / f"{utils.now().isoformat()}.json"
        )
        utils.write_json(data, timestamp_path)

        # Overwrite the latest file
        latest_path = (
            utils.RAW_DATA_DIR / "secretary_of_state" / folder_name / "latest.json"
        )
        utils.write_json(data, latest_path)


if __name__ == "__main__":
    cli()
