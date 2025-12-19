"""
Evaluation metrics for meal planner algorithms.

Metrics:
1. Constraint satisfaction rate: % of hard constraints satisfied
2. Calorie error: Absolute error from target
3. Protein error: Deficit from minimum (0 if meeting requirement)
4. Diversity score: Ingredient variety (0-100)
5. Preference score: User preference matching (0-100)
6. Balance score: Macronutrient ratio quality (0-100)
"""

from constraints import count_satisfied_constraints
from heuristics import calculate_diversity_score, calculate_preference_score


def calculate_constraint_satisfaction_rate(plan, user):
    """
    Calculate percentage of constraints satisfied.

    Args:
        plan: List of Recipe objects
        user: User object

    Returns:
        float: Constraint satisfaction rate (0-100)
    """
    if not plan:
        return 0.0

    satisfied, total = count_satisfied_constraints(plan, user)
    return (satisfied / total) * 100 if total > 0 else 0.0


def calculate_calorie_error(plan, user):
    """
    Calculate absolute calorie error from target.

    Args:
        plan: List of Recipe objects
        user: User object

    Returns:
        float: Absolute calorie error
    """
    if not plan:
        return float('inf')

    total_calories = sum(recipe.calories for recipe in plan)
    return abs(total_calories - user.calorie_target)


def calculate_protein_error(plan, user):
    """
    Calculate protein deficit (0 if meeting requirement).

    Args:
        plan: List of Recipe objects
        user: User object

    Returns:
        float: Protein deficit (0 if >= minimum)
    """
    if not plan:
        return float('inf')

    total_protein = sum(recipe.protein for recipe in plan)
    return max(0, user.protein_min - total_protein)


def calculate_balance_score(plan):
    """
    Calculate macronutrient balance score (0-100).
    Based on healthy macro ratios: Protein 25-35%, Carbs 45-55%, Fat 20-30%

    Args:
        plan: List of Recipe objects

    Returns:
        float: Balance score (0-100)
    """
    if not plan:
        return 0.0

    # Calculate total macros
    total_protein = sum(recipe.protein for recipe in plan)
    total_carbs = sum(recipe.carbs for recipe in plan)
    total_fat = sum(recipe.fat for recipe in plan)

    # Calculate calories from each macro (protein: 4 cal/g, carbs: 4 cal/g, fat: 9 cal/g)
    protein_cals = total_protein * 4
    carbs_cals = total_carbs * 4
    fat_cals = total_fat * 9
    total_cals = protein_cals + carbs_cals + fat_cals

    if total_cals == 0:
        return 0.0

    # Calculate percentages
    protein_pct = (protein_cals / total_cals) * 100
    carbs_pct = (carbs_cals / total_cals) * 100
    fat_pct = (fat_cals / total_cals) * 100

    # Ideal ranges
    protein_ideal = (25, 35)
    carbs_ideal = (45, 55)
    fat_ideal = (20, 30)

    # Calculate deviations from ideal ranges
    protein_dev = 0 if protein_ideal[0] <= protein_pct <= protein_ideal[1] else min(
        abs(protein_pct - protein_ideal[0]), abs(protein_pct - protein_ideal[1])
    )
    carbs_dev = 0 if carbs_ideal[0] <= carbs_pct <= carbs_ideal[1] else min(
        abs(carbs_pct - carbs_ideal[0]), abs(carbs_pct - carbs_ideal[1])
    )
    fat_dev = 0 if fat_ideal[0] <= fat_pct <= fat_ideal[1] else min(
        abs(fat_pct - fat_ideal[0]), abs(fat_pct - fat_ideal[1])
    )

    # Total deviation (lower is better)
    total_deviation = protein_dev + carbs_dev + fat_dev

    # Convert to score (0-100, higher is better)
    # Max reasonable deviation: ~60 (20% off on each macro)
    score = max(0, 100 - (total_deviation / 60 * 100))
    return score


def evaluate_plan(plan, user):
    """
    Calculate all evaluation metrics for a meal plan.

    Args:
        plan: List of Recipe objects
        user: User object

    Returns:
        dict: Dictionary of all metrics
    """
    if not plan:
        return {
            'constraint_satisfaction_rate': 0.0,
            'calorie_error': float('inf'),
            'protein_error': float('inf'),
            'diversity_score': 0.0,
            'preference_score': 0.0,
            'balance_score': 0.0,
            'total_calories': 0.0,
            'total_protein': 0.0,
            'success': False
        }

    # Calculate all metrics
    constraint_sat = calculate_constraint_satisfaction_rate(plan, user)
    calorie_error = calculate_calorie_error(plan, user)
    protein_error = calculate_protein_error(plan, user)
    diversity = calculate_diversity_score(plan)
    preference = calculate_preference_score(plan, user)
    balance = calculate_balance_score(plan)

    # Calculate totals
    total_calories = sum(recipe.calories for recipe in plan)
    total_protein = sum(recipe.protein for recipe in plan)

    # Success criteria: >80% constraint satisfaction, <150 cal error, >40 diversity
    success = (constraint_sat >= 80 and calorie_error <= 150 and diversity >= 40)

    return {
        'constraint_satisfaction_rate': constraint_sat,
        'calorie_error': calorie_error,
        'protein_error': protein_error,
        'diversity_score': diversity,
        'preference_score': preference,
        'balance_score': balance,
        'total_calories': total_calories,
        'total_protein': total_protein,
        'success': success
    }


def print_plan_evaluation(plan, user, algorithm_name=""):
    """
    Pretty print evaluation metrics for a meal plan.

    Args:
        plan: List of Recipe objects
        user: User object
        algorithm_name: Name of algorithm (for display)
    """
    if algorithm_name:
        print(f"\n{'=' * 60}")
        print(f"Evaluation: {algorithm_name}")
        print(f"{'=' * 60}")

    if not plan:
        print("No plan generated (failed to find solution)")
        return

    print(f"\nMeal Plan for {user.name}:")
    for i, recipe in enumerate(plan, 1):
        print(f"  Meal {i}: {recipe.name} ({recipe.calories}cal, {recipe.protein}g protein)")

    metrics = evaluate_plan(plan, user)

    print(f"\nNutritional Totals:")
    print(f"  Total Calories: {metrics['total_calories']:.1f} (target: {user.calorie_target})")
    print(f"  Total Protein: {metrics['total_protein']:.1f}g (minimum: {user.protein_min}g)")

    print(f"\nMetrics:")
    print(f"  Constraint Satisfaction: {metrics['constraint_satisfaction_rate']:.1f}%")
    print(f"  Calorie Error: {metrics['calorie_error']:.1f} cal")
    print(f"  Protein Error: {metrics['protein_error']:.1f} g")
    print(f"  Diversity Score: {metrics['diversity_score']:.1f}/100")
    print(f"  Preference Score: {metrics['preference_score']:.1f}/100")
    print(f"  Balance Score: {metrics['balance_score']:.1f}/100")

    print(f"\nSuccess: {'YES' if metrics['success'] else 'NO'}")


if __name__ == '__main__':
    # Test metrics
    from data_loader import load_recipes, load_users
    from constraints import filter_by_diet_and_allergens

    recipes = load_recipes()
    users = load_users()

    test_user = users[0]
    available = filter_by_diet_and_allergens(recipes, test_user)

    # Create a sample plan
    sample_plan = available[:3]

    print_plan_evaluation(sample_plan, test_user, "Sample Plan")
