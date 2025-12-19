"""
Data loading and preprocessing module for meal planner.
Handles loading recipes and users, converting strings to sets for efficient processing.
"""

import pandas as pd
import json
from pathlib import Path


class Recipe:
    """Represents a single recipe with nutritional information and metadata."""

    def __init__(self, recipe_id, name, calories, protein, carbs, fat, ingredients, tags):
        self.id = recipe_id
        self.name = name
        self.calories = float(calories)
        self.protein = float(protein)
        self.carbs = float(carbs)
        self.fat = float(fat)
        # Convert comma-separated string to set of lowercase ingredients
        self.ingredients = set(ing.strip().lower() for ing in ingredients.split(','))
        # Convert comma-separated string to set of lowercase tags
        self.tags = set(tag.strip().lower() for tag in tags.split(','))

    def __repr__(self):
        return f"Recipe({self.id}, {self.name}, {self.calories}cal, {self.protein}g protein)"

    def has_tag(self, tag):
        """Check if recipe has a specific dietary tag."""
        return tag.lower() in self.tags

    def contains_allergen(self, allergen):
        """Check if recipe contains an allergen (case-insensitive partial matching)."""
        allergen_lower = allergen.lower()
        for ingredient in self.ingredients:
            if allergen_lower in ingredient:
                return True
        return False


class User:
    """Represents a user with dietary constraints and preferences."""

    def __init__(self, user_id, name, diet_type, calorie_target, protein_min, allergens, preferences):
        self.id = user_id
        self.name = name
        self.diet_type = diet_type.lower()
        self.calorie_target = float(calorie_target)
        self.protein_min = float(protein_min)
        # Convert allergens to lowercase set
        self.allergens = set(allergen.lower() for allergen in allergens)
        # Convert preferences to lowercase set
        self.preferences = set(pref.lower() for pref in preferences)

    def __repr__(self):
        return f"User({self.name}, {self.diet_type}, {self.calorie_target}cal, {self.protein_min}g protein)"


def load_recipes(filepath='data/recipes.csv'):
    """
    Load recipes from CSV file and convert to Recipe objects.

    Args:
        filepath: Path to recipes CSV file

    Returns:
        List of Recipe objects
    """
    # Support both absolute and relative paths
    if not Path(filepath).exists():
        # Try relative to project root
        filepath = Path(__file__).parent.parent / filepath

    df = pd.read_csv(filepath)

    recipes = []
    for _, row in df.iterrows():
        recipe = Recipe(
            recipe_id=row['id'],
            name=row['name'],
            calories=row['calories'],
            protein=row['protein'],
            carbs=row['carbs'],
            fat=row['fat'],
            ingredients=row['ingredients'],
            tags=row['tags']
        )
        recipes.append(recipe)

    return recipes


def load_users(filepath='data/test_users.json'):
    """
    Load test users from JSON file and convert to User objects.

    Args:
        filepath: Path to users JSON file

    Returns:
        List of User objects
    """
    # Support both absolute and relative paths
    if not Path(filepath).exists():
        # Try relative to project root
        filepath = Path(__file__).parent.parent / filepath

    with open(filepath, 'r') as f:
        users_data = json.load(f)

    users = []
    for user_data in users_data:
        user = User(
            user_id=user_data['id'],
            name=user_data['name'],
            diet_type=user_data['diet_type'],
            calorie_target=user_data['calorie_target'],
            protein_min=user_data['protein_min'],
            allergens=user_data['allergens'],
            preferences=user_data['preferences']
        )
        users.append(user)

    return users


if __name__ == '__main__':
    # Test loading
    recipes = load_recipes()
    print(f"Loaded {len(recipes)} recipes")
    print(f"Sample recipe: {recipes[0]}")
    print(f"  Ingredients: {recipes[0].ingredients}")
    print(f"  Tags: {recipes[0].tags}")

    users = load_users()
    print(f"\nLoaded {len(users)} users")
    print(f"Sample user: {users[0]}")
    print(f"  Allergens: {users[0].allergens}")
    print(f"  Preferences: {users[0].preferences}")
