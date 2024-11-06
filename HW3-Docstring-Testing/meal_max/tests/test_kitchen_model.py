from contextlib import contextmanager
import re
import sqlite3

import pytest

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
)

## FIXTURES ##

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("meal_max.models.kitchen__model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

## ADD and DELETE ##

def test_create_meal(mock_cursor):
    """Test creating a new meal in the table."""

    # Call the function to create a new meal
    create_meal(meal="Meal name", Cuisine="Meal cuisine", price=19.99, difficulty= "LOW")

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal name", " Meal cuisine", 19.99, "LOW")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with a duplicate meal, cuisine, price, and year (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.name, meals.cuisine, meals.price, meals.difficulty")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match= "Meal with meal 'Meal Name', cuisine 'Meal Cuisine', price 'Meal Price', and difficulty 'Meal Difficulty' already exists."):
        create_meal(meal="Meal Name", cuisine="Meal Cuisine", price=19.99, difficulty="LOW")

def test_create_meal_invalid_price():
    """Test error when trying to create a meal with an invalid duration (e.g., negative duration)"""

    # Attempt to create a meal with a negative meal price
    with pytest.raises(ValueError, match="Invalid meal price: -19.99 \(must be a positive integer\)."):
        create_meal(meal="Meal Name", cuisine="Meal Cuisine", price=-19.99, difficulty="LOW")

    # Attempt to create a meal with a non-integer price
    with pytest.raises(ValueError, match="Invalid meal price: invalid \(must be a positive integer\)."):
        create_meal(meal="Meal Name", cuisine="Meal Cuisine", price="invalid", difficulty="LOW")

def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with an invalid difficulty (e.g., not 'LOW', 'MED', or 'HIGH'.)."""

    # Attempt to create a meal with a difficulty being an integer
    with pytest.raises(ValueError, match="Invalid difficulty provided: 100 \(must be 'LOW', 'MED', or 'HIGH'.)."):
        create_meal(meal="Meal Name", cuisine="Meal Cuisine", price="invalid", difficulty=100)

    # Attempt to create a meal with a difficulty being a negative level
    with pytest.raises(ValueError, match="Invalid difficulty provided: -100 \('LOW', 'MED', or 'HIGH')."):
        create_meal(meal="Meal Name", cuisine="Meal Cuisine", price="invalid", difficulty=-100)
    
    # Attempt to create a meal with a difficulty being a a string other than 'LOW', 'MED', or 'HIGH'
    with pytest.raises(ValueError, match="Invalid difficulty provided: invalid \(must be an integer greater than or equal to 1900\)."):
        create_meal(meal="Meal Name", cuisine="Meal Cuisine", price="invalid", difficulty="invalid")

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the table by meal ID."""

    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_meal function
    delete_meal(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM Meal WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE Meal SET deleted = TRUE WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""

    # Simulate that no meal exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent meal
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""

    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 999 has already been deleted"):
        delete_meal(999)

## GET LEADERBOARD ##

def test_leaderboard_sorted_by_wins(mock_cursor):
    """Test that meals are sorted by wins."""
    
    # Simulate some rows returned from the database
    mock_cursor.fetchall.return_value = [
        (1, "Meal A", "Cuisine A", 10.0, "LOW", 5, 3, 0.6),
        (2, "Meal B", "Cuisine B", 12.5, "MED", 10, 7, 0.7),
        (3, "Meal C", "Cuisine C", 8.0, "HIGH", 8, 6, 0.75)
    ]
    
    # Call the function with sort_by="wins"
    result = get_leaderboard(sort_by="wins")
    
    # Expected result should be sorted by wins in descending order
    expected_result = [
        {'id': 2, 'meal': 'Meal B', 'cuisine': 'Cuisine B', 'price': 12.5,
         'difficulty': 'MED', 'battles': 10, 'wins': 7, 'win_pct': 70.0},
        {'id': 3, 'meal': 'Meal C', 'cuisine': 'Cuisine C', 'price': 8.0,
         'difficulty': 'HIGH', 'battles': 8, 'wins': 6, 'win_pct': 75.0},
        {'id': 1, 'meal': 'Meal A', 'cuisine': 'Cuisine A', 'price': 10.0,
         'difficulty': 'LOW', 'battles': 5, 'wins': 3, 'win_pct': 60.0}
    ]
    
    assert result == expected_result


def test_leaderboard_sorted_by_win_pct(mock_cursor):
    """Test that meals are sorted by win percentage."""
    
    # Simulate some rows returned from the database
    mock_cursor.fetchall.return_value = [
        (1, "Meal A", "Cuisine A", 10.0, "LOW", 5, 3, 0.6),
        (2, "Meal B", "Cuisine B", 12.5, "MED", 10, 7, 0.7),
        (3, "Meal C", "Cuisine C", 8.0, "HIGH", 8, 6, 0.75)
    ]
    
    # Call the function with sort_by="win_pct"
    result = get_leaderboard(sort_by="win_pct")
    
    # Expected result should be sorted by win percentage in descending order
    expected_result = [
        {'id': 3, 'meal': 'Meal C', 'cuisine': 'Cuisine C', 'price': 8.0,
         'difficulty': 'HIGH', 'battles': 8, 'wins': 6, 'win_pct': 75.0},
        {'id': 2, 'meal': 'Meal B', 'cuisine': 'Cuisine B', 'price': 12.5,
         'difficulty': 'MED', 'battles': 10, 'wins': 7, 'win_pct': 70.0},
        {'id': 1, 'meal': 'Meal A', 'cuisine': 'Cuisine A', 'price': 10.0,
         'difficulty': 'LOW', 'battles': 5, 'wins': 3, 'win_pct': 60.0}
    ]
    
    assert result == expected_result


def test_invalid_sort_by_parameter(mock_cursor):
    """Test that an invalid sort_by parameter raises a ValueError."""
    
    with pytest.raises(ValueError):
        get_leaderboard(sort_by="invalid_sort")


def test_empty_leaderboard(mock_cursor):
    """Test that an empty leaderboard returns an empty list."""
    
    # Simulate no rows returned from the database
    mock_cursor.fetchall.return_value = []
    
    # Call the function with default sort_by="wins"
    result = get_leaderboard()
    
    # Expected result should be an empty list
    assert result == []


## GET MEAL ##

def test_get_meal_by_id(mock_cursor):
    # Simulate that the song exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Meal Name", "Meal Cuisine", 19.99, "LOW")

    # Call the function and check the result
    result = get_meal_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Meal Name", "Meal Cuisine", 19.99, "LOW")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_id_bad_id(mock_cursor):
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_id_already_deleted(mock_cursor):
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 999 has already been deleted"):
        get_meal_by_id(999)

def test_get_meal_by_name_found(mock_cursor):
    """Test that a meal is successfully retrieved by name."""
    
    # Simulate that the meal exists (id = 1, meal_name = "Meal Name")
    mock_cursor.fetchone.return_value = (1, "Meal Name", "Cuisine", 15.99, "MED", False)
    
    # Call the function and check the result
    result = get_meal_by_name("Meal Name")
    
    # Expected result based on the simulated fetchone return value
    expected_result = Meal(id=1, meal="Meal Name", cuisine="Cuisine", price=15.99, difficulty="MED")
    
    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"
    
    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    
    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]
    
    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal Name",)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_meal_by_name_deleted(mock_cursor):
    """Test that a ValueError is raised when trying to retrieve a deleted meal."""
    
    # Simulate that the meal exists but is marked as deleted (id = 1)
    mock_cursor.fetchone.return_value = (1, "Meal Name", "Cuisine", 15.99, "MED", True)
    
    # Expect a ValueError when attempting to retrieve a deleted meal
    with pytest.raises(ValueError, match="Meal with name Meal Name has been deleted"):
        get_meal_by_name("Meal Name")
    
    # Ensure that the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    
    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]
    
    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal Name",)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_meal_by_name_not_found(mock_cursor):
    """Test that a ValueError is raised when trying to retrieve a non-existent meal."""
    
    # Simulate that no meal exists with the given name (fetchone returns None)
    mock_cursor.fetchone.return_value = None
    
    # Expect a ValueError when attempting to retrieve a non-existent meal
    with pytest.raises(ValueError, match="Meal with name Meal Name not found"):
        get_meal_by_name("Meal Name")
    
    # Ensure that the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    
    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]
    
    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Meal Name",)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_meal_stats_win(mock_cursor):
    """Test updating meal stats with a win."""

    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_meal_stats function with a sample meal ID and result 'win'
    meal_id = 1
    update_meal_stats(meal_id, 'win')

    # Normalize the expected SQL query for updating stats with a win
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (meal ID)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_update_meal_stats_loss(mock_cursor):
    """Test updating meal stats with a loss."""

    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_meal_stats function with a sample meal ID and result 'loss'
    meal_id = 1
    update_meal_stats(meal_id, 'loss')

    # Normalize the expected SQL query for updating stats with a loss
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (meal ID)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_update_meal_stats_deleted_meal(mock_cursor):
    """Test error when trying to update stats for a deleted meal."""

    # Simulate that the meal exists but is marked as deleted (id = 1)
    mock_cursor.fetchone.return_value = [True]

    # Expect a ValueError when attempting to update a deleted meal
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, 'win')

    # Ensure that no SQL query for updating stats was executed after detecting deletion
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM meals WHERE id = ?", (1,))


def test_update_meal_stats_invalid_result(mock_cursor):
    """Test error when an invalid result is provided."""

    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Expect a ValueError when an invalid result ('invalid') is passed to update_meal_stats
    with pytest.raises(ValueError, match="Invalid result: invalid. Expected 'win' or 'loss'."):
        update_meal_stats(1, 'invalid')

