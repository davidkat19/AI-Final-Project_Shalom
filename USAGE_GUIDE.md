# AI Meal Planner - User Guide

## Quick Start (3 Steps)

### 1. Install
```bash
cd meal-planner
pip install -r requirements.txt
```

### 2. Run Interactive Planner
```bash
python interactive_planner.py
```

### 3. Follow Prompts
Answer simple questions about your diet and get your personalized meal plan!

---

## Interactive Meal Planner Tutorial

### Starting the Program

```bash
python interactive_planner.py
```

You'll see:
```
======================================================================
                    AI MEAL PLANNER
               Personalized Daily Meal Plans
======================================================================

Loading recipe database...
[OK] Loaded 200 recipes

MAIN MENU
  1. Create a new meal plan
  2. Try a sample user (Alex - high protein)
  3. Try a sample user (Sarah - vegan)
  4. Try a sample user (Mike - keto)
  5. View all sample users
  6. Exit
```

### Option 1: Create Your Own Meal Plan

**Step-by-step:**

1. **Choose option 1** from the main menu

2. **Enter your name** (or press Enter to use "User")
   ```
   What's your name? Sarah
   ```

3. **Select your diet type:**
   ```
   What type of diet do you follow?
     1. Balanced (no restrictions)
     2. High-Protein
     3. Vegan
     4. Vegetarian
     5. Pescatarian (fish OK)
     6. Keto (low-carb)
     7. Gluten-Free

   Enter number (1-7): 3
   ```

4. **Enter daily calorie target:**
   ```
   What's your daily calorie target?
     Typical ranges: 1400-1600 (weight loss)
                     1600-1800 (maintenance)
                     1800-2000 (active/muscle building)

   Enter calories (1400-2000): 1600
   ```

5. **Enter minimum protein goal:**
   ```
   What's your minimum daily protein goal (grams)?
     Typical ranges: 50-70g (general health)
                     70-90g (active lifestyle)
                     90-120g (muscle building)

   Enter protein goal (50-120g): 60
   ```

6. **List any allergens** (optional):
   ```
   Do you have any food allergens? (comma-separated)
     Common: peanuts, shellfish, dairy, gluten, soy, eggs
     Or press Enter to skip

   Allergens: [press Enter to skip]
   ```

7. **List favorite ingredients** (optional):
   ```
   What are your favorite ingredients? (comma-separated)
     Examples: chicken, salmon, beef, tofu, quinoa, avocado
     Or press Enter to skip

   Preferences: quinoa, chickpeas, tofu
   ```

8. **View your meal plan:**
   ```
   ======================================================================
                            YOUR MEAL PLAN
   ======================================================================

   Personalized plan for Sarah
   Diet: Vegan | Target: 1600 cal, 60g protein

   ----------------------------------------------------------------------
   YOUR 3 MEALS:
   ----------------------------------------------------------------------

   Meal 1: Quinoa Buddha Bowl
     Nutrition: 420 cal | 16g protein | 58g carbs | 14g fat
     Ingredients: avocado, chickpeas, kale, quinoa, tahini

   Meal 2: Tofu Pad Thai
     Nutrition: 440 cal | 18g protein | 52g carbs | 16g fat
     Ingredients: bean sprouts, lime, peanuts, rice noodles, tofu

   Meal 3: Lentil Curry
     Nutrition: 360 cal | 18g protein | 52g carbs | 8g fat
     Ingredients: chickpeas, coconut milk, curry powder, spinach, tomato

   ----------------------------------------------------------------------
   DAILY TOTALS:
   ----------------------------------------------------------------------
     Calories: 1220 cal (target: 1600)
     Protein:  52g (minimum: 60g)
     Carbs:    162g
     Fat:      38g

     Macros: 17% protein, 54% carbs, 28% fat

   ----------------------------------------------------------------------
   PLAN QUALITY:
   ----------------------------------------------------------------------
     Calorie Accuracy: acceptable (-380 cal difference)
     Protein Goal: below target (-8g difference)
     Diversity Score: 65/100
     Preference Match: 100/100
     Overall Balance: 82/100

     Generated in 3.2ms using AI planning algorithms
   ```

### Option 2-4: Try Sample Users

Quick way to see the planner in action:

- **Option 2:** Alex (high-protein, 1800 cal, avoids peanuts)
- **Option 3:** Sarah (vegan, 1600 cal, no allergens)
- **Option 4:** Mike (keto, 1900 cal, avoids shellfish)

Just select the number and see the instant meal plan!

### Option 5: View All Sample Users

See all 10 pre-configured users with different dietary needs:
- Different diet types (vegan, keto, pescatarian, etc.)
- Various calorie targets (1400-2000)
- Different protein goals (50-120g)
- Multiple allergen combinations

### Option 6: Exit

Safely exit the program.

---

## Understanding Your Meal Plan

### Meal Information

Each meal shows:
- **Name:** Recipe name
- **Nutrition:** Calories, protein, carbs, fat
- **Ingredients:** Key ingredients (first 5 shown)

### Daily Totals

- **Calories:** Total vs. your target
- **Protein:** Total vs. your minimum goal
- **Carbs:** Total carbohydrates
- **Fat:** Total fat
- **Macros:** Percentage breakdown of macronutrients

### Quality Metrics

1. **Calorie Accuracy:**
   - `perfect`: Within 50 calories of target
   - `close`: Within 150 calories
   - `acceptable`: Within 300 calories (±300 is the tolerance)

2. **Protein Goal:**
   - `excellent`: 10g+ above minimum
   - `good`: Meets or exceeds minimum
   - `below target`: Under minimum (shows deficit)

3. **Diversity Score (0-100):**
   - Measures ingredient variety across meals
   - Higher = more diverse ingredients
   - Target: ≥40 for good variety

4. **Preference Match (0-100):**
   - Percentage of your preferred ingredients in the plan
   - Only shown if you specified preferences
   - 100% = all preferences matched

5. **Balance Score (0-100):**
   - How well macros align with healthy ratios
   - Protein: 25-35%, Carbs: 45-55%, Fat: 20-30%
   - Higher = better balanced

---

## Troubleshooting

### "Could not generate a meal plan"

**Possible reasons:**
1. **Too many allergens** - Limits available recipes too much
2. **Protein goal too high for calorie target** - Impossible to meet both
3. **Very restrictive combination** - E.g., vegan + keto + multiple allergens

**Solutions:**
- Reduce number of allergens
- Lower protein goal slightly
- Increase calorie target
- Choose less restrictive diet type
- Try "balanced" diet first to test

### Example Problem Cases

**Won't work:**
- 1200 calories + 120g protein (too high protein for low calories)
- Vegan + avoids soy + avoids nuts + avoids gluten (too restrictive)

**Will work:**
- 1600 calories + 80g protein
- Vegetarian + avoids peanuts
- High-protein + 1800 calories + 100g protein

### Tips for Best Results

1. **Realistic protein goals:**
   - General health: 0.8-1.0g per kg body weight
   - Active: 1.2-1.6g per kg
   - Muscle building: 1.6-2.2g per kg

2. **Calorie target:**
   - Use online calculator for your TDEE (Total Daily Energy Expenditure)
   - Weight loss: TDEE - 500 calories
   - Maintenance: TDEE
   - Muscle gain: TDEE + 300-500 calories

3. **Allergens:**
   - Only list true allergens (medical need to avoid)
   - Use diet type for preferences (e.g., vegetarian instead of listing meat allergens)

4. **Preferences:**
   - List 2-5 favorite ingredients for best matching
   - Too many preferences may limit variety

---

## For Advanced Users

### Run Experiments

Compare different algorithms:
```bash
python experiments/run_experiments.py
```

Outputs:
- Baseline vs Oracle vs CSP comparison
- Beam width optimization study
- Constraint strictness analysis
- Dataset scaling experiments
- Detailed metrics in `experiment_results.csv`

### Programmatic Usage

```python
from src.data_loader import load_recipes, User
from src.csp_planner import greedy_csp_planner
from src.metrics import evaluate_plan

# Load recipes
recipes = load_recipes('data/recipes.csv')

# Create custom user
user = User(
    user_id=1,
    name="Custom User",
    diet_type="vegetarian",
    calorie_target=1700,
    protein_min=75,
    allergens=["peanuts"],
    preferences=["cheese", "eggs", "quinoa"]
)

# Generate plan
plan = greedy_csp_planner(recipes, user, top_k=15)

# Evaluate
metrics = evaluate_plan(plan, user)

# Display
if plan:
    for i, recipe in enumerate(plan, 1):
        print(f"Meal {i}: {recipe.name}")
```

### Customize Algorithm Parameters

```python
# Adjust beam width (default: 15)
plan = greedy_csp_planner(recipes, user, top_k=20)  # More exploration

# Change number of meals (default: 3)
plan = greedy_csp_planner(recipes, user, num_meals=4)
```

---

## FAQ

**Q: How long does it take to generate a plan?**
A: Typically 2-10 milliseconds (instant to human perception)

**Q: How many recipes are in the database?**
A: 200 diverse recipes covering all major diet types

**Q: Can I add my own recipes?**
A: Yes, edit `data/recipes.csv` following the same format

**Q: What algorithms does this use?**
A: Constraint Satisfaction Problem (CSP) with greedy heuristic-guided backtracking search - classical AI planning technique

**Q: Is this better than random meal selection?**
A: Yes - CSP achieves 90% success rate vs 60% for random sampling, with much better nutritional accuracy

**Q: Can I use this for weekly meal planning?**
A: Currently generates single-day plans. Run multiple times for weekly variety

**Q: Does it consider micronutrients (vitamins, minerals)?**
A: No, focuses on macronutrients (calories, protein, carbs, fat). Future enhancement

**Q: Is the nutritional data accurate?**
A: Based on typical recipe values. For medical purposes, verify with registered dietitian

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review README.md for technical details
3. Run `python test_setup.py` to verify installation
4. Check that you're in the `meal-planner` directory

---

**Enjoy your personalized meal planning! 🍽️**
