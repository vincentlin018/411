from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from .user import User, db

# Create Blueprint instance
routes = Blueprint('routes', __name__)
# ---------------------------
# Account Routes
# ---------------------------

@routes.route('/create-account', methods=['POST'])
def create_account():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required.'}), 400

    username = data['username']
    password = data['password']

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists.'}), 409

    try:
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)  # Use password_hash
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Account created successfully.'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required.'}), 400

    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Incorrect username or password.'}), 401

    access_token = create_access_token(identity=username)
    return jsonify({'message': 'Login successful.', 'access_token': access_token}), 200

@routes.route('/update-password', methods=['PUT'])
@jwt_required()
def update_password():
    data = request.get_json()

    if not data or 'old_password' not in data or 'new_password' not in data:
        return jsonify({'error': 'Old password and new password are required.'}), 400

    username = get_jwt_identity()
    old_password = data['old_password']
    new_password = data['new_password']

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    if not check_password_hash(user.password_hash, old_password):
        return jsonify({'error': 'Incorrect old password.'}), 401

    try:
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({'message': 'Password updated successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500