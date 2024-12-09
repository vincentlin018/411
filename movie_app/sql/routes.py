from flask import request, jsonify
from flask_bcrypt import Bcrypt
from user import db, User

bcrypt = Bcrypt()

def create_account():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    if User.query.filter_by(username = username).first():
        return jsonify({"error": "Username already exists"}), 400
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.generate_password_hash(password + salt.decode()).decode()

    new_user = User(username = username, salt = salt.decode(), hashed_password = hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User {username} created successfully"}), 201

def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    user = User.query.filter_by(username = username).first()

    if user and bcrypt.check_password_hash(user.hashed_password, password + user.salt):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401
    
def update_password():
    data = request.get_json()
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not username or not old_password or not new_password:
        return jsonify({"error": "Username, old password, and new password are required"}), 400
    
    user = User.query.filter_by(username = username).first()

    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not bcrypt.check_password_hash(user.hashed_password, old_password + user.salt):
        return jsonify({"error": "old password is incorrect"}), 400
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.generate_password_hash(new_password + salt.decode()).decode()

    user.salt = salt.decode()
    user.hashed_password = hashed_password
    db.session.commit()