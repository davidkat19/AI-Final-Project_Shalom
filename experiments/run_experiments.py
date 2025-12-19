"""
Comprehensive experimental evaluation of meal planning algorithms.

Experiments:
1. Baseline vs Oracle vs CSP comparison (all users)
2. Beam width ablation study (k = 5, 10, 15, 20, 30)
3. Constraint strictness analysis
4. Dataset size scaling (50, 100, 150, 200 recipes)
5. Failure case analysis

All results saved to experiment_results.csv
"""

import sys
import os
# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import time
import pandas as pd
from data_loader import load_recipes, load_users
from baseline import random_baseline_planner
from oracle import oracle_planner
from csp_planner import greedy_csp_planner, csp_planner_with_config
from metrics import evaluate_plan


def run_algorithm(algorithm_func, recipes, user, **kwargs):
    """
    Run an algorithm and measure performance.

    Args:
        algorithm_func: Function to call
        recipes: List of Recipe objects
        user: User object
        **kwargs: Additional arguments for algorithm

    Returns:
        dict: Results including plan, metrics, and runtime
    """
    start_time = time.time()
    plan = algorithm_func(recipes, user, **kwargs)
    end_time = time.time()

    runtime_ms = (end_time - start_time) * 1000

    metrics = evaluate_plan(plan, user) if plan else {
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

    return {
        'plan': plan,
        'metrics': metrics,
        'runtime_ms': runtime_ms,
        'found_solution': plan is not None
    }


def experiment_1_main_comparison(recipes, users):
    """
    Experiment 1: Compare Baseline vs Oracle vs CSP on all users.
    """
    print("\n" + "=" * 80)
    print("EXPERIMENT 1: BASELINE vs ORACLE vs CSP COMPARISON")
    print("=" * 80)

    results = []

    for user in users:
        print(f"\nUser: {user.name} ({user.diet_type}, {user.calorie_target}cal, {user.protein_min}g protein)")

        # Baseline
        baseline_result = run_algorithm(random_baseline_planner, recipes, user, seed=42)
        print(f"  Baseline: {'SUCCESS' if baseline_result['found_solution'] else 'FAILED'} ({baseline_result['runtime_ms']:.1f}ms)")

        # Oracle (limited for performance)
        oracle_result = run_algorithm(oracle_planner, recipes, user, max_combinations=10000)
        print(f"  Oracle: {'SUCCESS' if oracle_result['found_solution'] else 'FAILED'} ({oracle_result['runtime_ms']:.1f}ms)")

        # CSP
        csp_result = run_algorithm(greedy_csp_planner, recipes, user, top_k=15)
        print(f"  CSP: {'SUCCESS' if csp_result['found_solution'] else 'FAILED'} ({csp_result['runtime_ms']:.1f}ms)")

        # Store results
        for algo_name, result in [('Baseline', baseline_result), ('Oracle', oracle_result), ('CSP', csp_result)]:
            results.append({
                'experiment': 'main_comparison',
                'user_id': user.id,
                'user_name': user.name,
                'algorithm': algo_name,
                'found_solution': result['found_solution'],
                'runtime_ms': result['runtime_ms'],
                **result['metrics']
            })

    # Summary statistics
    print("\n" + "-" * 80)
    print("SUMMARY:")
    df = pd.DataFrame(results)
    for algo in ['Baseline', 'Oracle', 'CSP']:
        algo_results = df[df['algorithm'] == algo]
        success_rate = (algo_results['found_solution'].sum() / len(algo_results)) * 100
        avg_runtime = algo_results['runtime_ms'].mean()
        avg_cal_error = algo_results[algo_results['found_solution']]['calorie_error'].mean()
        avg_diversity = algo_results[algo_results['found_solution']]['diversity_score'].mean()

        print(f"\n{algo}:")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Avg Runtime: {avg_runtime:.1f}ms")
        if success_rate > 0:
            print(f"  Avg Calorie Error: {avg_cal_error:.1f} cal")
            print(f"  Avg Diversity: {avg_diversity:.1f}/100")

    return results


def experiment_2_beam_width_ablation(recipes, users):
    """
    Experiment 2: Beam width ablation study (k = 5, 10, 15, 20, 30).
    """
    print("\n" + "=" * 80)
    print("EXPERIMENT 2: BEAM WIDTH ABLATION STUDY")
    print("=" * 80)

    beam_widths = [5, 10, 15, 20, 30]
    results = []

    for k in beam_widths:
        print(f"\nBeam Width k={k}:")
        for user in users:
            result = run_algorithm(csp_planner_with_config, recipes, user, top_k=k)
            results.append({
                'experiment': 'beam_width_ablation',
                'user_id': user.id,
                'user_name': user.name,
                'beam_width': k,
                'found_solution': result['found_solution'],
                'runtime_ms': result['runtime_ms'],
                **result['metrics']
            })

        # Summary for this k
        k_results = [r for r in results if r['beam_width'] == k]
        success_count = sum(1 for r in k_results if r['found_solution'])
        avg_runtime = sum(r['runtime_ms'] for r in k_results) / len(k_results)
        print(f"  Success: {success_count}/{len(users)} ({success_count/len(users)*100:.1f}%)")
        print(f"  Avg Runtime: {avg_runtime:.1f}ms")

    return results


def experiment_3_constraint_strictness(recipes, users):
    """
    Experiment 3: Analyze how constraint strictness affects success rate.
    """
    print("\n" + "=" * 80)
    print("EXPERIMENT 3: CONSTRAINT STRICTNESS ANALYSIS")
    print("=" * 80)

    results = []

    # Categorize users by constraint strictness
    for user in users:
        num_allergens = len(user.allergens)
        is_restrictive_diet = user.diet_type in ['vegan', 'keto', 'gluten-free']

        if num_allergens == 0 and not is_restrictive_diet:
            category = 'lenient'
        elif num_allergens <= 1 and not is_restrictive_diet:
            category = 'moderate'
        else:
            category = 'strict'

        result = run_algorithm(greedy_csp_planner, recipes, user, top_k=15)

        print(f"\nUser: {user.name} ({category})")
        print(f"  Diet: {user.diet_type}, Allergens: {list(user.allergens)}")
        print(f"  Result: {'SUCCESS' if result['found_solution'] else 'FAILED'}")

        results.append({
            'experiment': 'constraint_strictness',
            'user_id': user.id,
            'user_name': user.name,
            'strictness': category,
            'num_allergens': num_allergens,
            'diet_type': user.diet_type,
            'found_solution': result['found_solution'],
            'runtime_ms': result['runtime_ms'],
            **result['metrics']
        })

    # Summary by category
    print("\n" + "-" * 80)
    print("SUMMARY BY STRICTNESS:")
    df = pd.DataFrame(results)
    for category in ['lenient', 'moderate', 'strict']:
        cat_results = df[df['strictness'] == category]
        if len(cat_results) > 0:
            success_rate = (cat_results['found_solution'].sum() / len(cat_results)) * 100
            print(f"\n{category.capitalize()}: {success_rate:.1f}% success ({cat_results['found_solution'].sum()}/{len(cat_results)})")

    return results


def experiment_4_dataset_scaling(recipes, users):
    """
    Experiment 4: Dataset size scaling (50, 100, 150, 200 recipes).
    """
    print("\n" + "=" * 80)
    print("EXPERIMENT 4: DATASET SIZE SCALING")
    print("=" * 80)

    dataset_sizes = [50, 100, 150, 200]
    results = []

    for size in dataset_sizes:
        print(f"\nDataset Size: {size} recipes")
        subset_recipes = recipes[:size]

        for user in users:
            result = run_algorithm(greedy_csp_planner, subset_recipes, user, top_k=15)
            results.append({
                'experiment': 'dataset_scaling',
                'user_id': user.id,
                'user_name': user.name,
                'dataset_size': size,
                'found_solution': result['found_solution'],
                'runtime_ms': result['runtime_ms'],
                **result['metrics']
            })

        # Summary for this size
        size_results = [r for r in results if r['dataset_size'] == size]
        success_count = sum(1 for r in size_results if r['found_solution'])
        avg_runtime = sum(r['runtime_ms'] for r in size_results) / len(size_results)
        print(f"  Success: {success_count}/{len(users)} ({success_count/len(users)*100:.1f}%)")
        print(f"  Avg Runtime: {avg_runtime:.1f}ms")

    return results


def experiment_5_failure_analysis(recipes, users):
    """
    Experiment 5: Analyze failure cases.
    """
    print("\n" + "=" * 80)
    print("EXPERIMENT 5: FAILURE CASE ANALYSIS")
    print("=" * 80)

    results = []
    failures = []

    for user in users:
        result = run_algorithm(greedy_csp_planner, recipes, user, top_k=15)

        if not result['found_solution']:
            failures.append({
                'user': user,
                'result': result
            })

        results.append({
            'experiment': 'failure_analysis',
            'user_id': user.id,
            'user_name': user.name,
            'found_solution': result['found_solution'],
            'runtime_ms': result['runtime_ms'],
            **result['metrics']
        })

    print(f"\nTotal Failures: {len(failures)}/{len(users)}")

    if failures:
        print("\nFailed Users:")
        for fail in failures:
            user = fail['user']
            print(f"\n  User: {user.name}")
            print(f"    Diet: {user.diet_type}")
            print(f"    Calorie Target: {user.calorie_target}")
            print(f"    Protein Min: {user.protein_min}g")
            print(f"    Allergens: {list(user.allergens)}")
            print(f"    Preferences: {list(user.preferences)}")

            # Analyze why it failed
            from constraints import filter_by_diet_and_allergens
            available = filter_by_diet_and_allergens(recipes, user)
            print(f"    Available Recipes: {len(available)}")

            if len(available) < 3:
                print(f"    REASON: Not enough recipes after filtering (need 3, have {len(available)})")
            else:
                print(f"    REASON: Could not satisfy calorie/protein constraints with available recipes")
    else:
        print("\nNo failures! All users successfully planned.")

    return results


def main():
    """Run all experiments."""
    print("\n" + "=" * 80)
    print("MEAL PLANNER EXPERIMENTAL EVALUATION")
    print("=" * 80)

    # Load data
    print("\nLoading data...")
    recipes = load_recipes()
    users = load_users()
    print(f"Loaded {len(recipes)} recipes and {len(users)} users")

    # Run all experiments
    all_results = []

    all_results.extend(experiment_1_main_comparison(recipes, users))
    all_results.extend(experiment_2_beam_width_ablation(recipes, users))
    all_results.extend(experiment_3_constraint_strictness(recipes, users))
    all_results.extend(experiment_4_dataset_scaling(recipes, users))
    all_results.extend(experiment_5_failure_analysis(recipes, users))

    # Save results to CSV
    output_file = 'experiment_results.csv'
    df = pd.DataFrame(all_results)

    # Replace infinity with a large number for CSV compatibility
    df = df.replace([float('inf'), -float('inf')], 999999)

    df.to_csv(output_file, index=False)
    print("\n" + "=" * 80)
    print(f"Results saved to {output_file}")
    print("=" * 80)

    # Show sample meal plans
    print("\n" + "=" * 80)
    print("SAMPLE MEAL PLANS")
    print("=" * 80)

    sample_users = users[:3]
    for user in sample_users:
        plan = greedy_csp_planner(recipes, user, top_k=15)
        if plan:
            print(f"\nUser: {user.name} ({user.diet_type})")
            print(f"Target: {user.calorie_target}cal, {user.protein_min}g protein minimum")
            print(f"Meal Plan:")
            for i, recipe in enumerate(plan, 1):
                print(f"  {i}. {recipe.name} - {recipe.calories}cal, {recipe.protein}g protein")
            print(f"Totals: {sum(r.calories for r in plan):.0f}cal, {sum(r.protein for r in plan):.0f}g protein")


if __name__ == '__main__':
    main()
