"""
Test script to verify the budget coach and benchmarks fix works correctly
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
            # Make some categories overspend
            if category == 'Entertainment':
                amount = -np.random.randint(2000, 8000)  # Higher entertainment spending
            elif category == 'Food':
                amount = -np.random.randint(1000, 6000)  # Higher food spending
            else:
                amount = -np.random.randint(100, 3000)
            
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
            'Amount': 80000,  # 80k monthly income
            'Category': 'Income',
            'Type': 'Credit'
        })
    
    return pd.DataFrame(transactions)

def test_budget_advisor():
    """Test the BudgetAdvisor functionality"""
    print("🧪 Testing Budget Advisor...")
    
    try:
        from budget_advisor import BudgetAdvisor
        from income_tracker import IncomeTracker
        
        # Create test data
        df = create_test_data()
        
        # Initialize components
        budget_advisor = BudgetAdvisor()
        income_tracker = IncomeTracker()
        
        # Test budget analysis
        budget_insights = budget_advisor.analyze_spending_patterns(df)
        print("✅ Budget analysis completed")
        
        # Check insights structure
        expected_keys = ['overspending_categories', 'spending_trends', 'unusual_transactions', 
                        'savings_opportunities', 'budget_recommendations']
        
        for key in expected_keys:
            if key in budget_insights:
                print(f"✅ Found {key}: {len(budget_insights[key])} items")
            else:
                print(f"❌ Missing {key}")
        
        # Test savings calculation
        savings_data = income_tracker.calculate_savings_rate(df)
        print(f"✅ Savings rate calculated: {savings_data['savings_rate']:.1f}%")
        
        # Test expense cutting tips
        tips = budget_advisor.generate_expense_cutting_tips(budget_insights)
        print(f"✅ Generated {len(tips)} expense cutting tips")
        
        return True
        
    except Exception as e:
        print(f"❌ Budget Advisor test failed: {e}")
        return False

def test_spending_comparator():
    """Test the SpendingComparator functionality"""
    print("\n🧪 Testing Spending Comparator...")
    
    try:
        from spending_comparator import SpendingComparator
        from income_tracker import IncomeTracker
        
        # Create test data
        df = create_test_data()
        
        # Initialize components
        comparator = SpendingComparator()
        income_tracker = IncomeTracker()
        
        # Get income for benchmarking
        savings_data = income_tracker.calculate_savings_rate(df)
        monthly_income = savings_data['monthly_income']
        print(f"✅ Monthly income calculated: KSh {monthly_income:,.0f}")
        
        # Test benchmark comparison
        comparison_data = comparator.compare_with_benchmarks(df, monthly_income)
        print("✅ Benchmark comparison completed")
        
        # Check comparison structure
        expected_keys = ['income_bracket', 'category_comparison', 'spending_score']
        for key in expected_keys:
            if key in comparison_data:
                print(f"✅ Found {key}")
            else:
                print(f"❌ Missing {key}")
        
        # Test spending efficiency
        efficiency_data = comparator.analyze_spending_efficiency(df)
        print("✅ Spending efficiency analysis completed")
        
        efficiency_score = efficiency_data.get('efficiency_score', 0)
        print(f"✅ Efficiency score: {efficiency_score:.1f}%")
        
        # Test cost-saving alternatives
        alternatives = comparator.find_cost_saving_alternatives(df)
        print(f"✅ Found {len(alternatives)} cost-saving alternatives")
        
        return True
        
    except Exception as e:
        print(f"❌ Spending Comparator test failed: {e}")
        return False

def test_integration():
    """Test the integration of both components"""
    print("\n🧪 Testing Integration...")
    
    try:
        df = create_test_data()
        
        # Test the data processing that would happen in the app
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        print(f"✅ Processed {len(expenses_df)} expense transactions")
        
        # Test category grouping
        category_totals = expenses_df.groupby('Category')['Amount'].sum()
        print(f"✅ Grouped into {len(category_totals)} categories")
        
        # Test percentage calculations
        total_expenses = category_totals.sum()
        for category, amount in category_totals.items():
            percentage = (amount / total_expenses) * 100
            print(f"  • {category}: {percentage:.1f}% (KSh {amount:,.0f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 BUDGET COACH & BENCHMARKS FIX VERIFICATION TEST\n")
    
    # Run all tests
    budget_test = test_budget_advisor()
    comparator_test = test_spending_comparator()
    integration_test = test_integration()
    
    print(f"\n📊 TEST RESULTS:")
    print(f"Budget Advisor: {'✅ PASS' if budget_test else '❌ FAIL'}")
    print(f"Spending Comparator: {'✅ PASS' if comparator_test else '❌ FAIL'}")
    print(f"Integration: {'✅ PASS' if integration_test else '❌ FAIL'}")
    
    if all([budget_test, comparator_test, integration_test]):
        print("\n🎉 All tests passed! Budget Coach and Benchmarks should work correctly!")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")