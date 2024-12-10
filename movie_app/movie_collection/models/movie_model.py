from dataclasses import dataclass
import logging
import os
import requests
from typing import List, Dict
from dotenv import load_dotenv
from movie_collection.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

# Load environment variables
load_dotenv()
BASE_URL = "http://www.omdbapi.com/"
api_key = os.getenv('API_KEY')

@dataclass
class Movie:
    """
    A class representing a movie with its attributes.

    Attributes:
        imdb_id (str): The IMDB ID of the movie.
        title (str): The title of the movie.
        year (str): The release year of the movie.
        director (str): The director of the movie.
        rating (float): The rating of the movie (0-10).
    """
    imdb_id: str
    title: str
    year: str
    director: str
    rating: float

    def __post_init__(self):
        """
        Validates the movie data after initialization.

        Raises:
            ValueError: If the rating is not between 0 and 10.
        """
        if not 0 <= self.rating <= 10:
            raise ValueError("Rating must be between 0 and 10.")

def search_movies(title: str) -> Dict:
    """
    Search for movies by title using the OMDB API.

    Args:
        title (str): The title of the movie to search for.

    Returns:
        Dict: JSON response containing search results from OMDB API - a list of the movies containing that title string.

    Raises:
        requests.RequestException: If the API request fails.
    """
    params = {
        's': title,
        'apikey': api_key
    }
    response = requests.get(BASE_URL, params=params)
    logger.info(f"Searched for movies with title: {title}")
    return response.json()

def get_movie_details(movie_id: str) -> Dict:
    """
    Get detailed information about a specific movie using its IMDB ID.

    Args:
        movie_id (str): The IMDB ID of the movie.

    Returns:
        Dict: JSON response containing detailed movie information.

    Raises:
        requests.RequestException: If the API request fails.
    """
    params = {
        'i': movie_id,
        'apikey': api_key,
        'plot': 'full'
    }
    response = requests.get(BASE_URL, params=params)
    logger.info(f"Retrieved details for movie ID: {movie_id}")
    return response.json()

def search_by_year(year: str) -> Dict:
    """
    Search for all movies from a specific year using the OMDB API.

    Args:
        year (str): The release year of the movies to search for.

    Returns:
        Dict: JSON response containing search results for the specified year.

    Raises:
        requests.RequestException: If the API request fails.
    """
    params = {
        'y': year,
        's': '*',  # Wildcard search to get all movies
        'apikey': api_key
    }
    response = requests.get(BASE_URL, params=params)
    logger.info(f"Searched for movies from year: {year}")
    return response.json()

def get_movie_by_title(title: str) -> Dict:
    """
    Get movie information by exact title match using the OMDB API.

    Args:
        title (str): The exact title of the movie.

    Returns:
        Dict: JSON response containing movie information.

    Raises:
        requests.RequestException: If the API request fails.
    """
    params = {
        't': title,
        'apikey': api_key
    }
    response = requests.get(BASE_URL, params=params)
    logger.info(f"Retrieved movie by exact title: {title}")
    return response.json()

def search_by_type(type: str) -> Dict:
    """
    Search for media by type using the OMDB API.

    Args:
        type_ (str): The type of media ('movie', 'series', 'episode').

    Returns:
        Dict: JSON response containing search results filtered by type.

    Raises:
        requests.RequestException: If the API request fails.
    """
    params = {
        's': '*',  # Wildcard search to get all media of the specified type
        'type': type,
        'apikey': api_key
    }
    response = requests.get(BASE_URL, params=params)
    logger.info(f"Searched for media of type: {type}")
    return response.json()