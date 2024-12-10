import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from user import User, db
from routes import create_account, login, update_password

bcrypt = Bcrypt()

######################################################
#
#    Fixtures
#
######################################################

@pytest.fixture
def mock_user_model(mocker):
    """Mock the User model."""
    return mocker.patch("routes.User")

@pytest.fixture
def mock_db_session(mocker):
    """Mock the database session."""
    return mocker.patch("routes.db.session")

@pytest.fixture
def app():
    """Fixture for Flask app."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app.test_client()

@pytest.fixture
def valid_user():
    """Fixture for a valid user."""
    return User(username="testuser", salt="salt123", hashed_password=bcrypt.generate_password_hash("passwordsalt123").decode())

######################################################
#
#    create_account
#
######################################################

def test_create_account_success(app, mock_user_model, mock_db_session):
    """Test successful account creation."""
    mock_user_model.query.filter_by.return_value.first.return_value = None

    response = app.post(
        "/create_account",
        json={"username": "newuser", "password": "securepassword"},
    )
    assert response.status_code == 201
    assert response.json["message"] == "User newuser created successfully"

def test_create_account_missing_fields(app):
    """Test account creation with missing fields."""
    response = app.post("/create_account", json={"username": "newuser"})
    assert response.status_code == 400
    assert response.json["error"] == "Username and password are required"

def test_create_account_existing_user(app, mock_user_model):
    """Test account creation with an existing username."""
    mock_user_model.query.filter_by.return_value.first.return_value = MagicMock()

    response = app.post(
        "/create_account",
        json={"username": "existinguser", "password": "securepassword"},
    )
    assert response.status_code == 400
    assert response.json["error"] == "Username already exists"

######################################################
#
#    login
#
######################################################

def test_login_success(app, mock_user_model, valid_user):
    """Test successful login."""
    mock_user_model.query.filter_by.return_value.first.return_value = valid_user

    response = app.post(
        "/login", json={"username": "testuser", "password": "password"}
    )
    assert response.status_code == 200
    assert response.json["message"] == "Login successful"

def test_login_invalid_credentials(app, mock_user_model):
    """Test login with invalid credentials."""
    mock_user_model.query.filter_by.return_value.first.return_value = None

    response = app.post(
        "/login", json={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json["error"] == "Invalid credentials"

def test_login_missing_fields(app):
    """Test login with missing fields."""
    response = app.post("/login", json={"username": "testuser"})
    assert response.status_code == 400
    assert response.json["error"] == "Username and password are required"

######################################################
#
#    update_password
#
######################################################

def test_update_password_success(app, mock_user_model, valid_user):
    """Test successful password update."""
    mock_user_model.query.filter_by.return_value.first.return_value = valid_user

    response = app.post(
        "/update_password",
        json={
            "username": "testuser",
            "old_password": "password",
            "new_password": "newpassword",
        },
    )
    assert response.status_code == 200
    assert response.json["message"] == "Password updated successfully"

def test_update_password_user_not_found(app, mock_user_model):
    """Test updating password for a nonexistent user."""
    mock_user_model.query.filter_by.return_value.first.return_value = None

    response = app.post(
        "/update_password",
        json={
            "username": "nonexistentuser",
            "old_password": "password",
            "new_password": "newpassword",
        },
    )
    assert response.status_code == 404
    assert response.json["error"] == "User not found"

def test_update_password_incorrect_old_password(app, mock_user_model, valid_user):
    """Test updating password with an incorrect old password."""
    mock_user_model.query.filter_by.return_value.first.return_value = valid_user

    response = app.post(
        "/update_password",
        json={
            "username": "testuser",
            "old_password": "wrongpassword",
            "new_password": "newpassword",
        },
    )
    assert response.status_code == 400
    assert response.json["error"] == "old password is incorrect"

def test_update_password_missing_fields(app):
    """Test updating password with missing fields."""
    response = app.post("/update_password", json={"username": "testuser"})
    assert response.status_code == 400
    assert response.json["error"] == "Username, old password, and new password are required"
