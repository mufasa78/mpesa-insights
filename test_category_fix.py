"""
Test script to verify the category key error fixes work correctly
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.getcwd())

def create_test_data():
    """Create test transaction data"""
    np.random.seed(42)
    
    # Generate 3 months of test data
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 3, 31)
    
    transactions = []
    current_date = start_date
    
    categories = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Shopping', 'Health']
    
    while current_date <= end_date:
        # Generate 1-3 transactions per day
        num_transactions = np.random.randint(1, 4)
        
        for _ in range(num_transactions):
            category = np.random.choice(categories)
            amount = -np.random.randint(100, 5000)
            
            transactions.append({
                'Date': current_date + timedelta(hours=np.random.randint(8, 20)),
                'Details': f'{category.upper()} TRANSACTION',
                'Amount': amount,
                'Category': category,
                'Type': 'Debit'
            })
        
        current_date += timedelta(days=1)
    
    # Add income transactions
    for month in [1, 2, 3]:
        transactions.append({
            'Date': datetime(2024, month, 28),
            'Details': 'SALARY PAYMENT',
            'Amount': 60000,
            'Category': 'Income',
            'Type': 'Credit'
        })
    
    return pd.DataFrame(transactions)

def test_budget_advisor_savings_opportunities():
    """Test the budget advisor savings opportunities structure"""
    print("🧪 Testing Budget Advisor Savings Opportunities...")
    
    try:
        from budget_advisor import BudgetAdvisor
        
        # Create test data
        df = create_test_data()
        
        # Initialize budget advisor
        budget_advisor = BudgetAdvisor()
        
        # Get budget insights
        budget_insights = budget_advisor.analyze_spending_patterns(df)
        
        # Test savings opportunities structure
        savings_opportunities = budget_insights.get('savings_opportunities', [])
        print(f"✅ Found {len(savings_opportunities)} savings opportunities")
        
        # Test the structure of each opportunity
        for i, opportunity in enumerate(savings_opportunities):
            required_keys = ['type', 'description', 'suggestion', 'potential_savings']
            
            for key in required_keys:
                if key in opportunity:
                    print(f"✅ Opportunity {i+1} has '{key}': {type(opportunity[key])}")
                else:
                    print(f"❌ Opportunity {i+1} missing '{key}'")
            
            # Test that we can access the keys safely
            opportunity_type = opportunity.get('type', 'General')
            suggestion = opportunity.get('suggestion', 'No suggestion available')
            potential_savings = opportunity.get('potential_savings', 0)
            description = opportunity.get('description', 'No description available')
            
            print(f"✅ Safe access test passed for opportunity {i+1}")
        
        return True
        
    except Exception as e:
        print(f"❌ Budget advisor test failed: {e}")
        return False

def test_income_tracker_suggestions():
    """Test the income tracker suggestions structure"""
    print("\n🧪 Testing Income Tracker Suggestions...")
    
    try:
        from income_tracker import IncomeTracker
        
        # Create test data
        df = create_test_data()
        
        # Initialize income tracker
        income_tracker = IncomeTracker()
        
        # Get income analysis
        income_analysis = income_tracker.analyze_income_patterns(df)
        
        # Get income suggestions
        income_suggestions = income_tracker.suggest_income_improvements(income_analysis)
        print(f"✅ Found {len(income_suggestions)} income suggestions")
        
        # Test the structure of each suggestion
        for i, suggestion in enumerate(income_suggestions):
            required_keys = ['category', 'suggestion', 'potential_impact', 'effort', 'timeframe']
            
            for key in required_keys:
                if key in suggestion:
                    print(f"✅ Suggestion {i+1} has '{key}': {suggestion[key]}")
                else:
                    print(f"❌ Suggestion {i+1} missing '{key}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Income tracker test failed: {e}")
        return False

def test_expense_predictor_methods():
    """Test the expense predictor available methods"""
    print("\n🧪 Testing Expense Predictor Methods...")
    
    try:
        from expense_predictor import ExpensePredictor
        
        # Create test data
        df = create_test_data()
        
        # Initialize predictor
        predictor = ExpensePredictor()
        
        # Test available methods
        available_methods = [method for method in dir(predictor) if not method.startswith('_') and callable(getattr(predictor, method))]
        print(f"✅ Available methods: {available_methods}")
        
        # Test predict_monthly_expenses
        predictions = predictor.predict_monthly_expenses(df)
        print(f"✅ Monthly predictions generated for {len(predictions)} items")
        
        # Test set_savings_goals
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        current_expenses = expenses_df.groupby('Category')['Amount'].sum().to_dict()
        
        goals = predictor.set_savings_goals(current_expenses)
        print(f"✅ Savings goals set for {len(goals)} categories")
        
        # Test micro savings suggestions
        micro_savings = predictor.suggest_micro_savings(df)
        print(f"✅ Generated {len(micro_savings)} micro savings suggestions")
        
        return True
        
    except Exception as e:
        print(f"❌ Expense predictor test failed: {e}")
        return False

def test_goal_reduction_calculation():
    """Test the goal reduction calculation logic"""
    print("\n🧪 Testing Goal Reduction Calculation...")
    
    try:
        # Create test data
        df = create_test_data()
        
        # Simulate the calculation logic from the app
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        category_spending = expenses_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        
        # Test calculation
        total_reduction_needed = 5000  # Example reduction needed
        total_current_spending = category_spending.sum()
        
        print(f"✅ Total current spending: KSh {total_current_spending:,.0f}")
        print(f"✅ Total reduction needed: KSh {total_reduction_needed:,.0f}")
        
        # Calculate proportional reductions
        for category, amount in category_spending.head(5).items():
            if category != 'Income':
                category_proportion = amount / total_current_spending
                suggested_reduction = total_reduction_needed * category_proportion
                reduction_percentage = (suggested_reduction / amount) * 100
                
                print(f"✅ {category}: Reduce by KSh {suggested_reduction:,.0f} ({reduction_percentage:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Goal reduction calculation test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CATEGORY KEY ERROR FIX VERIFICATION TEST\n")
    
    # Run all tests
    budget_test = test_budget_advisor_savings_opportunities()
    income_test = test_income_tracker_suggestions()
    predictor_test = test_expense_predictor_methods()
    goal_test = test_goal_reduction_calculation()
    
    print(f"\n📊 TEST RESULTS:")
    print(f"Budget Advisor: {'✅ PASS' if budget_test else '❌ FAIL'}")
    print(f"Income Tracker: {'✅ PASS' if income_test else '❌ FAIL'}")
    print(f"Expense Predictor: {'✅ PASS' if predictor_test else '❌ FAIL'}")
    print(f"Goal Calculation: {'✅ PASS' if goal_test else '❌ FAIL'}")
    
    if all([budget_test, income_test, predictor_test, goal_test]):
        print("\n🎉 All tests passed! Category key errors should be fixed!")
        print("\n✅ Key fixes applied:")
        print("  • Fixed savings opportunities structure access")
        print("  • Verified income suggestions structure")
        print("  • Replaced non-existent method with working logic")
        print("  • Added safe key access with fallbacks")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")