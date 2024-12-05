import pytest
from unittest.mock import patch, MagicMock
from movie_model import (
    Movie,
    add_favorite_movie,
    get_favorite_movies,
    delete_favorite_movie,
    get_movie_by_id,
    rate_movie,
    get_top_movies,
    add_to_watchlist
)

######################################################
#
#    Fixtures
#
######################################################

@pytest.fixture
def mock_db_connection(mocker):
    """Mock the database connection."""
    mock_conn = mocker.patch("movie_model.get_db_connection")
    conn = MagicMock()
    mock_conn.return_value.__enter__.return_value = conn
    return conn

@pytest.fixture
def sample_movie():
    """Fixture for a sample movie instance."""
    return Movie(id=1, title="Inception", genre="Sci-Fi", release_year=2010, director="Nolan", rating=8.8)

######################################################
#
#    Movie Dataclass
#
######################################################

def test_movie_post_init_valid(sample_movie):
    """Test valid Movie instance creation."""
    assert sample_movie.title == "Inception"
    assert sample_movie.rating == 8.8

def test_movie_post_init_invalid_release_year():
    """Test invalid Movie creation with release year before 1888."""
    with pytest.raises(ValueError, match="Release year must be 1888 or later."):
        Movie(id=1, title="Test", genre="Test", release_year=1800, director="Test", rating=8.0)

def test_movie_post_init_invalid_rating():
    """Test invalid Movie creation with rating outside 0-10."""
    with pytest.raises(ValueError, match="Rating must be between 0 and 10."):
        Movie(id=1, title="Test", genre="Test", release_year=2010, director="Test", rating=12.0)

######################################################
#
#    add_favorite_movie
#
######################################################

def test_add_favorite_movie_success(mock_db_connection):
    """Test adding a favorite movie."""
    add_favorite_movie(user_id=1, movie_id=1)
    mock_db_connection.cursor().execute.assert_called_once_with(
        "INSERT INTO user_favorites (user_id, movie_id) VALUES (?, ?)", (1, 1)
    )
    mock_db_connection.commit.assert_called_once()

def test_add_favorite_movie_duplicate(mock_db_connection):
    """Test adding a duplicate favorite movie."""
    mock_db_connection.cursor().execute.side_effect = sqlite3.IntegrityError
    with pytest.raises(ValueError, match="Movie 1 is already in favorites for user 1"):
        add_favorite_movie(user_id=1, movie_id=1)

######################################################
#
#    get_favorite_movies
#
######################################################

def test_get_favorite_movies_success(mock_db_connection, sample_movie):
    """Test retrieving favorite movies."""
    mock_db_connection.cursor().fetchall.return_value = [
        (1, "Inception", "Sci-Fi", 2010, "Nolan", 8.8)
    ]
    movies = get_favorite_movies(user_id=1)
    assert len(movies) == 1
    assert movies[0] == sample_movie

def test_get_favorite_movies_empty(mock_db_connection):
    """Test retrieving favorite movies when the list is empty."""
    mock_db_connection.cursor().fetchall.return_value = []
    movies = get_favorite_movies(user_id=1)
    assert movies == []

######################################################
#
#    delete_favorite_movie
#
######################################################

def test_delete_favorite_movie_success(mock_db_connection):
    """Test removing a favorite movie."""
    mock_db_connection.cursor().rowcount = 1
    delete_favorite_movie(user_id=1, movie_id=1)
    mock_db_connection.cursor().execute.assert_called_once_with(
        "DELETE FROM user_favorites WHERE user_id = ? AND movie_id = ?", (1, 1)
    )
    mock_db_connection.commit.assert_called_once()

def test_delete_favorite_movie_not_found(mock_db_connection):
    """Test removing a movie that is not in favorites."""
    mock_db_connection.cursor().rowcount = 0
    with pytest.raises(ValueError, match="Movie 1 not found in favorites for user 1"):
        delete_favorite_movie(user_id=1, movie_id=1)

######################################################
#
#    get_movie_by_id
#
######################################################

def test_get_movie_by_id_success(mock_db_connection, sample_movie):
    """Test retrieving a movie by ID."""
    mock_db_connection.cursor().fetchone.return_value = (
        1, "Inception", "Sci-Fi", 2010, "Nolan", 8.8
    )
    movie = get_movie_by_id(movie_id=1)
    assert movie == sample_movie

def test_get_movie_by_id_not_found(mock_db_connection):
    """Test retrieving a movie by ID that doesn't exist."""
    mock_db_connection.cursor().fetchone.return_value = None
    with pytest.raises(ValueError, match="Movie with ID 1 not found"):
        get_movie_by_id(movie_id=1)

######################################################
#
#    rate_movie
#
######################################################

def test_rate_movie_success(mock_db_connection):
    """Test rating a movie."""
    rate_movie(user_id=1, movie_id=1, rating=9.5)
    mock_db_connection.cursor().execute.assert_called_once_with(
        "INSERT OR REPLACE INTO user_ratings (user_id, movie_id, rating) VALUES (?, ?, ?)",
        (1, 1, 9.5),
    )
    mock_db_connection.commit.assert_called_once()

def test_rate_movie_invalid_rating():
    """Test rating a movie with an invalid rating."""
    with pytest.raises(ValueError, match="Rating must be between 0 and 10."):
        rate_movie(user_id=1, movie_id=1, rating=11.0)

######################################################
#
#    get_top_movies
#
######################################################

def test_get_top_movies_success(mock_db_connection):
    """Test retrieving top-rated movies."""
    mock_db_connection.cursor().fetchall.return_value = [
        (1, "Inception", "Sci-Fi", 2010, "Nolan", 9.0)
    ]
    movies = get_top_movies(limit=1)
    assert len(movies) == 1
    assert movies[0].title == "Inception"

######################################################
#
#    add_to_watchlist
#
######################################################

def test_add_to_watchlist_success(mock_db_connection):
    """Test adding a movie to the watchlist."""
    add_to_watchlist(user_id=1, movie_id=1)
    mock_db_connection.cursor().execute.assert_called_once_with(
        "INSERT INTO user_watchlist (user_id, movie_id) VALUES (?, ?)", (1, 1)
    )
    mock_db_connection.commit.assert_called_once()

def test_add_to_watchlist_duplicate(mock_db_connection):
    """Test adding a duplicate movie to the watchlist."""
    mock_db_connection.cursor().execute.side_effect = sqlite3.IntegrityError
    with pytest.raises(ValueError, match="Movie 1 is already in watchlist for user 1"):
        add_to_watchlist(user_id=1, movie_id=1)
