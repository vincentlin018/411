# CAS CS 411 Final Project: Movie App

The Movie Recommendation App offers users straightforward access to movie information and a personalized ranking of films tailored to their ratings.

# Features

1. **Search Movies:**
    Allows users to search for a list of movies by title using the OMDB API.

2. **Get Movie Details:**
    Allows users to get detailed information about a specific movie using its IMDB ID.

3. **Search by Year:**
    Allows users to search for all movies from a specific year using the OMDB API.

4. **Get Movie by Title:**
    Allows a user to get specific movie information by exact title match using the OMDB API.

5. **Search by type:**
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
    - Error Response Examples:
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
    - Error Response Examples:
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
    - Error Response Examples:
        - Code: 400
          Content: { "error": "Old password and new password are required" }
        - Code: 404
          Content: { "error": "User not found" }
        - Code: 401
          Content: { "error": "Incorrect old password" }
        - Code: 500
          Content: { "error": Exception Error }
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


## Route: /api/health
- **Request Type:** GET
- **Purpose:** Checks the health of the application server.
- **Response Format:** JSON
    - Success Response Example:
        - Code: 200
        - Content: { "status": "healthy" }
     
## Route: /api/db-check
- **Request Type:** GET
- **Purpose:** Verifies the connection to the database.
- **Response Format:** JSON
    - Success Response Example:
        - Code: 200
        - Content: { "database_status": "healthy" }
    - Error Response Examples:
        - Code: 404
        - Content: { "error": Exception Error }

     
## Route: /api/search
- **Request Type:** GET
- **Purpose:** Searches for movies based on a title.
- **Request Body:**
    - title (String): The title of the movie to search for.
- **Response Format:** JSON
    - Success Response Example:
        - Code: 200
        - Content: Search results in JSON format.
    - Error Response Examples:
        - Code: 400
          Content: { "error": "Title parameter is required" }
        - Code: 500
          Content: { "error": "Error message from the exception" }
- **Example Request:**
    {
        "title": "Star"
    }
- **Example Response:**
    {
      "movies": [
        {
          "title": "Star Wars: Episode IV - A New Hope",
          "year": "1977",
          "director": "George Lucas",
          "genre": "Action, Adventure, Sci-Fi"
        },
        {
          "title": "Star Wars: Episode V - The Empire Strikes Back",
          "year": "1980",
          "director": "Irvin Kershner",
          "genre": "Action, Adventure, Sci-Fi"
        },
        {
          "title": "Star Trek",
          "year": "2009",
          "director": "J.J. Abrams",
          "genre": "Action, Adventure, Sci-Fi"
        },
        {
          "title": "Star Trek: Into Darkness",
          "year": "2013",
          "director": "J.J. Abrams",
          "genre": "Action, Adventure, Sci-Fi"
        }
      ]
    }


## Route: /api/movie/<movie_id>
- **Request Type:** GET
- **Purpose:** Retrieves details for a specific movie by its ID.
- **Request Body:**
    - movie_id (String): The unique identifier for the movie.
- **Response Format:** JSON
    - Success Response Example:
        - Code: 200
        - Content: Movie details in JSON format
    - Error Response Examples:
        - Code: 500
          Content: { "error": Exception Error }
- **Example Request:**
    {
        "movie_id": "12345",
    }
- **Example Response:**
    {
      "title": "Inception",
      "year": "2010",
      "director": "Christopher Nolan",
      "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt"],
      "genre": "Sci-Fi, Thriller"
    }


## Route: /api/search/year
- **Request Type:** GET
- **Purpose:** Searches for movies by a specific year.
- **Request Body:**
    - year (String): The year to filter movies by.
- **Response Format:** JSON
    - Success Response Example:
        - Code: 200
        - Content: Search results in JSON format.
    - Error Response Examples:
        - Code: 400
          Content: { "error": "Year parameter is required" }
        - Code: 500
          Content: { "error": Exception Error }
- **Example Request:**
    {
        "year": "2010"
    }
- **Example Response:**
    {
      "movies": [
        {
          "title": "Inception",
          "year": "2010",
          "director": "Christopher Nolan"
        },
        {
          "title": "The Social Network",
          "year": "2010",
          "director": "David Fincher"
        }
      ]
    }


## Route: /api/movie/title/<title>
- **Request Type:** GET
- **Purpose:** Retrieves movie details by exact title.
- **Request Body:**
    - title (String): The title of the movie.
- **Response Format:** JSON
    - Success Response Example:
        - Code: 200
        - Content: Search results in JSON format.
    - Error Response Examples:
        - Code: 400
          Content: { "error": "Type parameter is required" }
        - Code: 500
          Content: { "error": Exception Error }
- **Example Request:**
    {
        "title": "Inception",
    }
- **Example Response:**
    {
      "title": "Inception",
      "year": "2010",
      "director": "Christopher Nolan",
      "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt"],
      "genre": "Sci-Fi, Thriller"
    }


## Route: /api/search/type
- **Request Type:** GET
- **Purpose:** Searches for media by type (e.g., movie, series).
- **Request Body:**
    - type (String): The type of media to search for.
- **Response Format:** JSON
    - Success Response Example:
        - Code: 200
        - Content: Search results in JSON format.
    - Error Response Examples:
        - Code: 400
          Content: { "error": "Year parameter is required" }
        - Code: 500
          Content: { "error": Exception Error }
- **Example Request:**
    {
        "type": "movie",
    }
- **Example Response:**
    {
      "movies": [
        {
          "title": "Inception",
          "year": "2010",
          "type": "movie"
        },
        {
          "title": "Iron Man",
          "year": "2008",
          "type": "Movie"
        }
      ]
    }
  
