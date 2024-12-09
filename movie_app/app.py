from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from flask_sqlalchemy import SQLAlchem
import os
import requests
import logging
import bcrypt
from movie_app.models.movie_model import (
    search_movies,
    get_movie_details,
    search_by_year,
    get_movie_by_title,
    search_by_type
)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Base URL with API key parameter
api_key = os.getenv('API_KEY')
BASE_URL = f"http://www.omdbapi.com/?apikey={api_key}&"

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    salt = db.Column(db.String(32), nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)

with app.app_context():
    db.create_all()

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
    logger.info('Health check')
    return make_response(jsonify({'status': 'healthy'}), 200)

@app.route('/api/db-check', methods=['GET'])
def db_check() -> Response:
    """
    Route to check if the database connection and user table are functional.

    Returns:
        JSON response indicating the database health status.
    Raises:
        404 error if there is an issue with the database.
    """
    try:
        logger.info("Checking database connection...")
        User.query.first()
        logger.info("Database connection is OK.")
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        logger.error(f"Database check failed: {str(e)}")
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
    
####################################################
#
# User Authentication Routes
#
####################################################

@app.route('/create-account', methods=['POST'])
def create_account():
    """
    Create a new user account.
    
    Expects a JSON payload with 'username' and 'password'.
    Returns a success message and 201 status code if account is created,
    or an error message with appropriate status code if creation fails.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    logger.info(f"Attempting to create account for user: {username}")

    if not username or not password:
        logger.warning("Account creation failed: Missing username or password")
        return jsonify({"error": "Username and password are required"}), 400
    
    if User.query.filter_by(username=username).first():
        logger.warning(f"Account creation failed: Username {username} already exists")
        return jsonify({"error": "Username already exists"}), 400
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    new_user = User(username=username, salt=salt.decode(), hashed_password=hashed_password.decode())
    db.session.add(new_user)
    db.session.commit()

    logger.info(f"Account created successfully for user: {username}")
    return jsonify({"message": f"User {username} created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user.
    
    Expects a JSON payload with 'username' and 'password'.
    Returns a success message if login is successful,
    or an error message with appropriate status code if login fails.
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    logger.info(f"Login attempt for user: {username}")

    if not username or not password:
        logger.warning("Login failed: Missing username or password")
        return jsonify({"error": "Username and password are required"}), 400
    
    user = User.query.filter_by(username=username).first()

    if user and bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        logger.info(f"Login successful for user: {username}")
        return jsonify({"message": "Login successful"}), 200
    else:
        logger.warning(f"Login failed for user: {username}")
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/update-password', methods=['PUT'])
def update_password():
    """
    Update a user's password.
    
    Expects a JSON payload with 'username', 'old_password', and 'new_password'.
    Returns a success message if password is updated successfully,
    or an error message with appropriate status code if update fails.
    """
    data = request.get_json()
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    logger.info(f"Password update attempt for user: {username}")

    if not username or not old_password or not new_password:
        logger.warning("Password update failed: Missing required fields")
        return jsonify({"error": "Username, old password, and new password are required"}), 400
    
    user = User.query.filter_by(username=username).first()

    if not user:
        logger.warning(f"Password update failed: User {username} not found")
        return jsonify({"error": "User not found"}), 404
    
    if not bcrypt.checkpw(old_password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        logger.warning(f"Password update failed: Incorrect old password for user {username}")
        return jsonify({"error": "Old password is incorrect"}), 400
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)

    user.salt = salt.decode()
    user.hashed_password = hashed_password.decode()
    db.session.commit()

    logger.info(f"Password updated successfully for user: {username}")
    return jsonify({"message": "Password updated successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)