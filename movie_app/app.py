from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sql.user import db
import sql.routes
import os
import requests
import logging
from movie_app.models.movie_model import (
    search_movies,
    get_movie_details,
    search_by_year,
    get_movie_by_title,
    search_by_type
)

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

#Initializing the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

#Initializing the database and bcrypt
db.init_app(app)
bcrypt = Bcrypt(app)

#Taking routes for the user login/account creation/updating password
app.add_url_rule('/create_account', 'create_account', sql.routes.create_account, methods = ['POST'])
app.add_url_rule('/login', 'login', sql.routes.login, methods = ['POST'])
app.add_url_rule('/update_password', 'update_password', sql.routes.update_password, methods = ['POST'])

#Initializing the database/creating tables
@app.before_first_request
def create_tables():
    db.create_all()


####################################################
#
# Healthchecks
#
####################################################

@app.route('/api/health', methods=['GET'])
def healthcheck() -> Response:
    """
    Health check endpoint to verify the service is running.

    Returns:
        Response: JSON response with service health status.
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

@app.route('/api/search', methods=['GET'])
def search_movies() -> Response:
    """
    Search for movies by title using OMDB API.

    Query Parameters:
        title (str): The movie title to search for.

    Returns:
        Response: JSON response containing search results.

    Raises:
        400: If title parameter is missing.
        500: If API request fails.
    """
    try:
        title = request.args.get('title')
        if not title:
            return make_response(jsonify({'error': 'Title parameter is required'}), 400)
        
        result = search_movies(title)
        return make_response(jsonify(result), 200)
    except Exception as e:
        logger.error(f"Failed to search movies: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/movie/<movie_id>', methods=['GET'])
def get_movie_details(movie_id: str) -> Response:
    """
    Get detailed information about a specific movie.

    Path Parameters:
        movie_id (str): The IMDB ID of the movie.

    Returns:
        Response: JSON response containing movie details.

    Raises:
        500: If API request fails.
    """
    try:
        result = get_movie_details(movie_id)
        return make_response(jsonify(result), 200)
    except Exception as e:
        logger.error(f"Failed to get movie details: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/search/year', methods=['GET'])
def search_year() -> Response:
    """
    Search for movies by year.

    Query Parameters:
        year (str): The release year of the movies.

    Returns:
        Response: JSON response containing search results.

    Raises:
        400: If year parameter is missing.
        500: If API request fails.
    """
    try:
        year = request.args.get('year')
        if not year:
            return make_response(jsonify({'error': 'Year parameter is required'}), 400)
        
        result = search_by_year(year)
        return make_response(jsonify(result), 200)
    except Exception as e:
        logger.error(f"Failed to search movies by year: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/movie/title/<title>', methods=['GET'])
def get_movie_by_title(title: str) -> Response:
    """
    Get movie information by exact title match.

    Path Parameters:
        title (str): The exact title of the movie.

    Returns:
        Response: JSON response containing movie information.

    Raises:
        500: If API request fails.
    """
    try:
        result = get_movie_by_title(title)
        return make_response(jsonify(result), 200)
    except Exception as e:
        logger.error(f"Failed to get movie by title: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/search/type', methods=['GET'])
def search_media_type() -> Response:
    """
    Search for media by type.

    Query Parameters:
        type_ (str): The type of media ('movie', 'series', 'episode').

    Returns:
        Response: JSON response containing search results.

    Raises:
        400: If type parameter is missing.
        500: If API request fails.
    """
    try:
        type_ = request.args.get('type')
        if not type_:
            return make_response(jsonify({'error': 'Type parameter is required'}), 400)
        
        result = search_by_type(type_)
        return make_response(jsonify(result), 200)
    except Exception as e:
        logger.error(f"Failed to search by type: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)