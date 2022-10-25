from src import utils


def test_download():
    """Test downloading."""
    url = "https://results.lavote.gov/electionresults/json?electionid=4269"
    utils.request_json(url)


def test_now():
    """Test the localized timestamp."""
    utils.now()


def test_write_json(tmp_path):
    """Test writing out a JSON dict."""
    utils.write_json({}, tmp_path / "test.json")


def test_get_latest_paths():
    """Test that get_latest_paths returns the right stuff."""
    assert len(utils.get_latest_paths()) == 3
