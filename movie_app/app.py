from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask_jwt_extended import JWTManager
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
    
    # JWT configuration
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

    # Override with any passed config
    if config:
        app.config.update(config)

    # Initialize extensions
    db.init_app(app)
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)

    # Register blueprints
    app.register_blueprint(routes)

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

    # Initialize database tables within application context
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    ####################################################
    # Healthchecks
    ####################################################

    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        app.logger.info('Health check')
        return make_response(jsonify({'status': 'healthy'}), 200)

    @app.route('/api/db-check', methods=['GET'])
    def db_check() -> Response:
        try:
            app.logger.info("Checking database connection...")
            app.logger.info("Database connection is OK.")
            return make_response(jsonify({'database_status': 'healthy'}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 404)

    ##########################################################
    # Movie Routes
    ##########################################################

    @app.route('/api/search', methods=['GET'])
    def search_movies_route() -> Response:
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
        try:
            result = get_movie_details(movie_id)
            return make_response(jsonify(result), 200)
        except Exception as e:
            logger.error(f"Failed to get movie details: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/search/year', methods=['GET'])
    def search_year_route() -> Response:
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
        try:
            result = get_movie_by_title(title)
            return make_response(jsonify(result), 200)
        except Exception as e:
            logger.error(f"Failed to get movie by title: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/search/type', methods=['GET'])
    def search_media_type_route() -> Response:
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