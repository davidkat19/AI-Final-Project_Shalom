<<<<<<< HEAD
# AI-Final-Project_Shalom
Meal planning system using constraint satisfaction algorithms to generate personalized plans optimizing for nutrition, diversity, and dietary constraints. Compare 3 approaches with interactive demo and analysis.
=======
# AI Meal Planner: Constraint Satisfaction and Heuristic Search

**AI Course Semester Project**
**Authors: David Katembo, Fabrice kadima, Pemphyle Nzuzi
**Date:** December 18, 2025.

---

## Table of Contents

1. [Task Definition](#task-definition)
2. [Infrastructure and Dataset](#infrastructure-and-dataset)
3. [Approach](#approach)
4. [Baseline and Oracle](#baseline-and-oracle)
5. [Literature Review](#literature-review)
6. [Setup and Usage](#setup-and-usage)

---

## Task Definition

### What the System Does

This AI meal planner generates personalized daily meal plans that satisfy user dietary constraints while optimizing nutritional goals.

**Input:**
- User dietary constraints: calorie target, minimum protein, diet type (vegan, keto, etc.), allergens, preferences
- Structured recipe dataset: 200 recipes with nutritional information and metadata

**Output:**
- Daily meal plan: 3 meals that satisfy all hard constraints and optimize soft constraints
- Nutritional breakdown and quality metrics

**Real-World Problem:**
Automated meal planning addresses the challenge of personalized nutrition management. People struggle to balance multiple nutritional goals (calories, protein, vitamins) while respecting dietary restrictions (allergies, ethics, health conditions). This system provides intelligent decision support for dietary management, similar to tools used by dietitians, meal kit services, and health apps.

### Scope

**Not Too Narrow:**
Unlike simple binary classification ("healthy" vs "unhealthy" recipes), this system performs structured prediction with multi-constraint optimization. It must balance conflicting goals and generate complete, feasible meal plans.

**Not Too Broad:**
Focused on feasible meal plan generation under constraints, not general nutrition advice or long-term dietary planning. The system operates on a fixed dataset with well-defined constraints.

**Appropriate Complexity:**
The problem involves:
- Combinatorial search space: 200³ = 8 million possible 3-meal combinations
- Multiple constraint types: hard (must satisfy) and soft (prefer to satisfy)
- Conflicting objectives: calorie accuracy vs protein goals vs ingredient diversity
- Real-world applicability with manageable computational requirements

---

## Infrastructure and Dataset

### Dataset Description

**Recipe Dataset (recipes.csv):**
- **Size:** 200 diverse recipes
- **Source:** Kaggle Recipe Ingredients dataset style (cleaned and formatted)
- **Fields:**
  - `id`: Unique recipe identifier (1-200)
  - `name`: Recipe name
  - `calories`: Calories per serving (120-650 range)
  - `protein`: Protein in grams (4-52g range)
  - `carbs`: Carbohydrates in grams
  - `fat`: Fat in grams
  - `ingredients`: Comma-separated ingredient list
  - `tags`: Comma-separated dietary tags (vegan, keto, gluten-free, high-protein, etc.)

**Dietary Tag Coverage:**
- Vegan: 40+ recipes
- Vegetarian: 60+ recipes
- Pescatarian: 50+ recipes
- High-protein (≥25g): 90+ recipes
- Keto: 60+ recipes
- Gluten-free: 100+ recipes
- Low-carb: 50+ recipes

**Test Users (test_users.json):**
- **Size:** 10 diverse users with realistic requirements
- **Fields:**
  - `id`: User identifier
  - `name`: User name
  - `diet_type`: Primary diet (vegan, vegetarian, pescatarian, keto, high-protein, gluten-free, balanced)
  - `calorie_target`: Daily calorie goal (1400-2000, achievable with 3 meals)
  - `protein_min`: Minimum daily protein (50-120g, achievable with 3 meals)
  - `allergens`: List of allergens to avoid (peanuts, shellfish, dairy, gluten)
  - `preferences`: Preferred ingredients (chicken, quinoa, salmon, etc.)

### Preprocessing

All preprocessing is automated in `src/data_loader.py`:

1. **Ingredient Parsing:** Convert comma-separated strings to sets for efficient lookup
   ```python
   ingredients = set(ing.strip().lower() for ing in ingredients.split(','))
   ```

2. **Tag Normalization:** Convert dietary tags to lowercase sets for consistent matching
   ```python
   tags = set(tag.strip().lower() for tag in tags.split(','))
   ```

3. **Type Conversion:** Ensure nutritional values are floats for calculations

4. **Validation:** All 200 recipes have complete nutritional information and valid tags

---

## Approach

### Problem Formulation: Constraint Satisfaction Problem (CSP)

**CSP Components:**

1. **Variables:**
   - Three meal slots: `slot_1`, `slot_2`, `slot_3`
   - Each slot must be assigned one recipe from the domain

2. **Domain:**
   - All recipes that match user's diet type and don't contain allergens
   - Domain is pre-filtered for efficiency (typically 50-150 recipes per user)

3. **Hard Constraints (Must Satisfy):**
   - **Diet Compatibility:** Each recipe must match user's diet type
     - Example: Vegan user → only vegan recipes
     - Hierarchy: pescatarian accepts vegan+vegetarian+pescatarian
   - **Allergen Avoidance:** No recipe contains user's allergens
     - Case-insensitive partial matching in ingredients
   - **Calorie Range:** Total calories within target ± 300
     - Example: Target 1800 → accept 1500-2100 range
   - **Minimum Protein:** Total protein ≥ user's minimum
     - Example: Minimum 120g → must achieve at least 120g

4. **Soft Constraints (Optimize via Heuristic):**
   - **Ingredient Diversity:** Minimize overlap between meals
   - **User Preferences:** Maximize matching of preferred ingredients
   - **Nutritional Balance:** Macronutrient ratios within healthy ranges

### Algorithm: Greedy Heuristic-Guided Backtracking Search

**Why This Approach?**

1. **CSP Framework Advantages:**
   - Natural representation of hard constraints
   - Systematic search with completeness guarantees
   - Backtracking handles infeasible partial assignments

2. **Greedy Heuristic Benefits:**
   - Reduces search space dramatically (200³ → manageable)
   - Tries most promising candidates first
   - Faster than exhaustive search while maintaining quality

3. **Comparison to Alternatives:**
   - Better than random sampling (baseline)
   - More efficient than exhaustive search (oracle)
   - More principled than pure greedy (can backtrack when stuck)

**Algorithm Details:**

```
FUNCTION greedy_csp_planner(recipes, user, num_meals=3, current_plan=[], used_ids={}):
    # BASE CASE: Complete assignment
    IF len(current_plan) == num_meals:
        IF NOT violates_hard_constraints(current_plan, user):
            RETURN current_plan  # Success!
        ELSE:
            RETURN None  # Constraint violation, backtrack

    # RECURSIVE CASE: Fill next slot

    # Step 1: Domain reduction (filter by diet type and allergens)
    available = filter_by_diet_and_allergens(recipes, user, exclude=used_ids)

    IF available is empty:
        RETURN None  # No valid options, backtrack

    # Step 2: Greedy heuristic ordering
    candidates = greedy_recipe_selector(available, current_plan, user, top_k=15)

    # Step 3: Try top-k candidates in order
    FOR recipe IN candidates:
        # Recursive call with updated plan
        result = greedy_csp_planner(
            recipes, user, num_meals,
            current_plan + [recipe],
            used_ids ∪ {recipe.id}
        )

        IF result is not None:
            RETURN result  # Found valid solution

    # Step 4: All candidates failed, backtrack
    RETURN None
```

**Heuristic Function:**

The heuristic evaluates how "promising" a candidate recipe is for the current partial plan. Lower score = more promising.

```python
h(partial_plan, candidate, user) =
    w1 × |total_calories - target|              # Calorie distance
  + w2 × max(0, protein_min - total_protein)    # Protein deficit
  + w3 × ingredient_overlap_count × 10           # Diversity penalty
  + w4 × (100 - diversity_score)                 # Low diversity penalty
  + w5 × (100 - preference_score)                # Low preference penalty
```

**Weights:** w1=1.0, w2=2.0, w3=1.0, w4=0.6, w5=0.4
(Protein deficit weighted higher as it's a critical constraint)

**Beam Width (top_k):** Default 15
- Balances exploration (more candidates) vs exploitation (fewer trials)
- Determined through ablation study (see Experiments)

### Concrete Example Walkthrough

**User:** Alex
- Diet: high-protein
- Calorie target: 1800
- Protein minimum: 120g
- Allergens: peanuts
- Preferences: chicken, beef, salmon

**Step 1: Domain Filtering**
```
Total recipes: 200
After diet filter (high-protein ≥25g): 91 recipes
After allergen filter (no peanuts): 85 recipes
Domain size: 85 recipes
```

**Step 2: Fill Slot 1**
```
Calculate heuristic for all 85 recipes
Top 5 candidates:
1. Grilled Steak (52g protein, 480cal) → score = 85.3
2. Chicken Alfredo (38g protein, 620cal) → score = 92.1
3. Grilled Salmon Salad (42g protein, 380cal) → score = 88.5
4. Turkey Meatballs (42g protein, 360cal) → score = 94.2
5. Beef Stir Fry (35g protein, 480cal) → score = 96.8

Select: Grilled Steak (lowest score, best match)
Current plan: [Grilled Steak]
Totals so far: 480cal, 52g protein
```

**Step 3: Fill Slot 2**
```
Exclude: Grilled Steak (id=21)
Available: 84 recipes

With partial plan [Grilled Steak], calculate heuristic
Top 5 candidates:
1. Chicken Alfredo (38g protein, 620cal) → score = 45.2
   - Good calorie complement (480+620=1100, need ~700 more)
   - High protein (52+38=90g, need 30g more)
   - No ingredient overlap with steak
2. Grilled Salmon Salad (42g protein, 380cal) → score = 52.1
3. ...

Select: Chicken Alfredo
Current plan: [Grilled Steak, Chicken Alfredo]
Totals so far: 1100cal, 90g protein
```

**Step 4: Fill Slot 3**
```
Exclude: Grilled Steak, Chicken Alfredo
Available: 83 recipes

Need: ~700 cal, ~30g protein to hit targets
With partial plan, calculate heuristic
Top 5 candidates:
1. Beef Lasagna (36g protein, 580cal) → score = 38.1
   - Perfect calorie match (1100+580=1680 ≈ 1800)
   - Exceeds protein (90+36=126 ≥ 120 ✓)
2. ...

Select: Beef Lasagna
Final plan: [Grilled Steak, Chicken Alfredo, Beef Lasagna]

Constraint check:
✓ Calories: 1680 (within 1800±300)
✓ Protein: 126g (≥ 120g)
✓ No allergens
✓ All high-protein recipes

SUCCESS - return plan
```

### Design Tradeoffs

1. **Accuracy vs Efficiency:**
   - **Choice:** Beam width k=15 (not exhaustive, not too narrow)
   - **Tradeoff:** May miss optimal solution but finds good solutions quickly
   - **Justification:** 15 candidates covers diverse options while maintaining <100ms runtime

2. **Completeness vs Speed:**
   - **Choice:** Greedy with backtracking (not pure greedy)
   - **Tradeoff:** Slower than pure greedy but can recover from bad choices
   - **Justification:** Backtracking essential for constrained problems where greedy can dead-end

3. **Hard vs Soft Constraints:**
   - **Choice:** Hard constraints via filtering/checking, soft via heuristic
   - **Tradeoff:** Hard constraints always satisfied, soft constraints optimized but not guaranteed
   - **Justification:** Matches real-world requirements (must avoid allergens, prefer diversity)

---

## Baseline and Oracle

### Baseline: Random Sampling with Calorie Filter

**Purpose:** Establish lower bound (minimum expected performance)

**Algorithm:**
```python
1. Filter recipes by diet and allergens
2. Randomly sample 3 meals (without replacement)
3. Check if total calories within target ± 300
4. Check if total protein ≥ minimum
5. If valid, return; else repeat (max 1000 attempts)
```

**Expected Performance:**
- Success rate: ~60% (random has low probability of hitting constraints)
- Calorie error: High variance
- Diversity: Purely random
- Runtime: Fast (<50ms)

**Why This Baseline?**
Shows that naive random sampling is insufficient for this problem. Any algorithm scoring below baseline is worse than random and should not be used.

### Oracle: Exhaustive Search with Optimal Scoring

**Purpose:** Establish upper bound (theoretical maximum with perfect information)

**Algorithm:**
```python
1. Filter recipes by diet and allergens
2. Generate ALL combinations of 3 meals
3. Filter by hard constraints (calories, protein)
4. Score all valid plans with optimal function:
   score = 0.1×(calorie_error)² + 0.2×(protein_surplus_error)²
           - 5×unique_ingredients - 20×preferences_matched
5. Return best-scoring plan
```

**Expected Performance:**
- Success rate: ~95% (finds solution if one exists within combinations tested)
- Calorie error: Minimal (optimizes precisely)
- Diversity: High (explicitly optimized)
- Runtime: Slow (2000-5000ms) - limited to 50k combinations for feasibility

**Why This Oracle?**
Shows what's possible with unlimited computational resources and perfect scoring. CSP should approach oracle quality while being much faster.

---

## Literature Review

### Existing Approaches to Meal Planning

**1. Recipe Classification Systems**

*Approach:* Binary or multi-class classification of recipes (healthy/unhealthy, suitable/unsuitable)

*Examples:*
- Nutritional label classification (FDA guidelines)
- Diet compatibility tagging systems

*Limitations:*
- No meal plan optimization - just labels individual recipes
- Doesn't handle multi-constraint balancing
- User must manually combine recipes to meet goals

*Our Improvement:* Structured prediction that generates complete, constraint-satisfying meal plans

**2. Calorie Counting Apps**

*Approach:* Simple filtering by calorie ranges, manual user selection

*Examples:*
- MyFitnessPal, Lose It!
- Database lookup + addition

*Limitations:*
- No automated planning - user selects each meal manually
- Ignores protein, diversity, and preference constraints
- Tedious for users (requires daily manual effort)

*Our Improvement:* Automated generation with multi-constraint optimization

**3. Collaborative Filtering Recommendation**

*Approach:* Recommend recipes based on user similarity (other users with similar preferences)

*Examples:*
- "Users who liked this also liked..."
- Matrix factorization for recipe recommendations

*Limitations:*
- No hard constraint guarantees (might recommend allergens)
- Doesn't ensure nutritional goals met
- Requires large user interaction data

*Our Improvement:* Hard constraint satisfaction with CSP guarantees

**4. Linear Programming Optimization**

*Approach:* Formulate as LP with nutritional constraints, minimize cost or maximize utility

*Examples:*
- Classic "diet problem" (Stigler, 1945)
- Nutritional optimization in hospitals

*Limitations:*
- Assumes continuous quantities (can eat 0.73 servings)
- Poor ingredient diversity (tends to select same foods repeatedly)
- Doesn't model discrete recipe selection well

*Our Improvement:* Discrete CSP with explicit diversity constraints

### Our Approach: Classical AI Planning

**Positioning:**

This project uses **Constraint Satisfaction (CSP)** with **heuristic search** - classical AI techniques taught in introductory AI courses. This differs from modern machine learning approaches in important ways:

**Advantages of CSP:**
- Guaranteed constraint satisfaction (hard constraints never violated)
- Interpretable reasoning (can explain why each recipe chosen)
- No training data required (works with fixed recipe database)
- Transparent to users (dietitians can verify logic)

**Complementary to ML:**
Could combine CSP constraints with learned preferences:
- Use CSP to ensure hard constraints (allergies, calories, protein)
- Use learned model to predict user preferences (soft constraints)
- Best of both: safety guarantees + personalization

**Why Not Pure ML?**
- Hard constraints difficult to guarantee with neural networks
- Insufficient training data (10 users, 200 recipes)
- Black-box models inappropriate for health/safety applications

---


## Setup and Usage *****

### 🌐 Web Application (Recommended)

**Best for everyone:** Use the web browser interface - most user-friendly option!

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

**Features:**
- Beautiful, modern interface
- Works on desktop and mobile
- Real-time results
- Compare different algorithms
- REST API for programmatic access

See [WEB_APP_GUIDE.md](WEB_APP_GUIDE.md) for complete documentation.

### 💻 Interactive CLI (Command Line)

**For terminal users:** Use the interactive command-line interface.

```bash
python interactive_planner.py
```

**What it does:**
- Asks for your dietary preferences (diet type, calories, protein, allergens)
- Generates a personalized 3-meal plan
- Shows nutritional breakdown and quality metrics
- User-friendly menu interface

**Example interaction:**
```
AI MEAL PLANNER - Personalized Daily Meal Plans

MAIN MENU
  1. Create a new meal plan
  2. Try a sample user (Alex - high protein)
  3. Try a sample user (Sarah - vegan)
  4. Try a sample user (Mike - keto)
  5. View all sample users
  6. Exit

Enter choice: 1

What's your name? John
What type of diet do you follow?
  1. Balanced  2. High-Protein  3. Vegan  ...
Enter number: 2

Your daily calorie target? 1800
Minimum daily protein goal (grams)? 100

[Generates personalized meal plan with nutrition info]
```

### Requirements

- Python 3.9+
- pandas >= 1.3.0
- numpy >= 1.21.0
- scikit-learn >= 0.24.0

### Installation

```bash
# Clone or download the project
cd meal-planner

# Install dependencies
pip install -r requirements.txt
```

### Quick Start

**1. Verify Setup:**
```bash
python test_setup.py
```

This runs 5 tests to confirm data loads correctly and algorithms work.

**2. Run Full Experiments:**
```bash
python experiments/run_experiments.py
```

This executes all 5 experiments and saves results to `experiment_results.csv`.
**Expected runtime:** 3-5 minutes

**Output:**
- Console: Experiment summaries and sample meal plans
- File: `experiment_results.csv` with detailed metrics

### Usage Examples

**Generate Meal Plan for User:**

```python
from src.data_loader import load_recipes, load_users
from src.csp_planner import greedy_csp_planner
from src.metrics import print_plan_evaluation

# Load data
recipes = load_recipes('data/recipes.csv')
users = load_users('data/test_users.json')

# Select user
user = users[0]  # Alex

# Generate plan
plan = greedy_csp_planner(recipes, user, top_k=15)

# Display results
if plan:
    print_plan_evaluation(plan, user, "CSP Planner")
else:
    print(f"Failed to generate plan for {user.name}")
```

**Run Individual Algorithms:**

```python
from src.baseline import random_baseline_planner
from src.oracle import oracle_planner

# Baseline
baseline_plan = random_baseline_planner(recipes, user, seed=42)

# Oracle (limited for performance)
oracle_plan = oracle_planner(recipes, user, max_combinations=10000)

# CSP
csp_plan = greedy_csp_planner(recipes, user, top_k=15)
```

**Custom Configuration:**

```python
from src.csp_planner import csp_planner_with_config

# Experiment with different beam widths
plan_k5 = csp_planner_with_config(recipes, user, top_k=5)
plan_k30 = csp_planner_with_config(recipes, user, top_k=30)
```

### Project Structure

```
meal-planner/
├── data/
│   ├── recipes.csv              # 200 recipes with nutritional data
│   └── test_users.json          # 10 test users with constraints
├── src/
│   ├── data_loader.py           # Load and parse data
│   ├── constraints.py           # Hard constraint checking
│   ├── heuristics.py            # Heuristic function and greedy selection
│   ├── baseline.py              # Random baseline algorithm
│   ├── oracle.py                # Exhaustive search oracle
│   ├── csp_planner.py           # Main CSP algorithm
│   └── metrics.py               # Evaluation metrics
├── experiments/
│   └── run_experiments.py       # Comprehensive experiments
├── requirements.txt             # Python dependencies
├── test_setup.py                # Quick verification script
└── README.md                    # This file
```

### CodaLab Submission

To submit to CodaLab:

1. Ensure `requirements.txt` is complete
2. Verify `python test_setup.py` passes
3. Run `python experiments/run_experiments.py` locally
4. Package entire `meal-planner/` directory
5. Submit with execution command: `python experiments/run_experiments.py`

**Expected Evaluation Time:** <5 minutes
**Expected Output:** `experiment_results.csv` with all metrics

---

## References

- Russell, S. & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Chapters 6-7 (Constraint Satisfaction, Search).
- Kaggle Recipe Ingredients Dataset: https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions
- USDA FoodData Central: https://fdc.nal.usda.gov/
- Dietary Guidelines for Americans (2020-2025): https://www.dietaryguidelines.gov/

---

**End of README**
>>>>>>> 6692f3f (Initial commit)
