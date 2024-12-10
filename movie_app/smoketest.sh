#!/bin/bash

# Script: simple_smoketest.sh
# Description: Performs basic smoke tests on the movie application API endpoints
# Usage: ./simple_smoketest.sh [--echo-json]

BASE_URL="http://localhost:5000/api"
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

# Function to make API calls and optionally echo JSON
call_api() {
    local endpoint=$1
    local method=${2:-GET}
    local data=${3:-""}
    
    if [ -n "$data" ]; then
        response=$(curl -s -X $method "$BASE_URL$endpoint" -H "Content-Type: application/json" -d "$data")
    else
        response=$(curl -s -X $method "$BASE_URL$endpoint")
    fi
    
    echo "Testing $method $endpoint"
    if [ "$ECHO_JSON" = true ]; then
        echo "$response" | jq .
    fi
}

# Health check
call_api "/health"

# Movie API Tests
call_api "/search?title=Inception"
call_api "/movie/tt1375666"
call_api "/search/year?year=2010"

# User Authentication Test
call_api "/create-account" "POST" '{"username":"testuser","password":"testpass"}'
call_api "/login" "POST" '{"username":"testuser","password":"testpass"}'

echo "All smoke tests completed!"