import click
from bs4 import BeautifulSoup

from .. import utils


@click.command()
def cli():
    """Scrape data posted by the New York State Board of Election."""
    # Get the latest data
    url = "https://nyenr.elections.ny.gov/"
    html = utils.request_html(url)

    # Parse data
    soup = BeautifulSoup(html, "html.parser")
    table_list = soup.find_all(class_="datatable", role="table")
    race_list = [_parse_table(t) for t in table_list]

    # Prep to write it out
    now = utils.now().isoformat()
    data = {"url": url, "scraped_datetime": now, "races": race_list}

    # Write out a timestamped file
    timestamp_path = (
        utils.RAW_DATA_DIR
        / "ny_state_board_of_elections"
        / f"{utils.now().isoformat()}.json"
    )
    utils.write_json(data, timestamp_path)

    # Overwrite the latest file
    latest_path = utils.RAW_DATA_DIR / "ny_state_board_of_elections" / "latest.json"
    utils.write_json(data, latest_path)


def _parse_table(html):
    """Parse data from the site's HTML tables."""
    race_name = html["summary"].split(">")[1].strip()
    row_list = html.find_all("tr")
    precincts_reporting = (
        row_list[0].find_all("td")[-1].text.strip().split(":")[-1].strip()
    )
    candidates = []
    for row in row_list[3:-1]:
        cell_list = row.find_all("td")
        d = dict(
            name=cell_list[0].text,
            party=cell_list[1].text,
            votes=int(cell_list[4].text.replace(",", "")),
            votes_percent=cell_list[3].text,
        )
        candidates.append(d)
    return dict(
        race_name=race_name,
        precincts_reporting=precincts_reporting,
        candidates=candidates,
    )


if __name__ == "__main__":
    cli()
