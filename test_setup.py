"""
Quick verification script to test meal planner setup.

Run this to verify:
1. Data loads correctly
2. All modules import successfully
3. Basic functionality works
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_data_loading():
    """Test data loading."""
    print("=" * 60)
    print("TEST 1: Data Loading")
    print("=" * 60)

    try:
        from data_loader import load_recipes, load_users

        recipes = load_recipes('data/recipes.csv')
        users = load_users('data/test_users.json')

        print(f"[OK] Loaded {len(recipes)} recipes")
        print(f"[OK] Loaded {len(users)} users")

        # Check sample recipe
        sample_recipe = recipes[0]
        print(f"\nSample Recipe: {sample_recipe.name}")
        print(f"  Calories: {sample_recipe.calories}")
        print(f"  Protein: {sample_recipe.protein}g")
        print(f"  Ingredients: {len(sample_recipe.ingredients)} items")
        print(f"  Tags: {sample_recipe.tags}")

        # Check sample user
        sample_user = users[0]
        print(f"\nSample User: {sample_user.name}")
        print(f"  Diet: {sample_user.diet_type}")
        print(f"  Calorie Target: {sample_user.calorie_target}")
        print(f"  Protein Min: {sample_user.protein_min}g")
        print(f"  Allergens: {sample_user.allergens}")

        return True

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


def test_constraints():
    """Test constraint checking."""
    print("\n" + "=" * 60)
    print("TEST 2: Constraint Checking")
    print("=" * 60)

    try:
        from data_loader import load_recipes, load_users
        from constraints import is_diet_compatible, filter_by_diet_and_allergens

        recipes = load_recipes('data/recipes.csv')
        users = load_users('data/test_users.json')

        test_user = users[0]

        # Test diet filtering
        compatible = [r for r in recipes if is_diet_compatible(r, test_user)]
        print(f"[OK]Diet filtering: {len(compatible)}/{len(recipes)} compatible with {test_user.diet_type}")

        # Test allergen filtering
        safe = filter_by_diet_and_allergens(recipes, test_user)
        print(f"[OK]Diet + allergen filtering: {len(safe)}/{len(recipes)} safe recipes")

        return True

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


def test_baseline():
    """Test baseline algorithm."""
    print("\n" + "=" * 60)
    print("TEST 3: Baseline Algorithm")
    print("=" * 60)

    try:
        from data_loader import load_recipes, load_users
        from baseline import random_baseline_planner

        recipes = load_recipes('data/recipes.csv')
        users = load_users('data/test_users.json')

        test_user = users[0]
        plan = random_baseline_planner(recipes, test_user, seed=42)

        if plan:
            print(f"[OK]Baseline found plan for {test_user.name}")
            for i, recipe in enumerate(plan, 1):
                print(f"  Meal {i}: {recipe.name}")
        else:
            print(f"[OK]Baseline ran (no solution found)")

        return True

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


def test_csp():
    """Test CSP planner."""
    print("\n" + "=" * 60)
    print("TEST 4: CSP Planner")
    print("=" * 60)

    try:
        from data_loader import load_recipes, load_users
        from csp_planner import greedy_csp_planner
        from metrics import evaluate_plan

        recipes = load_recipes('data/recipes.csv')
        users = load_users('data/test_users.json')

        test_user = users[0]
        plan = greedy_csp_planner(recipes, test_user, top_k=15)

        if plan:
            print(f"[OK]CSP found plan for {test_user.name}")
            for i, recipe in enumerate(plan, 1):
                print(f"  Meal {i}: {recipe.name} - {recipe.calories}cal, {recipe.protein}g protein")

            metrics = evaluate_plan(plan, test_user)
            print(f"\nMetrics:")
            print(f"  Constraint Satisfaction: {metrics['constraint_satisfaction_rate']:.1f}%")
            print(f"  Calorie Error: {metrics['calorie_error']:.1f} cal")
            print(f"  Diversity: {metrics['diversity_score']:.1f}/100")
        else:
            print(f"[ERROR] CSP failed to find plan for {test_user.name}")
            return False

        return True

    except Exception as e:
        print(f"[ERROR]Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_algorithms():
    """Test all three algorithms."""
    print("\n" + "=" * 60)
    print("TEST 5: All Algorithms Comparison")
    print("=" * 60)

    try:
        from data_loader import load_recipes, load_users
        from baseline import random_baseline_planner
        from oracle import oracle_planner
        from csp_planner import greedy_csp_planner
        import time

        recipes = load_recipes('data/recipes.csv')
        users = load_users('data/test_users.json')

        test_user = users[0]
        print(f"Testing with user: {test_user.name}\n")

        # Baseline
        start = time.time()
        baseline_plan = random_baseline_planner(recipes, test_user)
        baseline_time = (time.time() - start) * 1000
        print(f"Baseline: {'SUCCESS' if baseline_plan else 'FAILED'} ({baseline_time:.1f}ms)")

        # Oracle (limited)
        start = time.time()
        oracle_plan = oracle_planner(recipes, test_user, max_combinations=5000)
        oracle_time = (time.time() - start) * 1000
        print(f"Oracle: {'SUCCESS' if oracle_plan else 'FAILED'} ({oracle_time:.1f}ms)")

        # CSP
        start = time.time()
        csp_plan = greedy_csp_planner(recipes, test_user)
        csp_time = (time.time() - start) * 1000
        print(f"CSP: {'SUCCESS' if csp_plan else 'FAILED'} ({csp_time:.1f}ms)")

        print("\n[OK]All algorithms executed successfully")
        return True

    except Exception as e:
        print(f"[ERROR]Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "#" * 60)
    print("# MEAL PLANNER SETUP VERIFICATION")
    print("#" * 60 + "\n")

    tests = [
        test_data_loading,
        test_constraints,
        test_baseline,
        test_csp,
        test_all_algorithms
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("\n[OK]All tests passed! Setup is complete.")
        print("[OK]Run 'python experiments/run_experiments.py' to execute full experiments")
    else:
        print("\n[ERROR]Some tests failed. Please check the errors above.")

    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
