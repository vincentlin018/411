#!/bin/bash

# Load the environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Check if CREATE_DB is true, and run the database creation script if so
if [ "$CREATE_DB" = "true" ]; then
    echo "Creating the database..."
    python -c "
from movie_collection.utils.sql_utils import get_db_connection, create_user_tables
with get_db_connection() as conn:
    create_user_tables(conn)
"
else
    echo "Skipping database creation."
fi

# Start the Python application
exec python app.py