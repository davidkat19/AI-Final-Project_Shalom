"""
Flask Web Application for AI Meal Planner
Provides a web interface for generating personalized meal plans.
"""

from flask import Flask, render_template, request, jsonify
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import load_recipes, User
from csp_planner import greedy_csp_planner
from baseline import random_baseline_planner
from oracle import oracle_planner
from metrics import evaluate_plan
import time

app = Flask(__name__)

# Load recipes once at startup
print("Loading recipe database...")
recipes = load_recipes('data/recipes.csv')
print(f"Loaded {len(recipes)} recipes")


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/generate-plan', methods=['POST'])
def generate_plan():
    """
    Generate a meal plan based on user input.

    Expected JSON input:
    {
        "name": "User name",
        "diet_type": "balanced|high-protein|vegan|vegetarian|pescatarian|keto|gluten-free",
        "calorie_target": 1800,
        "protein_min": 100,
        "allergens": ["peanuts", "shellfish"],
        "preferences": ["chicken", "salmon"],
        "algorithm": "csp|baseline|oracle"
    }
    """
    try:
        data = request.json

        # Create user object
        user = User(
            user_id=999,
            name=data.get('name', 'User'),
            diet_type=data.get('diet_type', 'balanced'),
            calorie_target=float(data.get('calorie_target', 1700)),
            protein_min=float(data.get('protein_min', 70)),
            allergens=[a.strip().lower() for a in data.get('allergens', []) if a.strip()],
            preferences=[p.strip().lower() for p in data.get('preferences', []) if p.strip()]
        )

        # Select algorithm
        algorithm = data.get('algorithm', 'csp')

        # Generate plan
        start_time = time.time()

        if algorithm == 'baseline':
            plan = random_baseline_planner(recipes, user, seed=42)
        elif algorithm == 'oracle':
            plan = oracle_planner(recipes, user, max_combinations=10000)
        else:  # csp (default)
            plan = greedy_csp_planner(recipes, user, top_k=15)

        runtime_ms = (time.time() - start_time) * 1000

        # Evaluate plan
        if plan:
            metrics = evaluate_plan(plan, user)

            # Format response
            response = {
                'success': True,
                'user': {
                    'name': user.name,
                    'diet_type': user.diet_type,
                    'calorie_target': user.calorie_target,
                    'protein_min': user.protein_min,
                    'allergens': list(user.allergens),
                    'preferences': list(user.preferences)
                },
                'meals': [
                    {
                        'name': recipe.name,
                        'calories': recipe.calories,
                        'protein': recipe.protein,
                        'carbs': recipe.carbs,
                        'fat': recipe.fat,
                        'ingredients': list(recipe.ingredients)[:8],  # First 8 ingredients
                        'tags': list(recipe.tags)
                    }
                    for recipe in plan
                ],
                'totals': {
                    'calories': metrics['total_calories'],
                    'protein': metrics['total_protein'],
                    'carbs': sum(r.carbs for r in plan),
                    'fat': sum(r.fat for r in plan)
                },
                'metrics': {
                    'constraint_satisfaction': metrics['constraint_satisfaction_rate'],
                    'calorie_error': metrics['calorie_error'],
                    'protein_error': metrics['protein_error'],
                    'diversity_score': metrics['diversity_score'],
                    'preference_score': metrics['preference_score'],
                    'balance_score': metrics['balance_score'],
                    'success': metrics['success']
                },
                'runtime_ms': runtime_ms,
                'algorithm': algorithm
            }

            return jsonify(response)
        else:
            return jsonify({
                'success': False,
                'error': 'Could not generate meal plan with given constraints',
                'suggestions': [
                    'Try reducing the number of allergens',
                    'Lower the protein goal slightly',
                    'Increase the calorie target',
                    'Choose a less restrictive diet type'
                ]
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/sample-users', methods=['GET'])
def get_sample_users():
    """Get list of sample users."""
    from data_loader import load_users

    try:
        users = load_users('data/test_users.json')

        sample_users = [
            {
                'id': user.id,
                'name': user.name,
                'diet_type': user.diet_type,
                'calorie_target': user.calorie_target,
                'protein_min': user.protein_min,
                'allergens': list(user.allergens),
                'preferences': list(user.preferences)
            }
            for user in users[:5]  # First 5 sample users
        ]

        return jsonify({'users': sample_users})

    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    print("\n" + "="*70)
    print(" " * 20 + "AI MEAL PLANNER WEB APP")
    print(" " * 15 + "Open http://localhost:5000 in your browser")
    print("="*70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
