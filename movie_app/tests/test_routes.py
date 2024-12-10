import pytest
from flask import json
from werkzeug.security import generate_password_hash
from flask_bcrypt import Bcrypt
from datetime import timedelta
from flask_jwt_extended import JWTManager
from app import create_app
from sql.user import User, db
from sql.routes import routes

bcrypt = Bcrypt()

######################################################
#
#    Fixtures
#
######################################################

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_TOKEN_LOCATION': ['headers'],
        'JWT_SECRET_KEY': 'testing-key',
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1)
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_database(app):
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

######################################################
#
#    create_account
#
######################################################

def test_create_account(client, init_database):
    response = client.post('/create-account', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'Account created successfully.'

def test_create_account_duplicate(client, init_database):
    # First creation
    client.post('/create-account', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    
    # Duplicate creation attempt
    response = client.post('/create-account', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 409
    assert response.json['error'] == 'Username already exists.'

def test_create_account_missing_fields(client):
    response = client.post('/create-account', json={
        'username': 'testuser'
    })
    assert response.status_code == 400
    assert response.json['error'] == 'Username and password are required.'

######################################################
#
#    login
#
######################################################

def test_login_success(client, init_database):
    # Create user through the API
    client.post('/create-account', json={
        'username': 'testuser',
        'password': 'testpassword'
    })

    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 200
    assert response.json['message'] == 'Login successful.'
    assert 'access_token' in response.json

def test_login_invalid_credentials(client, init_database):
    # Create user
    client.post('/create-account', json={
        'username': 'testuser',
        'password': 'testpassword'
    })

    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json['error'] == 'Incorrect username or password.'

def test_login_missing_fields(client):
    response = client.post('/login', json={
        'username': 'testuser'
    })
    assert response.status_code == 400
    assert response.json['error'] == 'Username and password are required.'

######################################################
#
#    update_password
#
######################################################

def test_update_password_success(client, init_database):
    # Create user and login
    client.post('/create-account', json={
        'username': 'testuser',
        'password': 'oldpassword'
    })
    
    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'oldpassword'
    })
    access_token = login_response.json['access_token']

    response = client.put('/update-password', 
                         json={
                             'old_password': 'oldpassword',
                             'new_password': 'newpassword'
                         },
                         headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'Password updated successfully.'

def test_update_password_invalid_old_password(client, init_database):
    # Create user and login
    client.post('/create-account', json={
        'username': 'testuser',
        'password': 'oldpassword'
    })
    
    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'oldpassword'
    })
    access_token = login_response.json['access_token']

    response = client.put('/update-password', 
                         json={
                             'old_password': 'wrongpassword',
                             'new_password': 'newpassword'
                         },
                         headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 401
    assert response.json['error'] == 'Incorrect old password.'

def test_update_password_missing_fields(client, init_database):
    # Create user and login
    create_response = client.post('/create-account', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert create_response.status_code == 201, f"Account creation failed with status code {create_response.status_code}"

    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert login_response.status_code == 200, f"Login failed with status code {login_response.status_code}"

    print("Login response:", login_response.json)  # Debug print

    access_token = login_response.json.get('access_token')
    if access_token is None:
        pytest.fail("Access token not found in login response")

    response = client.put('/update-password', 
                         json={
                             'old_password': 'testpassword'
                         },
                         headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 400
    assert response.json['error'] == 'Old password and new password are required.'

def test_update_password_no_auth(client):
    response = client.put('/update-password', 
                         json={
                             'old_password': 'oldpassword',
                             'new_password': 'newpassword'
                         })
    assert response.status_code == 401