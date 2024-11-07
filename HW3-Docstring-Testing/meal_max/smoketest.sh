#!/bin/bash

# Define the base URL for the Flask API
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

###############################################
# Health Checks
###############################################
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

###############################################
# Meal Management
###############################################
create_meal() {
  meal=$1 cuisine=$2 price=$3 difficulty=$4
  echo "Adding meal ($meal, $cuisine, $price, $difficulty)..."
  
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}" \
    | grep -q '"status": "success"'
  
  if [ $? -eq 0 ]; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1
  echo "Getting meal by ID ($meal_id)..."
  
  response=$(curl -s -X GET "$BASE_URL/get-meal/$meal_id")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then echo "$response" | jq .; fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

delete_meal_by_id() {
  meal_id=$1
  echo "Deleting meal by ID ($meal_id)..."
  
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

###############################################
# Battle Management 
###############################################
start_battle() {
   meal_1=$1 meal_2=$2
   
   echo "Starting battle between meals ($meal_1 and $meal_2)..."
   
   curl -s -X POST "$BASE_URL/start-battle" -H "Content-Type: application/json" \
     -d "{\"combatants\": [$meal_1, $meal_2]}" \
     | grep -q '"status": "success"'
   
   if [ $? -eq 0 ]; then 
     echo "Battle started successfully."
     
     if [ "$ECHO_JSON" = true ]; then 
       curl -s "$BASE_URL/get-battle-result" | jq .
     fi
   
   else 
     echo "Failed to start battle."
     exit 1 
   fi 
}

###############################################
# Leaderboard Management 
###############################################
get_leaderboard() {
   sort_by=$1
   
   echo "Getting leaderboard sorted by $sort_by..."
   
   response=$(curl -s -X GET "$BASE_URL/leaderboard?sort_by=$sort_by")
   
   if echo "$response" | grep -q '"status": "success"'; then 
     echo "Leaderboard retrieved successfully."
     if [ "$ECHO_JSON" = true ]; then 
       echo "$response" | jq .
     fi 
   else 
     echo "Failed to retrieve leaderboard."
     exit 1 
   fi 
}

###############################################
# Run Smoketests 
###############################################

# Health checks 
check_health 
check_db 

# Meal management tests 
create_meal 'Spaghetti' 'Italian' '15.50' 'MED'
create_meal 'Pizza' 'Italian' '20.00' 'HIGH'
create_meal 'Burger' 'American' '10.00' 'LOW'

get_meal_by_id '1'
delete_meal_by_id '2'

# Battle management tests 
start_battle 'Pizza' 'Burger'

# Leaderboard test 
get_leaderboard 'wins'

echo "All smoketests passed successfully!"