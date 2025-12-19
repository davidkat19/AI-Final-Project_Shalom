"""
Baseline algorithm: Random meal sampling with basic calorie filtering.

Purpose: Establishes lower bound performance (minimum expected).
Algorithm: Random selection filtered only by calorie limits.
"""

import random
from constraints import filter_by_diet_and_allergens


def random_baseline_planner(recipes, user, num_meals=3, max_attempts=1000, seed=42):
    """
    Baseline algorithm: Random meal selection with basic calorie constraint.

    Approach:
    1. Filter recipes by diet and allergens
    2. Randomly sample 3 meals
    3. Check if total calories are within reasonable range
    4. Repeat until valid plan found or max attempts reached

    Args:
        recipes: List of Recipe objects
        user: User object
        num_meals: Number of meals to select (default: 3)
        max_attempts: Maximum random attempts (default: 1000)
        seed: Random seed for reproducibility

    Returns:
        List of Recipe objects (meal plan) or None if no solution found
    """
    random.seed(seed)

    # Pre-filter by diet and allergens (hard constraints)
    available = filter_by_diet_and_allergens(recipes, user)

    if len(available) < num_meals:
        # Not enough recipes to create a plan
        return None

    # Try random sampling
    for attempt in range(max_attempts):
        # Randomly sample num_meals recipes without replacement
        plan = random.sample(available, num_meals)

        # Check basic calorie constraint (wide tolerance)
        total_calories = sum(recipe.calories for recipe in plan)
        calorie_tolerance = 300  # Same as other algorithms

        if abs(total_calories - user.calorie_target) <= calorie_tolerance:
            # Check protein constraint
            total_protein = sum(recipe.protein for recipe in plan)
            if total_protein >= user.protein_min:
                # Found a valid plan
                return plan

    # Failed to find a plan after max_attempts
    return None


if __name__ == '__main__':
    # Test baseline algorithm
    from data_loader import load_recipes, load_users
    from metrics import print_plan_evaluation
    import time

    recipes = load_recipes()
    users = load_users()

    print("Testing Random Baseline Planner")
    print("=" * 60)

    for user in users[:3]:  # Test first 3 users
        print(f"\nUser: {user.name} ({user.diet_type}, {user.calorie_target}cal, {user.protein_min}g protein)")

        start_time = time.time()
        plan = random_baseline_planner(recipes, user)
        end_time = time.time()

        runtime_ms = (end_time - start_time) * 1000

        if plan:
            print(f"Found plan in {runtime_ms:.2f}ms")
            print_plan_evaluation(plan, user)
        else:
            print(f"Failed to find plan (runtime: {runtime_ms:.2f}ms)")
