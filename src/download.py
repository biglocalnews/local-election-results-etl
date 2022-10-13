import click
import requests


@click.command()
def cli(electionid=4269):
    """Download JSON data posted by the L.A. County Registrar/Recorder."""
    url = f"https://results.lavote.gov/electionresults/json?electionid={electionid}"
    click.echo(_request_json(url))


def _request_json(url):
    r = requests.get(url)
    assert r.ok
    return r.json()


if __name__ == "__main__":
    cli()
