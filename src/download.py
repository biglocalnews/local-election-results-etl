import click

from .utils import request_json


@click.command()
def cli(electionid=4269):
    """Download JSON data posted by the L.A. County Registrar/Recorder."""
    url = f"https://results.lavote.gov/electionresults/json?electionid={electionid}"
    click.echo(request_json(url))


if __name__ == "__main__":
    cli()
