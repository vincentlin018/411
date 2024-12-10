from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """
    User model for storing user account information.

    This model represents a user in the database, storing essential
    information for authentication and identification.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The user's chosen username, must be unique.
        salt (str): A random string used in password hashing for additional security.
        hashed_password (str): The user's password, hashed for security.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    salt = db.Column(db.String(128), nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        """
        Provide a string representation of the User instance.

        Returns:
            str: A string representation of the User.
        """
        return f'<User {self.username}>'
