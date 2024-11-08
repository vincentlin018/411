import pytest
from contextlib import contextmanager
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
    return Meal(1, 'Meal 1', 'Cuisine 1', 20.00, 'MED')
    #battle score should be = 178

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Meal 2', 'Cuisine 2', 10.00, 'HIGH')
    #battle score should be =  89

@pytest.fixture
def sample_battle(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]




##################################################
# Battle Test Cases
##################################################
def test_battle(battle_model, sample_battle, mock_update_meal_stats, mocker):
    """Test battle of 2 meals"""
    battle_model.combatants.extend(sample_battle)
    
    mock_get_random = mocker.patch("meal_max.models.battle_model.get_random", return_value=0.42)
    
    battle_winner = battle_model.battle()
    assert len(battle_model.combatants) == 1

    #delta=0.02, random_number=0.42, sample_meal1 should win
    assert battle_winner==sample_battle[0].meal

    #check if update_meal_stats was called for both
    mock_update_meal_stats.assert_any_call(1, 'win') 
    mock_update_meal_stats.assert_any_call(2, 'loss')


def test_battle_zero_meals(battle_model):
    """Test battle with empty list, should return ValueError"""

    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

def test_battle_one_meal(battle_model, sample_meal1):
    """Test battle with only one meal, should return ValueError"""

    battle_model.prep_combatant(sample_meal1)

    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

##################################################
# Add Meal Management Test Cases
##################################################

def test_add_meal_to_battle(battle_model, sample_meal1):
    """Test adding a meal to the battle."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Meal 1'

def test_extra_meals_to_battle(battle_model, sample_meal1, sample_meal2):
    """Test error when adding a duplicate meal to the battle by ID."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    #with pytest.raises(ValueError, match="Meal with ID 1 already exists in the battle"):
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
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
    assert test_score == (sample_meal1.price*len(sample_meal1.cuisine)) - 2