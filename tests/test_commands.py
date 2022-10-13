from retry import retry

from src import utils


@retry()
def test_download(tmpdir):
    """Test downloading."""
    url = "https://results.lavote.gov/electionresults/json?electionid=4269"
    utils.request_json(url)
