#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Movie Management
#
##########################################################

search_movies() {
    title=$1
    
    echo "Searching for movies by title ($title)..."

    
    response=$(curl -s -X GET "$BASE_URL/search-movies-by-title/$title")
    
    if echo "$response" | grep -q '"status": "success"'; then
    echo "Successfully seached for movies by title ($title)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Movie JSON (Title: $title):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to search for any movies by title ($title)."
    exit 1
  fi
}


get_movie_details() {
    movie_id=$1

    echo "Getting movie details by ID ($movie_id)..."

    response=$(curl -s -X GET "$BASE_URL/get-movie-details-by-id/$movie_id")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Movie details retrieved successfully by ID ($movie_id)."
        if [ "$ECHO_JSON" = true ]; then
        echo "Movie JSON (ID $movie_id):"
        echo "$response" | jq .
        fi
    else
        echo "Failed to get movie details by ID ($movie_id)."
        exit 1
    fi
}


search_by_year() {
    title=$1
    year=$2

    echo "Searching for movies by title and year (Title: '$title', Year: $year)..."
    response=$(curl -s -X GET "$BASE_URL/search-for-movies-by-title-and-year?title=$(echo $title | sed 's/ /%20/g')&year=$year")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Successfully searched for movies by title and year."
        if [ "$ECHO_JSON" = true ]; then
        echo "Movie JSON (by title and year):"
        echo "$response" | jq .
        fi
    else
        echo "Failed to search for any movies by title and year."
        exit 1
    fi
}


get_movie_by_title() {
    title=$1
    
    echo "Getting specific movie by title: ($title)..."

    
    response=$(curl -s -X GET "$BASE_URL/get-movie-by-title/$title")
    
    if echo "$response" | grep -q '"status": "success"'; then
    echo "Successfully retrieved movie by title ($title)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Movie JSON (Title: $title):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieved movie by title ($title)."
    exit 1
  fi
}

search_by_type() {
    title=$1
    type=$2

    echo "Searching for media by title and type (Title: '$title', Type: '$type')..."
    response=$(curl -s -X GET "$BASE_URL/search-by-title-and-type?title=$(echo $title | sed 's/ /%20/g')&type=$(echo $type | sed 's/ /%20/g')")
    if echo "$response" | grep -q '"status": "success"'; then
        echo "Successfully searched for media by title and type."
        if [ "$ECHO_JSON" = true ]; then
        echo "Movie JSON (by title and type):"
        echo "$response" | jq .
        fi
    else
        echo "Failed to search for any media by title and type."
        exit 1
    fi
}


# Execute the smoke tests
echo "Running Smoke Tests..."

# Health checks
check_health
check_db

# Movie Management Tests
# Search for movies by title (e.g., "Iron Man")
search_movies "Iron Man"

# Get movie details by ID (e.g., IMDb ID for "Iron Man")
get_movie_details "tt0371746"  # Example IMDb ID for "Iron Man"

# Search for movies by title and year (e.g., "The Avengers" in 2012)
search_by_year "The Avengers" 2012

# Get a specific movie by title (e.g., "Thor")
get_movie_by_title "Thor"

# Search for media by title and type (e.g., "WandaVision" as a series)
search_by_type "WandaVision" "series"

echo "All tests passed successfully!"