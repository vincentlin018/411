#!/bin/bash

# Script: smoketest.sh
# Description: Performs smoke tests on the movie application API endpoints
# Usage: ./smoketest.sh [--echo-json]

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

# Function: check_health
# Description: Verifies the health status of the service
# Returns: 0 if healthy, exits with 1 if unhealthy
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

# Function: check_db
# Description: Verifies the database connection is working
# Returns: 0 if healthy, exits with 1 if unhealthy
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
# Movie API Tests
#
##########################################################

# Function: test_search_movies
# Description: Tests the movie search functionality
# Parameters:
#   $1 - movie title to search for
test_search_movies() {
    title=$1
    echo "Searching for movies with title: $title"
    response=$(curl -s -X GET "$BASE_URL/search?title=$title")
    if [ "$ECHO_JSON" = true ]; then
        echo "$response" | jq .
    fi
}

# Function: test_movie_details
# Description: Tests retrieving detailed movie information
# Parameters:
#   $1 - IMDB ID of the movie
test_movie_details() {
    movie_id=$1
    echo "Getting movie details for ID: $movie_id"
    response=$(curl -s -X GET "$BASE_URL/movie/$movie_id")
    if [ "$ECHO_JSON" = true ]; then
        echo "$response" | jq .
    fi
}

# Function: test_search_by_year
# Description: Tests searching movies by release year
# Parameters:
#   $1 - year to search for
test_search_by_year() {
    year=$1
    echo "Searching movies from year: $year"
    response=$(curl -s -X GET "$BASE_URL/search/year?year=$year")
    if [ "$ECHO_JSON" = true ]; then
        echo "$response" | jq .
    fi
}

# Function: test_movie_by_title
# Description: Tests retrieving a movie by exact title
# Parameters:
#   $1 - exact title of the movie
test_movie_by_title() {
    title=$1
    echo "Getting movie by exact title: $title"
    response=$(curl -s -X GET "$BASE_URL/movie/title/$title")
    if [ "$ECHO_JSON" = true ]; then
        echo "$response" | jq .
    fi
}

# Function: test_search_by_type
# Description: Tests searching media by type
# Parameters:
#   $1 - media type (movie, series, episode)
test_search_by_type() {
    type=$1
    echo "Searching media by type: $type"
    response=$(curl -s -X GET "$BASE_URL/search/type?type=$type")
    if [ "$ECHO_JSON" = true ]; then
        echo "$response" | jq .
    fi
}

# Execute the smoke tests
echo "Running Smoke Tests..."

# Health checks
check_health
check_db

# API Tests
test_search_movies "Inception"
test_movie_details "tt1375666"
test_search_by_year "2010"
test_movie_by_title "The Dark Knight"
test_search_by_type "movie"

echo "All tests completed!"