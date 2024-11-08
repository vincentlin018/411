import pytest
import requests
from unittest.mock import Mock

from meal_max.utils.random_utils import get_random

RANDOM_NUMBER = 42

@pytest.fixture
def mock_random_org(mocker):
    mock_response = mocker.Mock()
    mock_response.text = f"{RANDOM_NUMBER}"
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response

def test_get_random(mock_random_org):
    """Test retrieving a random number from random.org."""
    result = get_random()
    assert result == RANDOM_NUMBER, f"Expected random number {RANDOM_NUMBER}, but got {result}"
    requests.get.assert_called_once_with(
        "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new",
        timeout=5
    )

def test_get_random_request_failure(mocker):
    """Simulate a request failure."""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(RuntimeError, match="Request to random.org failed: Connection error"):
        get_random()

def test_get_random_timeout(mocker):
    """Simulate a timeout."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)
    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random()

def test_get_random_invalid_response(mock_random_org):
    """Simulate an invalid response (non-digit)."""
    mock_random_org.text = "invalid_response"
    with pytest.raises(ValueError, match="Invalid response from random.org: invalid_response"):
        get_random()

def test_get_random_zero(mock_random_org):
    """Test when random.org returns zero."""
    mock_random_org.text = "0.00"
    result = get_random()
    assert result == 0, "Expected 0 when random.org returns 0.00"

def test_get_random_one(mock_random_org):
    """Test when random.org returns one."""
    mock_random_org.text = "1.00"
    result = get_random()
    assert result == 1.00, "Expected 100 when random.org returns 1.00"

def test_get_random_float(mock_random_org):
    """Test when random.org returns a float."""
    mock_random_org.text = "0.42"
    result = get_random()
    assert result == 0.42, "Expected 0.42 when random.org returns 0.42"

def test_get_random_leading_zero(mock_random_org):
    """Test when random.org returns a number with leading zero."""
    mock_random_org.text = "0.05"
    result = get_random()
    assert result == 0.05, "Expected 0.05 when random.org returns 0.05"

def test_get_random_trailing_newline(mock_random_org):
    """Test when random.org returns a number with trailing newline."""
    mock_random_org.text = "0.42\n"
    result = get_random()
    assert result == 0.42, "Expected 0.42 when random.org returns 0.42 with trailing newline"

def test_get_random_http_error(mocker):
    """Test handling of HTTP errors."""
    mocker.patch("requests.get", side_effect=requests.exceptions.HTTPError("404 Client Error"))
    with pytest.raises(RuntimeError, match="Request to random.org failed: 404 Client Error"):
        get_random()

def test_get_random_connection_error(mocker):
    """Test handling of connection errors."""
    mocker.patch("requests.get", side_effect=requests.exceptions.ConnectionError("Connection refused"))
    with pytest.raises(RuntimeError, match="Request to random.org failed: Connection refused"):
        get_random()

def test_get_random_empty_response(mock_random_org):
    """Test handling of empty response."""
    mock_random_org.text = ""
    with pytest.raises(ValueError, match="Invalid response from random.org:"):
        get_random()

def test_get_random_request_params(mocker):
    """Test that the correct parameters are sent in the request."""
    mock_get = mocker.patch("requests.get")
    get_random()
    mock_get.assert_called_once_with(
        "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new",
        timeout=5
    )