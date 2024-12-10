from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sql.user import db
from sql.routes import routes
import os
import requests
import logging
from movie_collection.models.movie_model import (
    search_movies,
    get_movie_details,  
    search_by_year,
    get_movie_by_title,
    search_by_type
)

def create_app(config=None):
    """
    Create and configure the Flask application.

    Args:
        config (dict, optional): Configuration dictionary to override default settings.

    Returns:
        Flask: Configured Flask application instance.
    """
    # Configure logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    load_dotenv()

    # Initialize Flask app
    app = Flask(__name__)
    
    # Default configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Override with any passed config
    if config:
        app.config.update(config)

    # Initialize extensions
    db.init_app(app)
    bcrypt = Bcrypt(app)

    # Register blueprints
    app.register_blueprint(routes)

    # Base URL with API key parameter
    api_key = os.getenv('API_KEY')
    BASE_URL = f"http://www.omdbapi.com/?apikey={api_key}&"

    def make_request(params: dict):
        """
        Make a request to the OMDb API.

        Args:
            params (dict): Dictionary of query parameters for the API request.

        Returns:
            dict: JSON response from the API.

        Raises:
            requests.exceptions.RequestException: If the API request fails.
        """
        try:
            params['apikey'] = api_key
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"OMDb API request failed: {e}")
            raise

    @app.before_first_request
    def create_tables():
        """
        Initialize the database by creating all tables defined in the models.

        This function is called before the first request to the application.
        """
        db.create_all()

    ####################################################
    #
    # Healthchecks
    #
    ####################################################

    @app.route('/')
    def home():
        """
        Root endpoint that returns a simple status check.

        Returns:
            JSON response indicating the service is running.
        """
        return jsonify({'status': 'ok'})

    @app.route('/api/health')
    def health_check():
        """
        Health check endpoint to verify service status.

        Returns:
            JSON response with health status and 200 OK status code.
        """
        return jsonify({'status': 'healthy'}), 200

    @app.route('/api/db-check')
    def db_check():
        """
        Database connection check endpoint.

        TODO: Implement actual database connection verification.

        Returns:
            JSON response with database status and 200 OK status code.
        """
        # Add your database connection check logic here
        return jsonify({'database_status': 'healthy'}), 200

    ##########################################################
    #
    # Movie Routes
    #
    ##########################################################

    @app.route('/api/search', methods=['GET'])
    def search_movies_route() -> Response:
        """
        Search for movies by title.

        Returns:
            Response: JSON response with search results or error message.
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
    def get_movie_details_route(movie_id: str) -> Response:
        """
        Get details for a specific movie by ID.

        Args:
            movie_id (str): The ID of the movie to retrieve details for.

        Returns:
            Response: JSON response with movie details or error message.
        """
        try:
            result = get_movie_details(movie_id)
            return make_response(jsonify(result), 200)
        except Exception as e:
            logger.error(f"Failed to get movie details: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/search/year', methods=['GET'])
    def search_year_route() -> Response:
        """
        Search for movies by year.

        Returns:
            Response: JSON response with search results or error message.
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
    def get_movie_by_title_route(title: str) -> Response:
        """
        Get movie details by title.

        Args:
            title (str): The title of the movie to retrieve details for.

        Returns:
            Response: JSON response with movie details or error message.
        """
        try:
            result = get_movie_by_title(title)
            return make_response(jsonify(result), 200)
        except Exception as e:
            logger.error(f"Failed to get movie by title: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/search/type', methods=['GET'])
    def search_media_type_route() -> Response:
        """
        Search for media by type (e.g., movie, series, episode).

        Returns:
            Response: JSON response with search results or error message.
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

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)