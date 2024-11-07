import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stats function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")

"""Fixtures providing sample meals for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(1, 'Meal 1', 'Cuisine 1', 20.00, 'HIGH')

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Meal 2', 'Cuisine 2', 10.00, 'LOW')

@pytest.fixture
def sample_battle(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]


##################################################
# Add Meal Management Test Cases
##################################################

def test_add_meal_to_battle(battle_model, sample_meal1):
    """Test adding a meal to the battle."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Meal 1'

def test_add_duplicate_meal_to_battle(battle_model, sample_meal1):
    """Test error when adding a duplicate meal to the battle by ID."""
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Meal with ID 1 already exists in the battle"):
        battle_model.prep_combatant(sample_meal1)

##################################################
# Remove Meal Management Test Cases
##################################################

def test_clear_battle(battle_model, sample_meal1):
    """Test clearing the entire playlist."""
    battle_model.prep_combatant(sample_meal1)

    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Battle should be empty after clearing"

def test_clear_battle_empty_battle(battle_model):
    """Test clearing the entire battle when it's empty."""
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Battle should be empty after clearing"

##################################################
# Meal Retrieval Test Cases
##################################################

def test_get_combatants(battle_model, sample_battle):
    """Test successfully retrieving all meals from the battle."""
    battle_model.combatants.extend(sample_battle)

    all_meals = battle_model.get_combatants()
    assert len(all_meals) == 2
    assert all_meals[0].id == 1
    assert all_meals[1].id == 2

def test_get_battle_score(battle_model, sample_meal1):
    """Test successfully calculating battle score"""
    test_score = battle_model.get_battle_score(sample_meal1)
    assert test_score == (sample_meal1.price*len(sample_meal1.cuisine)) - 1