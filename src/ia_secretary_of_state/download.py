import io
import zipfile

import click
import pandas as pd
from playwright.sync_api import sync_playwright

from .. import utils


@click.group()
def cli():
    """Download data posted by the Iowa Secretary of State."""
    pass


@cli.command()
def statewide():
    """Download statewide data."""
    # Get the latest data
    raw_dir = utils.RAW_DATA_DIR / "ia_secretary_of_state" / "statewide"

    # Fire up the browser
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        )

        # Go to the page
        page = context.new_page()
        page.goto(
            "https://electionresults.iowa.gov/IA/115641/web.285569/#/summary",
            timeout=10 * 1000,
        )
        print(page.content())

        # Download the ZIP
        zip_path = raw_dir / "statewide.zip"
        with page.expect_download() as download_info:
            selector = "xpath=//a[contains(@href, 'summary.zip')]"
            page.locator(selector).nth(0).dispatch_event("click")
            download_info.value.save_as(zip_path)

    # Parse the CSV into JSON
    zip_obj = zipfile.ZipFile(zip_path)
    unzipped_obj = next(
        zip_obj.read(name) for name in zip_obj.namelist() if name == "summary.csv"
    )
    unzipped_df = pd.read_csv(io.StringIO(unzipped_obj.decode("latin-1")))
    data = unzipped_df.to_dict(orient="records")

    # Write out a timestamped file
    timestamp_path = raw_dir / f"{utils.now().isoformat()}.json"
    utils.write_json(data, timestamp_path)

    # Overwrite the latest file
    latest_path = raw_dir / "latest.json"
    utils.write_json(data, latest_path)


if __name__ == "__main__":
    cli()
