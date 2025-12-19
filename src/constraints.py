"""
Constraint checking module for CSP meal planner.
Handles both hard constraints (must be satisfied) and soft constraints (preferences).
"""


def is_diet_compatible(recipe, user):
    """
    Check if a recipe is compatible with user's diet type (hard constraint).

    Diet hierarchy:
    - vegan: only vegan recipes
    - vegetarian: vegan + vegetarian recipes
    - pescatarian: vegan + vegetarian + pescatarian recipes
    - high-protein: recipes with >= 25g protein
    - keto: recipes tagged as keto
    - gluten-free: recipes tagged as gluten-free
    - balanced: all recipes (no restriction)

    Args:
        recipe: Recipe object
        user: User object

    Returns:
        bool: True if recipe matches user's diet type
    """
    diet_type = user.diet_type

    if diet_type == 'vegan':
        return recipe.has_tag('vegan')

    elif diet_type == 'vegetarian':
        # Vegetarian accepts vegan and vegetarian recipes
        return recipe.has_tag('vegan') or recipe.has_tag('vegetarian')

    elif diet_type == 'pescatarian':
        # Pescatarian accepts vegan, vegetarian, and pescatarian recipes
        return (recipe.has_tag('vegan') or
                recipe.has_tag('vegetarian') or
                recipe.has_tag('pescatarian'))

    elif diet_type == 'high-protein':
        # High-protein requires >= 25g protein per meal
        return recipe.protein >= 25

    elif diet_type == 'keto':
        return recipe.has_tag('keto')

    elif diet_type == 'gluten-free':
        return recipe.has_tag('gluten-free')

    elif diet_type == 'balanced':
        # Balanced diet accepts all recipes
        return True

    else:
        # Unknown diet type - accept all (defensive)
        return True


def has_allergen(recipe, user):
    """
    Check if recipe contains any of user's allergens (hard constraint).

    Args:
        recipe: Recipe object
        user: User object

    Returns:
        bool: True if recipe contains allergens (should be excluded)
    """
    for allergen in user.allergens:
        if recipe.contains_allergen(allergen):
            return True
    return False


def check_calorie_constraint(plan, user, tolerance=300):
    """
    Check if meal plan's total calories are within target range (hard constraint).

    Args:
        plan: List of Recipe objects
        user: User object
        tolerance: Calorie tolerance in either direction (default: 300)

    Returns:
        bool: True if total calories within target ± tolerance
    """
    total_calories = sum(recipe.calories for recipe in plan)
    lower_bound = user.calorie_target - tolerance
    upper_bound = user.calorie_target + tolerance
    return lower_bound <= total_calories <= upper_bound


def check_protein_constraint(plan, user):
    """
    Check if meal plan meets minimum protein requirement (hard constraint).

    Args:
        plan: List of Recipe objects
        user: User object

    Returns:
        bool: True if total protein >= user's minimum
    """
    total_protein = sum(recipe.protein for recipe in plan)
    return total_protein >= user.protein_min


def violates_hard_constraints(plan, user, calorie_tolerance=300):
    """
    Check if a complete meal plan violates any hard constraints.

    Hard constraints:
    1. Diet compatibility (checked during filtering)
    2. Allergen avoidance (checked during filtering)
    3. Calorie range: total within target ± tolerance
    4. Minimum protein: total >= user.protein_min

    Args:
        plan: List of Recipe objects (complete assignment)
        user: User object
        calorie_tolerance: Calorie tolerance (default: 300)

    Returns:
        bool: True if any hard constraint is violated
    """
    # Check calorie constraint
    if not check_calorie_constraint(plan, user, calorie_tolerance):
        return True

    # Check protein constraint
    if not check_protein_constraint(plan, user):
        return True

    return False


def filter_by_diet_and_allergens(recipes, user, exclude_ids=None):
    """
    Pre-filter recipes by diet type and allergens (domain reduction for CSP).

    Args:
        recipes: List of Recipe objects
        user: User object
        exclude_ids: Set of recipe IDs to exclude (already used in plan)

    Returns:
        List of Recipe objects that pass hard constraints
    """
    if exclude_ids is None:
        exclude_ids = set()

    filtered = []
    for recipe in recipes:
        # Skip already used recipes
        if recipe.id in exclude_ids:
            continue

        # Check diet compatibility
        if not is_diet_compatible(recipe, user):
            continue

        # Check allergens
        if has_allergen(recipe, user):
            continue

        filtered.append(recipe)

    return filtered


def count_satisfied_constraints(plan, user):
    """
    Count how many constraints are satisfied (for evaluation metrics).

    Returns a tuple: (satisfied_count, total_count)
    """
    satisfied = 0
    total = 0

    # Diet compatibility (per recipe)
    for recipe in plan:
        total += 1
        if is_diet_compatible(recipe, user):
            satisfied += 1

    # Allergen avoidance (per recipe)
    for recipe in plan:
        total += 1
        if not has_allergen(recipe, user):
            satisfied += 1

    # Calorie constraint (plan-level)
    total += 1
    if check_calorie_constraint(plan, user):
        satisfied += 1

    # Protein constraint (plan-level)
    total += 1
    if check_protein_constraint(plan, user):
        satisfied += 1

    return satisfied, total


if __name__ == '__main__':
    # Test constraint checking
    from data_loader import load_recipes, load_users

    recipes = load_recipes()
    users = load_users()

    test_user = users[0]  # Alex - high-protein, no peanuts
    print(f"Testing constraints for user: {test_user}")

    # Test diet filtering
    compatible = [r for r in recipes if is_diet_compatible(r, test_user)]
    print(f"\nDiet-compatible recipes: {len(compatible)}/{len(recipes)}")

    # Test allergen filtering
    safe = [r for r in compatible if not has_allergen(r, test_user)]
    print(f"Safe recipes (no allergens): {len(safe)}/{len(compatible)}")

    # Create a sample plan
    sample_plan = safe[:3]
    print(f"\nSample plan: {[r.name for r in sample_plan]}")
    print(f"Total calories: {sum(r.calories for r in sample_plan)}")
    print(f"Total protein: {sum(r.protein for r in sample_plan)}")
    print(f"Violates hard constraints: {violates_hard_constraints(sample_plan, test_user)}")
