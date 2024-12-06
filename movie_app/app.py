from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
# from flask_cors import CORS

from movie_app.models import add_favorite_movie, get_favorite_movies, delete_favorite_movie, get_movie_by_id, rate_movie, get_top_movies, add_to_watchlist
import logging

app = Flask(__name__)

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

# Base URL with API key parameter
api_key = os.getenv('API_KEY')
BASE_URL = f"http://www.omdbapi.com/?apikey={api_key}&"


def make_request(params: dict):
    """Base function for making API requests"""
    try:
        params['apikey'] = api_key
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"OMDb API request failed: {e}")
        raise


def get_movie_details(movie_id: str):
    params = {
        'i': movie_id
    }
    return make_request(params)

####################################################
#
# Healthchecks
#
####################################################

@app.route('/api/health', methods=['GET'])
def healthcheck() -> Response:
    """
    Health check route to verify the service is running.

    Returns:
        JSON response indicating the health status of the service.
    """
    app.logger.info('Health check')
    return make_response(jsonify({'status': 'healthy'}), 200)

@app.route('/api/db-check', methods=['GET'])
def db_check() -> Response:
    """
    Route to check if the database connection and movie table are functional.

    Returns:
        JSON response indicating the database health status.
    Raises:
        404 error if there is an issue with the database.
    """
    try:
        app.logger.info("Checking database connection...")
        check_database_connection()
        app.logger.info("Database connection is OK.")
        app.logger.info("Checking if movie table exists...")
        check_table_exists("movie")
        app.logger.info("movie table exists.")
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)


##########################################################
#
# Movie Model
#
##########################################################

@app.route('/api/add-favorite', methods=['POST'])
def add_favorite() -> Response:
    """
    Adds a movie to the user's favorite list.

    Expected JSON Input:
        - user_id (int): The user ID.
        - movie_id (int): The movie ID to add to favorites.

    Returns:
        JSON response indicating success operation.
    Raises:
        400 error
        500 error
    """
    app.logger.info('Creating new favorite song')

    try:
        data = request.get_json()

        user_id = data.get('user_id')
        movie_id = data.get('movie_id')

        if user_id is None or movie_id is None:
            return make_response(jsonify({'error': 'user_id and movie_id are required'}), 400)

        # Check that vars are ints 
        try:
            user_id = int(user_id)
    
        except ValueError as e:
            return make_response(jsonify({'error': 'User_id must be a valid int'}), 400)

        try:
            movie_id = int(movie_id)
    
        except ValueError as e:
            return make_response(jsonify({'error': 'Movie_id must be a valid int'}), 400)

        # call the function
        add_favorite_movie(user_id, movie_id)
        app.logger.info(f"Added movie {movie_id} to user {user_id}'s favorites")
        
        return make_response(jsonify({'status': 'success'}), 201)
    except Exception as e:
        app.logger.error(f"Failed to add favorite movie: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/get-favorites/<int:user_id>', methods=['GET'])
def get_favorites(user_id: int) -> Response:
    """
    Retrieves a user's favorite movies.

    Path Parameter:
        - user_id (int): The user ID.

    Returns:
        JSON response with the list of favorite movies.
    Raises:
        400 error
        500 error
    """
    
    try:
        app.logger.info(f"Retrieving favorites my user_id: {user_id}")

        if not user_id:
            return make_response(jsonify({'error': 'User_id is required'}), 400)

        favorites = get_favorite_movies(user_id)
        return make_response(jsonify({'status': 'success', 'favorites': [movie.__dict__ for movie in favorites]}), 200)
    except Exception as e:
        logger.error(f"Failed to get favorite movies: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/delete-favorite/<int:user_id>/<int:movie_id>', methods=['DELETE'])
def delete_favorite(user_id: int, movie_id: int) -> Response:
    """
    Deletes a movie from a user's favorite list.

    Path Parameters:
        - user_id (int): The user ID.
        - movie_id (int): The movie ID to remove.

    Returns:
        JSON response indicating success of the operation.
    Raises:
        500 error
    """
    try:
        app.logger.info(f"Deleting meal by user and movie id: {user_id}, {movie_id}")
        delete_favorite_movie(user_id, movie_id)
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        logger.error(f"Failed to delete favorite movie: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/get-movie/<int:movie_id>', methods=['GET'])
def get_movie(movie_id: int) -> Response:
    """
    Retrieves a movie by its movie ID.

    Path Parameter:
        - movie_id (int): The ID of the movie to retrieve.

    Returns:
        JSON response with movie details.
    Raises:
        500 error
    """
    try:
        app.logger.info(f"Retrieving movie by movie ID: {movie_id}")

        movie = get_movie_by_id(movie_id)
        return make_response(jsonify({'status': 'success', 'movie': movie.__dict__}), 200)
    except Exception as e:
        logger.error(f"Failed to get movie: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/rate-movie', methods=['POST'])
def rate_movie() -> Response:
    """
    Allows a user to rate a movie.

    Expected JSON Input:
        - user_id (int): The user ID.
        - movie_id (int): The movie ID.
        - rating (float): The rating between 0 and 10.

    Returns:
        JSON response indicating success or error.
    Raises:
        400 error
        500 error
    """
    try:
        data = request.get_json()

        user_id = data.get('user_id')
        movie_id = data.get('movie_id')
        rating = data.get('rating')

        if user_id is None or movie_id is None or rating is None:
            return make_response(jsonify({'error': 'user_id, movie_id, and rating are required'}), 400)

        if not isinstance(rating, (float, int)) or not 0 <= rating <= 10:
            return make_response(jsonify({'error': 'Rating must be a float between 0 and 10'}), 400)

        rate_movie(user_id, movie_id, rating)
        return make_response(jsonify({'status': 'success'}), 200)
    except Exception as e:
        logger.error(f"Failed to rate movie: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/top-movies', methods=['GET'])
def top_movies() -> Response:
    """
    Retrieves the top-rated movies.

    Query Parameter:
        - limit (int): The number of top movies to retrieve (default is 10).

    Returns:
        JSON response with top-rated movies.
    Raises: 
        500 error
    """
    try:
        limit = request.args.get('limit', default=10, type=int)

        app.logger.info("Generating top movie list")

        top_movies_list = get_top_movies(limit)
        return make_response(jsonify({'status': 'success', 'top_movies': [movie.__dict__ for movie in top_movies_list]}), 200)
    except Exception as e:
        logger.error(f"Failed to get top movies: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/add-watchlist', methods=['POST'])
def add_watchlist() -> Response:
    """
    Adds a movie to a user's watchlist.

    Expected JSON Input:
        - user_id (int): The user ID.
        - movie_id (int): The movie ID.

    Returns:
        JSON response indicating success.
    """
    app.logger.info('Creating new watchlist item')
    try:
        data = request.get_json()

        user_id = data.get('user_id')
        movie_id = data.get('movie_id')

        if user_id is None or movie_id is None:
            return make_response(jsonify({'error': 'user_id and movie_id are required'}), 400)

        add_to_watchlist(user_id, movie_id)

        return make_response(jsonify({'status': 'success'}), 201)
    except Exception as e:
        logger.error(f"Failed to add to watchlist: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
