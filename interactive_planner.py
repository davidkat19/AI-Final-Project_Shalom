"""
Interactive Meal Planner - Easy-to-use interface for generating personalized meal plans.

Run this script to interactively create meal plans based on your dietary preferences.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import load_recipes, Recipe, User
from csp_planner import greedy_csp_planner
from baseline import random_baseline_planner
from metrics import evaluate_plan
import time


def print_header():
    """Print welcome header."""
    print("\n" + "=" * 70)
    print(" " * 20 + "AI MEAL PLANNER")
    print(" " * 15 + "Personalized Daily Meal Plans")
    print("=" * 70)


def get_user_input():
    """Collect user preferences interactively."""
    print("\n" + "-" * 70)
    print("Let's create your personalized meal plan!")
    print("-" * 70)

    # Get name
    name = input("\nWhat's your name? ").strip() or "User"

    # Get diet type
    print("\nWhat type of diet do you follow?")
    print("  1. Balanced (no restrictions)")
    print("  2. High-Protein")
    print("  3. Vegan")
    print("  4. Vegetarian")
    print("  5. Pescatarian (fish OK)")
    print("  6. Keto (low-carb)")
    print("  7. Gluten-Free")

    diet_map = {
        '1': 'balanced',
        '2': 'high-protein',
        '3': 'vegan',
        '4': 'vegetarian',
        '5': 'pescatarian',
        '6': 'keto',
        '7': 'gluten-free'
    }

    diet_choice = input("Enter number (1-7): ").strip()
    diet_type = diet_map.get(diet_choice, 'balanced')

    # Get calorie target
    print("\nWhat's your daily calorie target?")
    print("  Typical ranges: 1400-1600 (weight loss)")
    print("                  1600-1800 (maintenance)")
    print("                  1800-2000 (active/muscle building)")

    while True:
        try:
            calorie_input = input("Enter calories (1400-2000): ").strip()
            calorie_target = float(calorie_input) if calorie_input else 1700
            if 1200 <= calorie_target <= 2500:
                break
            print("  Please enter a value between 1200 and 2500")
        except ValueError:
            print("  Please enter a valid number")

    # Get protein minimum
    print("\nWhat's your minimum daily protein goal (grams)?")
    print("  Typical ranges: 50-70g (general health)")
    print("                  70-90g (active lifestyle)")
    print("                  90-120g (muscle building)")

    while True:
        try:
            protein_input = input("Enter protein goal (50-120g): ").strip()
            protein_min = float(protein_input) if protein_input else 70
            if 40 <= protein_min <= 150:
                break
            print("  Please enter a value between 40 and 150")
        except ValueError:
            print("  Please enter a valid number")

    # Get allergens
    print("\nDo you have any food allergens? (comma-separated)")
    print("  Common: peanuts, shellfish, dairy, gluten, soy, eggs")
    print("  Or press Enter to skip")

    allergen_input = input("Allergens: ").strip()
    allergens = [a.strip().lower() for a in allergen_input.split(',') if a.strip()] if allergen_input else []

    # Get preferences
    print("\nWhat are your favorite ingredients? (comma-separated)")
    print("  Examples: chicken, salmon, beef, tofu, quinoa, avocado")
    print("  Or press Enter to skip")

    pref_input = input("Preferences: ").strip()
    preferences = [p.strip().lower() for p in pref_input.split(',') if p.strip()] if pref_input else []

    # Create User object
    user = User(
        user_id=999,
        name=name,
        diet_type=diet_type,
        calorie_target=calorie_target,
        protein_min=protein_min,
        allergens=allergens,
        preferences=preferences
    )

    return user


def display_meal_plan(plan, user, metrics, runtime_ms):
    """Display meal plan in a user-friendly format."""
    print("\n" + "=" * 70)
    print(" " * 25 + "YOUR MEAL PLAN")
    print("=" * 70)

    if not plan:
        print("\n[!] Sorry, could not generate a meal plan with your constraints.")
        print("\nPossible reasons:")
        print("  - Too many allergens limiting available recipes")
        print("  - Protein goal too high for calorie target")
        print("  - Very restrictive diet + allergen combination")
        print("\nSuggestions:")
        print("  - Relax protein goal slightly")
        print("  - Increase calorie target")
        print("  - Try a less restrictive diet type")
        return

    # Display meals
    print(f"\nPersonalized plan for {user.name}")
    print(f"Diet: {user.diet_type.title()} | Target: {user.calorie_target:.0f} cal, {user.protein_min:.0f}g protein")

    if user.allergens:
        print(f"Avoiding: {', '.join(user.allergens)}")

    print("\n" + "-" * 70)
    print("YOUR 3 MEALS:")
    print("-" * 70)

    total_cal = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0

    for i, recipe in enumerate(plan, 1):
        print(f"\nMeal {i}: {recipe.name}")
        print(f"  Nutrition: {recipe.calories:.0f} cal | "
              f"{recipe.protein:.0f}g protein | "
              f"{recipe.carbs:.0f}g carbs | "
              f"{recipe.fat:.0f}g fat")
        print(f"  Ingredients: {', '.join(sorted(list(recipe.ingredients)[:5]))}"
              f"{', ...' if len(recipe.ingredients) > 5 else ''}")

        total_cal += recipe.calories
        total_protein += recipe.protein
        total_carbs += recipe.carbs
        total_fat += recipe.fat

    # Display totals
    print("\n" + "-" * 70)
    print("DAILY TOTALS:")
    print("-" * 70)
    print(f"  Calories: {total_cal:.0f} cal (target: {user.calorie_target:.0f})")
    print(f"  Protein:  {total_protein:.0f}g (minimum: {user.protein_min:.0f}g)")
    print(f"  Carbs:    {total_carbs:.0f}g")
    print(f"  Fat:      {total_fat:.0f}g")

    # Calculate percentages
    total_cals_from_macros = (total_protein * 4) + (total_carbs * 4) + (total_fat * 9)
    if total_cals_from_macros > 0:
        protein_pct = (total_protein * 4 / total_cals_from_macros) * 100
        carbs_pct = (total_carbs * 4 / total_cals_from_macros) * 100
        fat_pct = (total_fat * 9 / total_cals_from_macros) * 100

        print(f"\n  Macros: {protein_pct:.0f}% protein, {carbs_pct:.0f}% carbs, {fat_pct:.0f}% fat")

    # Display quality metrics
    print("\n" + "-" * 70)
    print("PLAN QUALITY:")
    print("-" * 70)

    cal_diff = total_cal - user.calorie_target
    cal_status = "perfect" if abs(cal_diff) < 50 else ("close" if abs(cal_diff) < 150 else "acceptable")
    print(f"  Calorie Accuracy: {cal_status} ({cal_diff:+.0f} cal difference)")

    protein_diff = total_protein - user.protein_min
    protein_status = "excellent" if protein_diff >= 10 else ("good" if protein_diff >= 0 else "below target")
    print(f"  Protein Goal: {protein_status} ({protein_diff:+.0f}g difference)")

    print(f"  Diversity Score: {metrics['diversity_score']:.0f}/100")

    if user.preferences:
        print(f"  Preference Match: {metrics['preference_score']:.0f}/100")

    print(f"  Overall Balance: {metrics['balance_score']:.0f}/100")

    print(f"\n  Generated in {runtime_ms:.1f}ms using AI planning algorithms")


def main_menu():
    """Main interactive loop."""
    print_header()

    print("\nLoading recipe database...")
    try:
        recipes = load_recipes('data/recipes.csv')
        print(f"[OK] Loaded {len(recipes)} recipes")
    except Exception as e:
        print(f"[ERROR] Could not load recipes: {e}")
        print("Make sure you're in the meal-planner directory!")
        return

    while True:
        print("\n" + "=" * 70)
        print("MAIN MENU")
        print("=" * 70)
        print("  1. Create a new meal plan")
        print("  2. Try a sample user (Alex - high protein)")
        print("  3. Try a sample user (Sarah - vegan)")
        print("  4. Try a sample user (Mike - keto)")
        print("  5. View all sample users")
        print("  6. Exit")

        choice = input("\nEnter choice (1-6): ").strip()

        if choice == '1':
            # Custom user
            user = get_user_input()

            print("\n" + "-" * 70)
            print("Generating your personalized meal plan...")
            print("-" * 70)

            start_time = time.time()
            plan = greedy_csp_planner(recipes, user, top_k=15)
            runtime_ms = (time.time() - start_time) * 1000

            metrics = evaluate_plan(plan, user) if plan else {}
            display_meal_plan(plan, user, metrics, runtime_ms)

        elif choice in ['2', '3', '4']:
            # Sample users
            from data_loader import load_users
            users = load_users('data/test_users.json')

            sample_map = {'2': 0, '3': 1, '4': 2}  # Alex, Sarah, Mike
            user = users[sample_map[choice]]

            print(f"\n[Sample User: {user.name}]")
            print(f"  Diet: {user.diet_type}")
            print(f"  Calories: {user.calorie_target}")
            print(f"  Protein: {user.protein_min}g")
            print(f"  Allergens: {list(user.allergens) if user.allergens else 'None'}")

            print("\nGenerating meal plan...")
            start_time = time.time()
            plan = greedy_csp_planner(recipes, user, top_k=15)
            runtime_ms = (time.time() - start_time) * 1000

            metrics = evaluate_plan(plan, user) if plan else {}
            display_meal_plan(plan, user, metrics, runtime_ms)

        elif choice == '5':
            # View all sample users
            from data_loader import load_users
            users = load_users('data/test_users.json')

            print("\n" + "=" * 70)
            print("SAMPLE USERS")
            print("=" * 70)

            for i, user in enumerate(users, 1):
                print(f"\n{i}. {user.name}")
                print(f"   Diet: {user.diet_type}")
                print(f"   Calories: {user.calorie_target} | Protein: {user.protein_min}g")
                if user.allergens:
                    print(f"   Allergens: {', '.join(user.allergens)}")

            print("\n[Use options 2-4 in main menu to try sample users]")

        elif choice == '6':
            print("\n" + "=" * 70)
            print("Thank you for using AI Meal Planner!")
            print("Stay healthy! :)")
            print("=" * 70 + "\n")
            break

        else:
            print("\n[!] Invalid choice. Please enter 1-6.")

        # Ask if user wants to continue
        if choice in ['1', '2', '3', '4']:
            input("\nPress Enter to return to main menu...")


if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n[Interrupted by user]")
        print("Goodbye!\n")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
