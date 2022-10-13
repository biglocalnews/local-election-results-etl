from src import download


def test_download(tmpdir):
    """Test downloading."""
    url = "https://results.lavote.gov/electionresults/json?electionid=4269"
    download._request_json(url)
