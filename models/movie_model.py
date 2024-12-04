from dataclasses import dataclass
import logging
import os
import sqlite3
from typing import Any, List

from movie_app.utils.sql_utils import get_db_connection
from movie_app.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class Movie:
    id: int
    title: str
    genre: str
    release_year: int
    director: str
    rating: float

    def __post_init__(self):
        """
        Validates the movie data after initialization.

        Raises:
            ValueError: If the release year is before 1888 or the rating is not between 0 and 10.
        """
        if self.release_year < 1888:
            raise ValueError("Release year must be 1888 or later.")
        if not 0 <= self.rating <= 10:
            raise ValueError("Rating must be between 0 and 10.")

def add_favorite_movie(user_id: int, movie_id: int) -> None:
    """
    Adds a movie to a user's favorites list.

    Args:
        user_id (int): The ID of the user.
        movie_id (int): The ID of the movie to add to favorites.

    Raises:
        ValueError: If the movie is already in the user's favorites.
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Insert the user-movie pair into the user_favorites table
            cursor.execute("""
                INSERT INTO user_favorites (user_id, movie_id)
                VALUES (?, ?)
            """, (user_id, movie_id))
            conn.commit()
            logger.info("Movie successfully added to favorites for user %s: %s", user_id, movie_id)
    except sqlite3.IntegrityError:
        logger.error("Movie already in favorites: User %s, Movie %s", user_id, movie_id)
        raise ValueError(f"Movie {movie_id} is already in favorites for user {user_id}")
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def get_favorite_movies(user_id: int) -> List[Movie]:
    """
    Retrieves a list of a user's favorite movies.

    Args:
        user_id (int): The ID of the user.

    Returns:
        List[Movie]: A list of Movie objects representing the user's favorite movies.

    Raises:
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Join the movies and user_favorites tables to get the favorite movies
            cursor.execute("""
                SELECT m.id, m.title, m.genre, m.release_year, m.director, m.rating
                FROM movies m
                JOIN user_favorites uf ON m.id = uf.movie_id
                WHERE uf.user_id = ?
            """, (user_id,))
            rows = cursor.fetchall()
            
        favorite_movies = [Movie(*row) for row in rows]
        logger.info("Retrieved %s favorite movies for user %s", len(favorite_movies), user_id)
        return favorite_movies
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def delete_favorite_movie(user_id: int, movie_id: int) -> None:
    """
    Removes a movie from a user's favorites list.

    Args:
        user_id (int): The ID of the user.
        movie_id (int): The ID of the movie to remove from favorites.

    Raises:
        ValueError: If the movie is not in the user's favorites.
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Delete the user-movie pair from the user_favorites table
            cursor.execute("""
                DELETE FROM user_favorites
                WHERE user_id = ? AND movie_id = ?
            """, (user_id, movie_id))
            conn.commit()
            if cursor.rowcount == 0:
                logger.info("Movie %s not found in favorites for user %s", movie_id, user_id)
                raise ValueError(f"Movie {movie_id} not found in favorites for user {user_id}")
            logger.info("Movie %s removed from favorites for user %s", movie_id, user_id)
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def get_movie_by_id(movie_id: int) -> Movie:
    """
    Retrieves a movie by its ID.

    Args:
        movie_id (int): The ID of the movie to retrieve.

    Returns:
        Movie: A Movie object representing the retrieved movie.

    Raises:
        ValueError: If the movie with the given ID is not found.
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Select the movie with the given ID
            cursor.execute("""
                SELECT id, title, genre, release_year, director, rating
                FROM movies WHERE id = ?
            """, (movie_id,))
            row = cursor.fetchone()
            
        if row:
            return Movie(*row)
        else:
            logger.info("Movie with ID %s not found", movie_id)
            raise ValueError(f"Movie with ID {movie_id} not found")
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def rate_movie(user_id: int, movie_id: int, rating: float) -> None:
    """
    Rates a movie for a user.

    Args:
        user_id (int): The ID of the user rating the movie.
        movie_id (int): The ID of the movie being rated.
        rating (float): The rating given to the movie (between 0 and 10).

    Raises:
        ValueError: If the rating is not between 0 and 10.
        sqlite3.Error: If any database error occurs.
    """
    if not 0 <= rating <= 10:
        raise ValueError("Rating must be between 0 and 10.")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Insert or replace the rating in the user_ratings table
            cursor.execute("""
                INSERT OR REPLACE INTO user_ratings (user_id, movie_id, rating)
                VALUES (?, ?, ?)
            """, (user_id, movie_id, rating))
            conn.commit()
            logger.info("Rating %s added for movie %s by user %s", rating, movie_id, user_id)
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def get_top_movies(limit: int = 10) -> List[Movie]:
    """
    Retrieves a list of top-rated movies.

    Args:
        limit (int): The maximum number of movies to retrieve (default is 10).

    Returns:
        List[Movie]: A list of Movie objects representing the top-rated movies.

    Raises:
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Select top-rated movies based on average user ratings
            cursor.execute("""
                SELECT id, title, genre, release_year, director, AVG(rating) as avg_rating
                FROM movies
                JOIN user_ratings ON movies.id = user_ratings.movie_id
                GROUP BY movies.id
                ORDER BY avg_rating DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            
        top_movies = [Movie(*row) for row in rows]
        logger.info("Retrieved top %s movies", len(top_movies))
        return top_movies
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def add_to_watchlist(user_id: int, movie_id: int) -> None:
    """
    Adds a movie to a user's watchlist.

    Args:
        user_id (int): The ID of the user.
        movie_id (int): The ID of the movie to add to the watchlist.

    Raises:
        ValueError: If the movie is already in the user's watchlist.
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Insert the user-movie pair into the user_watchlist table
            cursor.execute("""
                INSERT INTO user_watchlist (user_id, movie_id)
                VALUES (?, ?)
            """, (user_id, movie_id))
            conn.commit()
            logger.info("Movie %s added to watchlist for user %s", movie_id, user_id)
    except sqlite3.IntegrityError:
        logger.error("Movie already in watchlist: User %s, Movie %s", user_id, movie_id)
        raise ValueError(f"Movie {movie_id} is already in watchlist for user {user_id}")
    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
    

    