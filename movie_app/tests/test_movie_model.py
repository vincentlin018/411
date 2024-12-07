import pytest
from unittest.mock import patch, MagicMock
import requests
from movie_app.models.movie_model import (
    Movie,
    search_movies,
    get_movie_details,
    search_by_year,
    get_movie_by_title,
    search_by_type
)

######################################################
#
#    Fixtures
#
######################################################

@pytest.fixture
def mock_requests_get(mocker):
    """Mock the requests.get function."""
    return mocker.patch('requests.get')

@pytest.fixture
def sample_movie():
    """Fixture for a sample movie instance."""
    return Movie(
        imdb_id="tt1375666",
        title="Inception",
        year="2010",
        director="Christopher Nolan",
        rating=8.8
    )

######################################################
#
#    Movie Dataclass
#
######################################################

def test_movie_post_init_valid(sample_movie):
    """Test valid Movie instance creation."""
    assert sample_movie.title == "Inception"
    assert sample_movie.rating == 8.8

def test_movie_post_init_invalid_rating():
    """Test invalid Movie creation with rating outside 0-10."""
    with pytest.raises(ValueError, match="Rating must be between 0 and 10."):
        Movie(imdb_id="tt1375666", title="Test", year="2010", director="Test", rating=12.0)

######################################################
#
#    API Functions
#
######################################################

def test_search_movies_success(mock_requests_get):
    """Test searching movies by title."""
    mock_response = {
        'Search': [{'Title': 'Inception', 'Year': '2010', 'imdbID': 'tt1375666'}]
    }
    mock_requests_get.return_value.json.return_value = mock_response
    
    result = search_movies('Inception')
    assert result == mock_response

def test_get_movie_details_success(mock_requests_get):
    """Test getting detailed movie information."""
    mock_response = {
        'Title': 'Inception',
        'Year': '2010',
        'Director': 'Christopher Nolan',
        'imdbRating': '8.8'
    }
    mock_requests_get.return_value.json.return_value = mock_response
    
    result = get_movie_details('tt1375666')
    assert result == mock_response

def test_search_by_year_success(mock_requests_get):
    """Test searching movies by title and year."""
    mock_response = {
        'Search': [{'Title': 'Inception', 'Year': '2010', 'imdbID': 'tt1375666'}]
    }
    mock_requests_get.return_value.json.return_value = mock_response
    
    result = search_by_year('Inception', '2010')
    assert result == mock_response

def test_get_movie_by_title_success(mock_requests_get):
    """Test getting movie by exact title."""    
    mock_response = {
        'Title': 'Inception',
        'Year': '2010',
        'Director': 'Christopher Nolan'
    }
    mock_requests_get.return_value.json.return_value = mock_response
    
    result = get_movie_by_title('Inception')
    assert result == mock_response

def test_search_by_type_success(mock_requests_get):
    """Test searching media by type."""
    mock_response = {
        'Search': [{'Title': 'Inception', 'Type': 'movie', 'Year': '2010'}]
    }
    mock_requests_get.return_value.json.return_value = mock_response
    
    result = search_by_type('Inception', 'movie')
    assert result == mock_response

def test_api_request_failure(mock_requests_get):
    """Test handling of API request failure."""
    mock_requests_get.side_effect = requests.RequestException("API Error")
    
    with pytest.raises(requests.RequestException):
        search_movies('Inception')