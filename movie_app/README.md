# CAS CS 411 Final Project: Movie App

The Movie Recommendation App offers users straightforward access to movie information and a personalized ranking of films tailored to their ratings.

# Features

1. **Search Movies**
    Allows users to search for a list of movies by title using the OMDB API.

2. **Get Movie Details**
    Allows users to get detailed information about a specific movie using its IMDB ID.

3. **Search by Year**
    Allows users to search for all movies from a specific year using the OMDB API.

4. **Get Movie by Title**
    Allows a user to get specific movie information by exact title match using the OMDB API.

5. **Search by type**
    Allows users to search for media by type (movie, series, or episode) using the OMDB API.


# Routes

## Route: /create-account

- **Request Type:** POST
- **Purpose:** Creates a new user account with a username and password.
- **Request Body:**
    - username (String): User's chosen username.
    - password (String): User's chosen password.
- **Response Format:** JSON
    - Success Response Example:
        - Code: 201
          Content: { "message": "Account created successfully" }
    - Error Responses:
        - Code: 400
          Content: { "error": "Username and password are required" }
        - Code: 409
          Content: { "error": "Username already exists" }
        - Code: 500
          Content: { "error": "Exception Error" }
- **Example Request:**
    {
        "username": "newuser1",
        "password": "securepassword"
    }
- **Example Response:**
    {
        "message": "Account created successfully",
        "status": "201"
    }

## Route: /login
- **Request Type:** POST
- **Purpose:** Authenticates a user with a username and password.
- **Request Body:**
    - username (String): User's chosen username.
    - password (String): User's chosen password.
- **Response Format:** JSON
    - Success Response Example:
        - Code: 200
        - Content: { "message": "Login successful", "access_token" : "{access_token}" }
    - Error Responses:
        - Code: 400
          Content: { "error": "Username and password are required" }
        - Code: 401
          Content: { "error": "Incorrect username or password" }
- **Example Request:**
    {
        "username": "newuser1",
        "password": "securepassword"
    }
- **Example Response:**
    {
        "message": "Login Successful",
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ...",
        "status": "200"
    }

## Route: /update-password
- **Request Type:** PUT
- **Purpose:** Allows users to change their password by providing their current password for verification.
- **Request Body:**
    - old_password (String): The user's current password.
    - new_password (String): The new password the user wants to set.
- **Response Format:** JSON
    - Success Response Example:
        - Code: 200
        - Content: { "message": "Password updated successfully" }
    - Error Responses:
        - Code: 400
          Content: { "error": "Old password and new password are required" }
        - Code: 404
          Content: { "error": "User not found" }
        - Code: 401
          Content: { "error": "Incorrect old password" }
        - Code: 500
          Content: { "error": "Exception Error" }
- **Example Request:**
    {
        "old_password": "currentpassword",
        "new_password": "newpassword"
    }
- **Example Response:**
    {
        "message": "Password updated successfully"
        "status": "200"
    }
