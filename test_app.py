"""
Simple test script to verify the app functionality
"""

import pandas as pd
from datetime import datetime, timedelta
from income_tracker import IncomeTracker
from categorizer import ExpenseCategorizer
from budget_advisor import BudgetAdvisor

def test_basic_functionality():
    """Test basic functionality without Streamlit"""
    print("🧪 Testing M-Pesa Statement Analyzer Components")
    print("=" * 50)
    
    # Create sample data
    sample_data = [
        {'Date': datetime.now() - timedelta(days=30), 'Details': 'Salary Payment', 'Amount': 80000, 'Category': 'Income'},
        {'Date': datetime.now() - timedelta(days=25), 'Details': 'Naivas Supermarket', 'Amount': -5000, 'Category': 'Food'},
        {'Date': datetime.now() - timedelta(days=20), 'Details': 'Uber Trip', 'Amount': -500, 'Category': 'Transport'},
        {'Date': datetime.now() - timedelta(days=15), 'Details': 'KPLC Bill', 'Amount': -3000, 'Category': 'Utilities'},
        {'Date': datetime.now() - timedelta(days=10), 'Details': 'Freelance Payment', 'Amount': 25000, 'Category': 'Income'},
        {'Date': datetime.now() - timedelta(days=5), 'Details': 'Netflix Subscription', 'Amount': -1200, 'Category': 'Entertainment'},
    ]
    
    df = pd.DataFrame(sample_data)
    print(f"✅ Created sample data with {len(df)} transactions")
    
    # Test Income Tracker
    print("\n💰 Testing Income Tracker...")
    income_tracker = IncomeTracker()
    income_analysis = income_tracker.analyze_income_patterns(df)
    
    print(f"   Total Income: KSh {income_analysis['total_income']:,.2f}")
    print(f"   Monthly Average: KSh {income_analysis['monthly_average']:,.2f}")
    print(f"   Income Sources: {len(income_analysis['income_sources'])}")
    
    # Test Savings Rate
    savings_data = income_tracker.calculate_savings_rate(df)
    print(f"   Savings Rate: {savings_data['savings_rate']:.1f}%")
    print(f"   Status: {savings_data['status']}")
    
    # Test Categorizer
    print("\n🏷️ Testing Categorizer...")
    categorizer = ExpenseCategorizer()
    categorized_df = categorizer.categorize_transactions(df)
    categories = categorized_df['Category'].unique()
    print(f"   Categories found: {', '.join(categories)}")
    
    # Test Budget Advisor
    print("\n🎯 Testing Budget Advisor...")
    budget_advisor = BudgetAdvisor()
    insights = budget_advisor.analyze_spending_patterns(df)
    
    print(f"   Overspending categories: {len(insights['overspending_categories'])}")
    print(f"   Savings opportunities: {len(insights['savings_opportunities'])}")
    print(f"   Budget recommendations: {len(insights['budget_recommendations'])}")
    
    print("\n🎉 All components tested successfully!")
    print("The app should work correctly when run with Streamlit.")

if __name__ == "__main__":
    test_basic_functionality()