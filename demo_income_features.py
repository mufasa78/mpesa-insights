"""
Demo script showing the new income tracking features
Run this to see examples of the income insights your users will get
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from income_tracker import IncomeTracker

def create_sample_data_with_income():
    """Create sample M-Pesa transaction data with proper income tracking"""
    np.random.seed(42)
    
    # Generate 6 months of sample data
    start_date = datetime.now() - timedelta(days=180)
    dates = pd.date_range(start_date, periods=200, freq='D')
    
    transactions = []
    
    # Income transactions
    income_sources = {
        'Salary Payment from ABC Company': {'amount': 85000, 'frequency': 30},  # Monthly salary
        'Freelance Web Design Payment': {'amount': 25000, 'frequency': 45},    # Irregular freelance
        'Rental Income - Apartment': {'amount': 15000, 'frequency': 30},       # Monthly rent
        'Business Sales - Online Store': {'amount': 8000, 'frequency': 7},     # Weekly business income
        'Investment Dividend': {'amount': 3000, 'frequency': 90},              # Quarterly dividends
    }
    
    # Expense categories
    expense_categories = {
        'Food': {'avg': -800, 'std': 300, 'freq': 0.8},
        'Transport': {'avg': -200, 'std': 100, 'freq': 0.6},
        'Utilities': {'avg': -1500, 'std': 200, 'freq': 0.1},
        'Entertainment': {'avg': -1200, 'std': 500, 'freq': 0.3},
        'Shopping': {'avg': -2000, 'std': 800, 'freq': 0.2},
        'Health': {'avg': -800, 'std': 400, 'freq': 0.1}
    }
    
    # Generate income transactions
    for i, date in enumerate(dates):
        for source, params in income_sources.items():
            if i % params['frequency'] == 0:  # Based on frequency
                # Add some variation to income amounts
                variation = np.random.normal(1.0, 0.1)  # ±10% variation
                amount = params['amount'] * max(0.5, variation)  # Ensure positive
                
                transactions.append({
                    'Date': date,
                    'Details': source,
                    'Amount': amount,
                    'Category': 'Income',
                    'Type': 'Receive Money'
                })
        
        # Generate expense transactions
        for category, params in expense_categories.items():
            if np.random.random() < params['freq']:
                amount = np.random.normal(params['avg'], params['std'])
                
                # Category-specific transaction details
                if category == 'Food':
                    details = np.random.choice(['Naivas Supermarket', 'KFC', 'Local Restaurant', 'Carrefour'])
                elif category == 'Transport':
                    details = np.random.choice(['Uber Trip', 'Matatu Fare', 'Fuel Station', 'Parking'])
                elif category == 'Utilities':
                    details = np.random.choice(['KPLC Bill', 'Safaricom Postpaid', 'Water Bill'])
                elif category == 'Entertainment':
                    details = np.random.choice(['Cinema Ticket', 'Netflix Subscription', 'Club Entry'])
                elif category == 'Shopping':
                    details = np.random.choice(['Jumia Purchase', 'Electronics Store', 'Clothing Store'])
                else:
                    details = np.random.choice(['Hospital Bill', 'Pharmacy', 'Medical Checkup'])
                
                transactions.append({
                    'Date': date,
                    'Details': details,
                    'Amount': amount,
                    'Category': category,
                    'Type': 'Expense'
                })
    
    return pd.DataFrame(transactions)

def demo_income_tracking(df):
    """Demonstrate income tracking features"""
    print("💰 INCOME TRACKING DEMO")
    print("=" * 50)
    
    tracker = IncomeTracker()
    income_analysis = tracker.analyze_income_patterns(df)
    
    print(f"\n📊 INCOME OVERVIEW:")
    print(f"• Total Income: KSh {income_analysis['total_income']:,.2f}")
    print(f"• Monthly Average: KSh {income_analysis['monthly_average']:,.2f}")
    print(f"• Income Stability: {income_analysis['income_stability']['description']}")
    print(f"• Growth Trend: {income_analysis['growth_trend']['trend']}")
    
    print(f"\n💼 INCOME SOURCES:")
    for source, amount in income_analysis['income_sources'].items():
        percentage = (amount / income_analysis['total_income'] * 100) if income_analysis['total_income'] > 0 else 0
        print(f"• {source}: KSh {amount:,.2f} ({percentage:.1f}%)")
    
    print(f"\n💡 INCOME RECOMMENDATIONS:")
    for rec in income_analysis['recommendations']:
        print(f"• {rec}")

def demo_savings_rate_calculation(df):
    """Demonstrate accurate savings rate calculation"""
    print("\n\n💰 SAVINGS RATE ANALYSIS")
    print("=" * 50)
    
    tracker = IncomeTracker()
    savings_data = tracker.calculate_savings_rate(df)
    
    print(f"\n📈 FINANCIAL SUMMARY:")
    print(f"• Monthly Income: KSh {savings_data['monthly_income']:,.2f}")
    print(f"• Monthly Expenses: KSh {savings_data['monthly_expenses']:,.2f}")
    print(f"• Monthly Savings: KSh {savings_data['monthly_savings']:,.2f}")
    print(f"• Savings Rate: {savings_data['savings_rate']:.1f}%")
    print(f"• Status: {savings_data['status']}")
    
    # Provide context
    if savings_data['savings_rate'] >= 20:
        print("🎉 Excellent! You're meeting the recommended 20% savings rate.")
    elif savings_data['savings_rate'] >= 10:
        print("👍 Good savings rate, but try to reach 20% for optimal financial health.")
    elif savings_data['savings_rate'] > 0:
        print("⚠️ Your savings rate is below recommended levels. Consider reducing expenses.")
    else:
        print("🚨 You're spending more than you earn. Immediate action needed!")

def demo_income_improvement_suggestions(df):
    """Demonstrate income improvement suggestions"""
    print("\n\n📈 INCOME IMPROVEMENT SUGGESTIONS")
    print("=" * 50)
    
    tracker = IncomeTracker()
    income_analysis = tracker.analyze_income_patterns(df)
    suggestions = tracker.suggest_income_improvements(income_analysis)
    
    print(f"\n💡 PERSONALIZED SUGGESTIONS:")
    for suggestion in suggestions:
        print(f"\n🎯 {suggestion['category']}:")
        print(f"   Suggestion: {suggestion['suggestion']}")
        print(f"   Potential Impact: {suggestion['potential_impact']}")
        print(f"   Effort Level: {suggestion['effort']}")
        print(f"   Timeframe: {suggestion['timeframe']}")

def demo_financial_health_with_income(df):
    """Show how income tracking improves financial health analysis"""
    print("\n\n🏥 FINANCIAL HEALTH WITH INCOME DATA")
    print("=" * 50)
    
    tracker = IncomeTracker()
    savings_data = tracker.calculate_savings_rate(df)
    
    print(f"\n📊 KEY FINANCIAL HEALTH INDICATORS:")
    
    # Income stability
    income_analysis = tracker.analyze_income_patterns(df)
    stability = income_analysis['income_stability']
    print(f"• Income Stability: {stability['description']} (Score: {stability['score']:.2f}/1.00)")
    
    # Savings rate health
    savings_rate = savings_data['savings_rate']
    if savings_rate >= 20:
        savings_health = "Excellent"
    elif savings_rate >= 10:
        savings_health = "Good"
    elif savings_rate >= 5:
        savings_health = "Fair"
    elif savings_rate > 0:
        savings_health = "Poor"
    else:
        savings_health = "Critical"
    
    print(f"• Savings Health: {savings_health} ({savings_rate:.1f}% savings rate)")
    
    # Income diversification
    num_sources = len(income_analysis['income_sources'])
    if num_sources >= 3:
        diversification = "Well Diversified"
    elif num_sources == 2:
        diversification = "Moderately Diversified"
    else:
        diversification = "Single Source Risk"
    
    print(f"• Income Diversification: {diversification} ({num_sources} sources)")
    
    # Emergency fund estimate
    monthly_expenses = savings_data['monthly_expenses']
    current_savings = savings_data['monthly_savings'] * 6  # Rough estimate
    emergency_months = current_savings / monthly_expenses if monthly_expenses > 0 else 0
    
    print(f"• Emergency Fund Coverage: {emergency_months:.1f} months (target: 3-6 months)")

def main():
    """Run the complete income tracking demo"""
    print("🚀 INCOME TRACKING FEATURES DEMO")
    print("=" * 60)
    print("This demo shows how income tracking enhances financial analysis!")
    
    # Create sample data with proper income tracking
    df = create_sample_data_with_income()
    print(f"\n📊 Generated {len(df)} transactions with income tracking over 6 months")
    
    # Show income vs expense breakdown
    income_total = df[df['Amount'] > 0]['Amount'].sum()
    expense_total = df[df['Amount'] < 0]['Amount'].sum()
    print(f"💰 Total Income: KSh {income_total:,.2f}")
    print(f"💸 Total Expenses: KSh {abs(expense_total):,.2f}")
    print(f"💵 Net Savings: KSh {income_total + expense_total:,.2f}")
    
    # Run all demos
    demo_income_tracking(df)
    demo_savings_rate_calculation(df)
    demo_income_improvement_suggestions(df)
    demo_financial_health_with_income(df)
    
    print("\n\n🎉 INCOME TRACKING DEMO COMPLETE!")
    print("With proper income tracking, users get:")
    print("• Accurate savings rate calculations")
    print("• Better budget recommendations")
    print("• Income improvement suggestions")
    print("• More precise financial health scores")
    print("• Realistic goal setting based on actual income")

if __name__ == "__main__":
    main()