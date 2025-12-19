"""
Heuristic functions for greedy CSP meal planner.
Lower score = more promising candidate (better fit for current partial plan).
"""


def calculate_calorie_distance(plan, user):
    """
    Calculate absolute distance from target calories.

    Args:
        plan: List of Recipe objects (partial or complete)
        user: User object

    Returns:
        float: Absolute calorie error (lower is better)
    """
    total_calories = sum(recipe.calories for recipe in plan)
    return abs(total_calories - user.calorie_target)


def calculate_protein_deficit(plan, user):
    """
    Calculate protein deficit (how far below minimum).

    Args:
        plan: List of Recipe objects (partial or complete)
        user: User object

    Returns:
        float: Protein deficit (0 if meeting requirement, positive if below)
    """
    total_protein = sum(recipe.protein for recipe in plan)
    return max(0, user.protein_min - total_protein)


def count_ingredient_overlaps(plan):
    """
    Count how many ingredients appear in multiple meals (diversity penalty).

    Args:
        plan: List of Recipe objects

    Returns:
        int: Number of overlapping ingredients
    """
    if len(plan) < 2:
        return 0

    # Count occurrences of each ingredient
    ingredient_counts = {}
    for recipe in plan:
        for ingredient in recipe.ingredients:
            ingredient_counts[ingredient] = ingredient_counts.get(ingredient, 0) + 1

    # Count ingredients that appear in multiple meals
    overlaps = sum(1 for count in ingredient_counts.values() if count > 1)
    return overlaps


def calculate_diversity_score(plan):
    """
    Calculate ingredient diversity score (0-100 scale).
    Higher score = more diverse ingredients and dietary tags.

    Args:
        plan: List of Recipe objects

    Returns:
        float: Diversity score (0-100)
    """
    if not plan:
        return 0

    # Unique ingredients
    all_ingredients = set()
    for recipe in plan:
        all_ingredients.update(recipe.ingredients)
    unique_ingredient_count = len(all_ingredients)

    # Unique tags
    all_tags = set()
    for recipe in plan:
        all_tags.update(recipe.tags)
    unique_tag_count = len(all_tags)

    # Ingredient overlap penalty
    total_ingredients = sum(len(recipe.ingredients) for recipe in plan)
    overlap_ratio = 1.0 - (unique_ingredient_count / total_ingredients if total_ingredients > 0 else 0)

    # Combine metrics (weighted)
    # More unique ingredients and tags = higher score
    # Less overlap = higher score
    diversity = (unique_ingredient_count * 2 +  # Weight ingredients more
                 unique_tag_count * 1 -
                 overlap_ratio * 20)

    # Normalize to 0-100 scale (heuristic normalization)
    # Typical range: 10-40 for 3 meals
    normalized = min(100, max(0, diversity * 2))
    return normalized


def calculate_preference_score(plan, user):
    """
    Calculate preference matching score (0-100 scale).
    Higher score = more user preferences matched.

    Args:
        plan: List of Recipe objects
        user: User object

    Returns:
        float: Preference score (0-100)
    """
    if not user.preferences or not plan:
        return 50  # Neutral score if no preferences

    # Count how many preferred ingredients appear in plan
    plan_ingredients = set()
    for recipe in plan:
        plan_ingredients.update(recipe.ingredients)

    matches = len(user.preferences & plan_ingredients)
    total_preferences = len(user.preferences)

    # Percentage of preferences matched
    match_percentage = (matches / total_preferences) * 100 if total_preferences > 0 else 50
    return match_percentage


def combined_heuristic(partial_plan, candidate_recipe, user, num_meals=3):
    """
    Combined heuristic function for greedy recipe selection.
    Lower score = more promising candidate.

    Considers:
    1. Calorie distance from target
    2. Protein deficit
    3. Ingredient overlap penalty
    4. Diversity penalty
    5. Preference penalty

    Args:
        partial_plan: List of Recipe objects (current partial assignment)
        candidate_recipe: Recipe object being evaluated
        user: User object
        num_meals: Total number of meals in complete plan

    Returns:
        float: Heuristic score (lower is better)
    """
    # Create hypothetical plan with candidate
    hypothetical_plan = partial_plan + [candidate_recipe]

    # Calculate individual components
    calorie_error = calculate_calorie_distance(hypothetical_plan, user)
    protein_deficit = calculate_protein_deficit(hypothetical_plan, user)
    overlap_penalty = count_ingredient_overlaps(hypothetical_plan) * 10
    diversity_score = calculate_diversity_score(hypothetical_plan)
    preference_score = calculate_preference_score(hypothetical_plan, user)

    # Weights for different components
    w_calorie = 1.0
    w_protein = 2.0  # Protein deficit is critical
    w_overlap = 1.0
    w_diversity = 0.6
    w_preference = 0.4

    # Combined score (lower is better)
    score = (w_calorie * calorie_error +
             w_protein * protein_deficit +
             w_overlap * overlap_penalty +
             w_diversity * (100 - diversity_score) +
             w_preference * (100 - preference_score))

    # Adjust for plan progress
    # As we fill slots, calorie accuracy becomes more important
    progress = len(hypothetical_plan) / num_meals
    if progress >= 0.67:  # Last meal
        score += abs(calorie_error) * 0.5  # Extra penalty for calorie mismatch

    return score


def greedy_recipe_selector(available_recipes, partial_plan, user, top_k=15, num_meals=3):
    """
    Select top-k most promising recipes using greedy heuristic.

    Args:
        available_recipes: List of Recipe objects (already filtered by diet/allergens)
        partial_plan: List of Recipe objects (current partial assignment)
        user: User object
        top_k: Number of top candidates to return
        num_meals: Total number of meals in complete plan

    Returns:
        List of top-k Recipe objects sorted by heuristic score (best first)
    """
    # Calculate heuristic score for each candidate
    scored_recipes = []
    for recipe in available_recipes:
        score = combined_heuristic(partial_plan, recipe, user, num_meals)
        scored_recipes.append((score, recipe))

    # Sort by score (ascending - lower is better)
    scored_recipes.sort(key=lambda x: x[0])

    # Return top-k recipes
    return [recipe for score, recipe in scored_recipes[:top_k]]


if __name__ == '__main__':
    # Test heuristic functions
    from data_loader import load_recipes, load_users
    from constraints import filter_by_diet_and_allergens

    recipes = load_recipes()
    users = load_users()

    test_user = users[0]  # Alex - high-protein
    print(f"Testing heuristics for user: {test_user}")

    # Filter available recipes
    available = filter_by_diet_and_allergens(recipes, test_user)
    print(f"Available recipes: {len(available)}")

    # Test greedy selection for first meal
    print("\nTop 5 candidates for first meal:")
    top_candidates = greedy_recipe_selector(available, [], test_user, top_k=5)
    for i, recipe in enumerate(top_candidates, 1):
        score = combined_heuristic([], recipe, test_user)
        print(f"{i}. {recipe.name} (score: {score:.2f}, {recipe.calories}cal, {recipe.protein}g protein)")

    # Test with partial plan
    partial = [top_candidates[0]]
    print(f"\nPartial plan: {[r.name for r in partial]}")
    print("Top 5 candidates for second meal:")
    top_candidates_2 = greedy_recipe_selector(available, partial, test_user, top_k=5)
    for i, recipe in enumerate(top_candidates_2, 1):
        score = combined_heuristic(partial, recipe, test_user)
        print(f"{i}. {recipe.name} (score: {score:.2f}, {recipe.calories}cal, {recipe.protein}g protein)")
