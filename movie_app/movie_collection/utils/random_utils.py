import logging
import requests

from movie_collection.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

def get_random_movie(num_movies: int) -> int:
    """
    Fetches a random int between 1 and the number of movies in the catalog from random.org.

    Args:
        num_movies (int): The maximum number of movies to choose from.

    Returns:
        int: The random number fetched from random.org.

    Raises:
        RuntimeError: If the request to random.org fails or returns an invalid response.
        ValueError: If the response from random.org is not a valid integer.
    """
    url = f"https://www.random.org/integers/?num=1&min=1&max={num_movies}&col=1&base=10&format=plain&rnd=new"

    try:
        logger.info("Fetching random movie number from %s", url)
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        random_number_str = response.text.strip()

        try:
            random_number = int(random_number_str)
        except ValueError:
            raise ValueError(f"Invalid response from random.org: {random_number_str}")

        logger.info("Received random movie number: %d", random_number)
        return random_number

    except requests.exceptions.Timeout:
        logger.error("Request to random.org timed out.")
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.error("Request to random.org failed: %s", e)
        raise RuntimeError(f"Request to random.org failed: {e}")