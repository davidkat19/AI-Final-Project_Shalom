"""
Main CSP Meal Planner with Greedy Heuristic Backtracking Search.

CSP Formulation:
- Variables: 3 meal slots (slot_1, slot_2, slot_3)
- Domain: All recipes matching user's diet type and allergen constraints
- Hard Constraints:
    * Diet compatibility: each recipe must match user's diet type
    * Allergen avoidance: no recipe contains user's allergens
    * Calorie range: total_calories within target ± 300
    * Minimum protein: total_protein >= user.protein_min
- Soft Constraints (via heuristic):
    * Ingredient diversity: minimize overlap between meals
    * User preferences: maximize preference ingredient matches
    * Nutritional balance: macronutrient ratios within healthy ranges

Algorithm: Greedy Heuristic-Guided Backtracking Search
1. Pre-filter domain by hard constraints (diet type, allergens)
2. For each meal slot (starting from slot_1):
   a. Calculate heuristic score for each candidate recipe
   b. Sort candidates by score (greedy ordering)
   c. Try top-k candidates (beam width = 15)
   d. For each candidate, recurse to next slot
   e. If complete assignment violates constraints, backtrack
3. Return first valid complete assignment found
"""

from constraints import filter_by_diet_and_allergens, violates_hard_constraints
from heuristics import greedy_recipe_selector


def greedy_csp_planner(recipes, user, num_meals=3, current_plan=None, used_ids=None, top_k=15):
    """
    CSP meal planner using greedy heuristic-guided backtracking search.

    Args:
        recipes: List of Recipe objects (full recipe database)
        user: User object (with constraints and preferences)
        num_meals: Number of meals to select (default: 3)
        current_plan: List of Recipe objects (partial assignment, used in recursion)
        used_ids: Set of recipe IDs already in plan (avoid duplicates)
        top_k: Beam width for greedy search (default: 15)

    Returns:
        List of Recipe objects (complete meal plan) or None if no solution found
    """
    # Initialize for first call
    if current_plan is None:
        current_plan = []
    if used_ids is None:
        used_ids = set()

    # BASE CASE: Complete assignment
    if len(current_plan) == num_meals:
        # Check hard constraints on complete plan
        if not violates_hard_constraints(current_plan, user):
            return current_plan  # Found valid solution
        else:
            return None  # Violates hard constraints, backtrack

    # RECURSIVE CASE: Fill next slot

    # Domain reduction: filter by diet and allergens, exclude already-used recipes
    available = filter_by_diet_and_allergens(recipes, user, exclude_ids=used_ids)

    if not available:
        return None  # No available recipes, backtrack

    # GREEDY HEURISTIC: Select top-k most promising candidates
    candidates = greedy_recipe_selector(available, current_plan, user, top_k, num_meals)

    # Try each candidate in order (greedy - best first)
    for recipe in candidates:
        # Add recipe to current plan
        new_plan = current_plan + [recipe]
        new_used_ids = used_ids | {recipe.id}

        # Recursive call to fill next slot
        result = greedy_csp_planner(
            recipes=recipes,
            user=user,
            num_meals=num_meals,
            current_plan=new_plan,
            used_ids=new_used_ids,
            top_k=top_k
        )

        if result is not None:
            # Found valid complete plan
            return result

    # All candidates failed, backtrack
    return None


def csp_planner_with_config(recipes, user, num_meals=3, top_k=15):
    """
    Wrapper function for CSP planner with configurable parameters.
    Useful for experiments and ablation studies.

    Args:
        recipes: List of Recipe objects
        user: User object
        num_meals: Number of meals (default: 3)
        top_k: Beam width (default: 15)

    Returns:
        List of Recipe objects or None
    """
    return greedy_csp_planner(recipes, user, num_meals, top_k=top_k)


if __name__ == '__main__':
    # Test CSP planner
    from data_loader import load_recipes, load_users
    from metrics import print_plan_evaluation
    import time

    recipes = load_recipes()
    users = load_users()

    print("Testing CSP Planner (Greedy Heuristic Backtracking)")
    print("=" * 60)

    for user in users[:5]:  # Test first 5 users
        print(f"\nUser: {user.name} ({user.diet_type}, {user.calorie_target}cal, {user.protein_min}g protein)")

        start_time = time.time()
        plan = greedy_csp_planner(recipes, user, top_k=15)
        end_time = time.time()

        runtime_ms = (end_time - start_time) * 1000

        if plan:
            print(f"Found plan in {runtime_ms:.2f}ms")
            print_plan_evaluation(plan, user)
        else:
            print(f"Failed to find plan (runtime: {runtime_ms:.2f}ms)")

    # Demonstrate concrete example from specification
    print("\n" + "=" * 60)
    print("CONCRETE EXAMPLE WALKTHROUGH")
    print("=" * 60)

    # Find Alex user
    alex = next((u for u in users if u.name == "Alex"), None)
    if alex:
        print(f"\nUser: {alex.name}")
        print(f"  Diet: {alex.diet_type}")
        print(f"  Calorie target: {alex.calorie_target}")
        print(f"  Protein minimum: {alex.protein_min}g")
        print(f"  Allergens: {alex.allergens}")
        print(f"  Preferences: {alex.preferences}")

        # Step 1: Show filtering
        available = filter_by_diet_and_allergens(recipes, alex)
        print(f"\nStep 1: Filter recipes")
        print(f"  Total recipes: {len(recipes)}")
        print(f"  After diet & allergen filtering: {len(available)}")

        # Step 2: Show greedy selection for first slot
        from heuristics import combined_heuristic
        top_5 = greedy_recipe_selector(available, [], alex, top_k=5)
        print(f"\nStep 2: Top 5 candidates for Meal 1:")
        for i, recipe in enumerate(top_5, 1):
            score = combined_heuristic([], recipe, alex)
            print(f"  {i}. {recipe.name}: {recipe.protein}g protein, {recipe.calories}cal, score={score:.1f}")

        # Step 3: Generate complete plan
        print(f"\nStep 3: Generate complete plan using CSP")
        plan = greedy_csp_planner(recipes, alex)
        if plan:
            print(f"\nFinal Plan:")
            total_cal = 0
            total_prot = 0
            for i, recipe in enumerate(plan, 1):
                print(f"  Meal {i}: {recipe.name} ({recipe.protein}g protein, {recipe.calories}cal)")
                total_cal += recipe.calories
                total_prot += recipe.protein
            print(f"\nTotals: {total_cal}cal (target: {alex.calorie_target}±300)")
            print(f"        {total_prot}g protein (minimum: {alex.protein_min}g)")
            print(f"Constraints satisfied: {'YES' if not violates_hard_constraints(plan, alex) else 'NO'}")
