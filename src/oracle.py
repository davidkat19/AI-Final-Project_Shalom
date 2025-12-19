"""
Oracle algorithm: Exhaustive search with optimal scoring.

Purpose: Establishes upper bound performance (theoretical maximum with perfect information).
Algorithm: Tests all valid combinations and selects the best using optimal scoring function.
"""

from itertools import combinations
from constraints import filter_by_diet_and_allergens, violates_hard_constraints


def oracle_scoring_function(plan, user):
    """
    Hand-crafted optimal scoring function for oracle.
    Lower score = better plan.

    Considers:
    - Calorie accuracy (squared error for precision)
    - Protein surplus (meeting requirement with some buffer)
    - Ingredient diversity
    - Preference matching

    Args:
        plan: List of Recipe objects
        user: User object

    Returns:
        float: Quality score (lower is better)
    """
    # Calorie error (squared for precision)
    total_calories = sum(recipe.calories for recipe in plan)
    calorie_error = (total_calories - user.calorie_target) ** 2

    # Protein (prefer meeting requirement with slight surplus)
    total_protein = sum(recipe.protein for recipe in plan)
    protein_score = abs(total_protein - user.protein_min - 10) ** 2  # Target: min + 10g buffer

    # Diversity: count unique ingredients
    all_ingredients = set()
    for recipe in plan:
        all_ingredients.update(recipe.ingredients)
    diversity_penalty = -len(all_ingredients) * 5  # Negative = reward

    # Preference matching
    plan_ingredients = set()
    for recipe in plan:
        plan_ingredients.update(recipe.ingredients)
    preferences_matched = len(user.preferences & plan_ingredients)
    preference_penalty = -preferences_matched * 20  # Negative = reward

    # Combined score (lower is better)
    score = (calorie_error * 0.1 +
             protein_score * 0.2 +
             diversity_penalty +
             preference_penalty)

    return score


def oracle_planner(recipes, user, num_meals=3, max_combinations=50000):
    """
    Oracle algorithm: Exhaustive search with optimal scoring.

    Approach:
    1. Filter recipes by diet and allergens
    2. Generate all possible combinations of num_meals
    3. Filter by hard constraints (calories, protein)
    4. Score all valid plans using optimal function
    5. Return best plan

    WARNING: Computationally expensive for large recipe sets.
    Limited to max_combinations to prevent excessive runtime.

    Args:
        recipes: List of Recipe objects
        user: User object
        num_meals: Number of meals to select (default: 3)
        max_combinations: Maximum combinations to evaluate (default: 50000)

    Returns:
        List of Recipe objects (best meal plan) or None if no solution found
    """
    # Pre-filter by diet and allergens
    available = filter_by_diet_and_allergens(recipes, user)

    if len(available) < num_meals:
        return None

    # Generate all possible combinations
    all_combinations = combinations(available, num_meals)

    best_plan = None
    best_score = float('inf')
    evaluated = 0

    for plan in all_combinations:
        plan = list(plan)

        # Check hard constraints
        if violates_hard_constraints(plan, user):
            continue

        # Score this valid plan
        score = oracle_scoring_function(plan, user)

        if score < best_score:
            best_score = score
            best_plan = plan

        evaluated += 1

        # Limit evaluation for performance
        if evaluated >= max_combinations:
            break

    return best_plan


if __name__ == '__main__':
    # Test oracle algorithm
    from data_loader import load_recipes, load_users
    from metrics import print_plan_evaluation
    import time

    recipes = load_recipes()
    users = load_users()

    print("Testing Oracle Planner (Exhaustive Search)")
    print("=" * 60)
    print("WARNING: This may take some time for large recipe sets")

    for user in users[:2]:  # Test first 2 users
        print(f"\nUser: {user.name} ({user.diet_type}, {user.calorie_target}cal, {user.protein_min}g protein)")

        start_time = time.time()
        plan = oracle_planner(recipes, user, max_combinations=10000)  # Limited for testing
        end_time = time.time()

        runtime_ms = (end_time - start_time) * 1000

        if plan:
            print(f"Found plan in {runtime_ms:.2f}ms")
            print_plan_evaluation(plan, user)
        else:
            print(f"Failed to find plan (runtime: {runtime_ms:.2f}ms)")
