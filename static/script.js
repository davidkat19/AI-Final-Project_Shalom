// AI Meal Planner - Client-side JavaScript

// Global chart variables
let macroChart = null;
let targetChart = null;

// Handle form submission
document.getElementById('mealPlanForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    // Hide previous results/errors
    document.getElementById('results').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    document.getElementById('loading').style.display = 'block';

    // Collect form data
    const formData = {
        name: document.getElementById('name').value,
        diet_type: document.getElementById('diet_type').value,
        calorie_target: parseFloat(document.getElementById('calorie_target').value),
        protein_min: parseFloat(document.getElementById('protein_min').value),
        allergens: document.getElementById('allergens').value.split(',').map(s => s.trim()).filter(s => s),
        preferences: document.getElementById('preferences').value.split(',').map(s => s.trim()).filter(s => s),
        algorithm: document.getElementById('algorithm').value
    };

    try {
        // Call API
        const response = await fetch('/api/generate-plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        // Hide loading
        document.getElementById('loading').style.display = 'none';

        if (data.success) {
            displayResults(data);
        } else {
            displayError(data);
        }

    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        displayError({
            error: 'Network error: ' + error.message,
            suggestions: ['Check your internet connection', 'Ensure the server is running']
        });
    }
});

// Display results
function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.style.display = 'block';

    // User Info
    const userInfo = `
        <p><strong>Plan for:</strong> ${data.user.name}</p>
        <p><strong>Diet:</strong> ${data.user.diet_type.replace('-', ' ').toUpperCase()}</p>
        <p><strong>Target:</strong> ${data.user.calorie_target} cal, ${data.user.protein_min}g protein</p>
        ${data.user.allergens.length > 0 ? `<p><strong>Avoiding:</strong> ${data.user.allergens.join(', ')}</p>` : ''}
    `;
    document.getElementById('userInfo').innerHTML = userInfo;

    // Meals
    const mealsHTML = data.meals.map((meal, index) => `
        <div class="meal-card">
            <h3>Meal ${index + 1}: ${meal.name}</h3>
            <div class="meal-nutrition">
                <div class="nutrition-item">
                    <div class="nutrition-value">${Math.round(meal.calories)}</div>
                    <div class="nutrition-label">Calories</div>
                </div>
                <div class="nutrition-item">
                    <div class="nutrition-value">${Math.round(meal.protein)}g</div>
                    <div class="nutrition-label">Protein</div>
                </div>
                <div class="nutrition-item">
                    <div class="nutrition-value">${Math.round(meal.carbs)}g</div>
                    <div class="nutrition-label">Carbs</div>
                </div>
                <div class="nutrition-item">
                    <div class="nutrition-value">${Math.round(meal.fat)}g</div>
                    <div class="nutrition-label">Fat</div>
                </div>
            </div>
            <div class="meal-ingredients">
                <strong>Ingredients:</strong>
                ${meal.ingredients.map(ing => `<span class="ingredient-tag">${ing}</span>`).join('')}
            </div>
        </div>
    `).join('');
    document.getElementById('meals').innerHTML = mealsHTML;

    // Totals
    const totals = data.totals;
    const user = data.user;
    const calDiff = Math.round(totals.calories - user.calorie_target);
    const proteinDiff = Math.round(totals.protein - user.protein_min);

    const macroCalories = (totals.protein * 4) + (totals.carbs * 4) + (totals.fat * 9);
    const proteinPct = Math.round((totals.protein * 4 / macroCalories) * 100);
    const carbsPct = Math.round((totals.carbs * 4 / macroCalories) * 100);
    const fatPct = Math.round((totals.fat * 9 / macroCalories) * 100);

    const totalsHTML = `
        <h3>Daily Totals</h3>
        <div class="totals-grid">
            <div class="total-item">
                <div class="total-label">Calories</div>
                <div class="total-value">${Math.round(totals.calories)}</div>
                <div class="total-target">Target: ${user.calorie_target} (${calDiff >= 0 ? '+' : ''}${calDiff})</div>
            </div>
            <div class="total-item">
                <div class="total-label">Protein</div>
                <div class="total-value">${Math.round(totals.protein)}g</div>
                <div class="total-target">Minimum: ${user.protein_min}g (${proteinDiff >= 0 ? '+' : ''}${proteinDiff}g)</div>
            </div>
            <div class="total-item">
                <div class="total-label">Carbs</div>
                <div class="total-value">${Math.round(totals.carbs)}g</div>
                <div class="total-target">${carbsPct}% of calories</div>
            </div>
            <div class="total-item">
                <div class="total-label">Fat</div>
                <div class="total-value">${Math.round(totals.fat)}g</div>
                <div class="total-target">${fatPct}% of calories</div>
            </div>
        </div>
        <p style="text-align: center; margin-top: 15px; color: #666;">
            Macros: ${proteinPct}% protein, ${carbsPct}% carbs, ${fatPct}% fat
        </p>
    `;
    document.getElementById('totals').innerHTML = totalsHTML;

    // Metrics
    const metrics = data.metrics;
    const algorithmName = data.algorithm === 'csp' ? 'CSP' :
                         data.algorithm === 'baseline' ? 'Baseline' : 'Oracle';

    const metricsHTML = `
        <h3>Plan Quality Metrics</h3>
        <div class="metrics-grid">
            <div class="metric-item">
                <div class="metric-label">Constraint Satisfaction</div>
                <div class="metric-value">${Math.round(metrics.constraint_satisfaction)}%</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Calorie Error</div>
                <div class="metric-value">${Math.round(metrics.calorie_error)}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Diversity Score</div>
                <div class="metric-value">${Math.round(metrics.diversity_score)}/100</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Balance Score</div>
                <div class="metric-value">${Math.round(metrics.balance_score)}/100</div>
            </div>
        </div>
        <div style="text-align: center; margin-top: 15px;">
            <span class="success-badge ${metrics.success ? 'success' : 'warning'}">
                ${metrics.success ? '✓ Excellent Plan' : '⚠ Acceptable Plan'}
            </span>
        </div>
        <div class="runtime">
            Generated in ${data.runtime_ms.toFixed(1)}ms using ${algorithmName} algorithm
        </div>
    `;
    document.getElementById('metrics').innerHTML = metricsHTML;

    // Create charts
    createMacroChart(totals);
    createTargetChart(data);

    // Show algorithm comparison
    document.getElementById('comparisonSection').style.display = 'block';

    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Create macro distribution pie chart
function createMacroChart(totals) {
    const ctx = document.getElementById('macroChart');

    // Destroy existing chart
    if (macroChart) {
        macroChart.destroy();
    }

    // Calculate macro calories
    const proteinCals = totals.protein * 4;
    const carbsCals = totals.carbs * 4;
    const fatCals = totals.fat * 9;

    macroChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Protein', 'Carbs', 'Fat'],
            datasets: [{
                data: [proteinCals, carbsCals, fatCals],
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(76, 175, 80, 0.8)',
                    'rgba(255, 193, 7, 0.8)'
                ],
                borderColor: [
                    'rgba(102, 126, 234, 1)',
                    'rgba(76, 175, 80, 1)',
                    'rgba(255, 193, 7, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            size: 12,
                            family: 'Poppins'
                        },
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} cal (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Create target achievement bar chart
function createTargetChart(data) {
    const ctx = document.getElementById('targetChart');

    // Destroy existing chart
    if (targetChart) {
        targetChart.destroy();
    }

    const totals = data.totals;
    const user = data.user;
    const metrics = data.metrics;

    // Calculate percentages
    const calorieAchievement = (totals.calories / user.calorie_target) * 100;
    const proteinAchievement = (totals.protein / user.protein_min) * 100;
    const constraintAchievement = metrics.constraint_satisfaction;
    const diversityAchievement = metrics.diversity_score;

    targetChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Calories', 'Protein', 'Constraints', 'Diversity'],
            datasets: [{
                label: 'Achievement %',
                data: [
                    Math.min(calorieAchievement, 120),
                    Math.min(proteinAchievement, 150),
                    constraintAchievement,
                    diversityAchievement
                ],
                backgroundColor: [
                    calorieAchievement >= 90 && calorieAchievement <= 110 ? 'rgba(76, 175, 80, 0.7)' : 'rgba(255, 152, 0, 0.7)',
                    proteinAchievement >= 100 ? 'rgba(76, 175, 80, 0.7)' : 'rgba(255, 152, 0, 0.7)',
                    constraintAchievement >= 80 ? 'rgba(76, 175, 80, 0.7)' : 'rgba(244, 67, 54, 0.7)',
                    diversityAchievement >= 40 ? 'rgba(76, 175, 80, 0.7)' : 'rgba(255, 152, 0, 0.7)'
                ],
                borderColor: [
                    calorieAchievement >= 90 && calorieAchievement <= 110 ? 'rgba(76, 175, 80, 1)' : 'rgba(255, 152, 0, 1)',
                    proteinAchievement >= 100 ? 'rgba(76, 175, 80, 1)' : 'rgba(255, 152, 0, 1)',
                    constraintAchievement >= 80 ? 'rgba(76, 175, 80, 1)' : 'rgba(244, 67, 54, 1)',
                    diversityAchievement >= 40 ? 'rgba(76, 175, 80, 1)' : 'rgba(255, 152, 0, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 120,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        },
                        font: {
                            family: 'Poppins'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        font: {
                            family: 'Poppins'
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });
}

// Display error
function displayError(data) {
    const errorDiv = document.getElementById('error');
    errorDiv.style.display = 'block';

    document.getElementById('errorMessage').textContent = data.error;

    if (data.suggestions && data.suggestions.length > 0) {
        const suggestionsHTML = `
            <h3>Suggestions:</h3>
            <ul>
                ${data.suggestions.map(s => `<li>${s}</li>`).join('')}
            </ul>
        `;
        document.getElementById('suggestions').innerHTML = suggestionsHTML;
    } else {
        document.getElementById('suggestions').innerHTML = '';
    }

    // Scroll to error
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Load sample user
async function loadSampleUser() {
    try {
        const response = await fetch('/api/sample-users');
        const data = await response.json();

        if (data.users && data.users.length > 0) {
            // Pick a random sample user
            const user = data.users[Math.floor(Math.random() * data.users.length)];

            // Fill form
            document.getElementById('name').value = user.name;
            document.getElementById('diet_type').value = user.diet_type;
            document.getElementById('calorie_target').value = user.calorie_target;
            document.getElementById('protein_min').value = user.protein_min;
            document.getElementById('allergens').value = user.allergens.join(', ');
            document.getElementById('preferences').value = user.preferences.join(', ');

            alert(`Loaded sample user: ${user.name} (${user.diet_type})`);
        }
    } catch (error) {
        alert('Error loading sample users: ' + error.message);
    }
}
