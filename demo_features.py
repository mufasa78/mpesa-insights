"""
Demo script showing the new expense-cutting features
Run this to see examples of the insights your users will get
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from budget_advisor import BudgetAdvisor
from expense_predictor import ExpensePredictor
from spending_comparator import SpendingComparator
from financial_health import FinancialHealthAnalyzer

def create_sample_data():
    """Create sample M-Pesa transaction data for demonstration"""
    np.random.seed(42)
    
    # Generate 3 months of sample data
    start_date = datetime.now() - timedelta(days=90)
    dates = pd.date_range(start_date, periods=150, freq='D')
    
    transactions = []
    
    categories = {
        'Food': {'avg': -800, 'std': 300, 'freq': 0.8},
        'Transport': {'avg': -200, 'std': 100, 'freq': 0.6},
        'Utilities': {'avg': -1500, 'std': 200, 'freq': 0.1},
        'Entertainment': {'avg': -1200, 'std': 500, 'freq': 0.3},
        'Shopping': {'avg': -2000, 'std': 800, 'freq': 0.2},
        'Health': {'avg': -800, 'std': 400, 'freq': 0.1}
    }
    
    # Add some income transactions
    for i, date in enumerate(dates):
        # Random income (salary, business, etc.)
        if i % 30 == 0:  # Monthly salary
            transactions.append({
                'Date': date,
                'Details': 'Salary Payment',
                'Amount': 80000,
                'Category': 'Income',
                'Type': 'Receive Money'
            })
        
        # Daily expenses
        for category, params in categories.items():
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

def demo_budget_advisor(df):
    """Demonstrate budget advisor features"""
    print("🎯 BUDGET ADVISOR DEMO")
    print("=" * 50)
    
    advisor = BudgetAdvisor()
    insights = advisor.analyze_spending_patterns(df)
    
    # Overspending categories
    print("\n⚠️ OVERSPENDING ALERTS:")
    for overspend in insights['overspending_categories'][:3]:
        print(f"• {overspend['category']}: {overspend['current_percentage']:.1f}% of expenses")
        print(f"  Recommended: {overspend['recommended_percentage']:.1f}%")
        print(f"  💰 Potential savings: KSh {overspend['potential_savings']:,.2f}/month")
    
    # Money-saving tips
    print("\n💡 MONEY-SAVING TIPS:")
    tips = advisor.generate_expense_cutting_tips(insights)
    for tip in tips[:3]:
        print(f"• {tip}")
    
    # Savings opportunities
    print("\n🎯 SAVINGS OPPORTUNITIES:")
    for opportunity in insights['savings_opportunities'][:3]:
        print(f"• {opportunity['description']}")
        print(f"  💡 {opportunity['suggestion']}")
        print(f"  💰 Potential savings: KSh {opportunity['potential_savings']:,.2f}")

def demo_expense_predictor(df):
    """Demonstrate expense prediction features"""
    print("\n\n🔮 EXPENSE PREDICTOR DEMO")
    print("=" * 50)
    
    predictor = ExpensePredictor()
    predictions = predictor.predict_monthly_expenses(df)
    
    print("\n📈 NEXT MONTH'S PREDICTIONS:")
    total_predicted = 0
    for category, data in predictions.items():
        print(f"• {category}: KSh {data['predicted_amount']:,.2f}")
        print(f"  Trend: {data['trend']}, Confidence: {data['confidence']*100:.0f}%")
        total_predicted += data['predicted_amount']
    
    print(f"\n💰 Total Predicted: KSh {total_predicted:,.2f}")
    
    # Micro-savings suggestions
    print("\n☕ MICRO-SAVINGS SUGGESTIONS:")
    micro_savings = predictor.suggest_micro_savings(df)
    for suggestion in micro_savings[:3]:
        print(f"• {suggestion['suggestion']}")
        print(f"  💰 Monthly savings: KSh {suggestion['potential_monthly_savings']:,.2f}")
        print(f"  📅 Annual savings: KSh {suggestion['potential_annual_savings']:,.2f}")

def demo_spending_comparator(df):
    """Demonstrate spending comparison features"""
    print("\n\n📊 SPENDING COMPARATOR DEMO")
    print("=" * 50)
    
    comparator = SpendingComparator()
    comparison_data = comparator.compare_with_benchmarks(df)
    
    # Overall score
    score_data = comparison_data['overall_score']
    print(f"\n🎯 FINANCIAL SCORE: {score_data['score']:.0f}/100 (Grade: {score_data['grade']})")
    print(f"📊 Income Bracket: {comparison_data['income_bracket'].title()}")
    print(f"💬 {score_data['message']}")
    
    # Category comparisons
    print("\n📈 CATEGORY COMPARISONS:")
    for category, data in comparison_data['comparisons'].items():
        status_emoji = '🟢' if data['status'] == 'optimal' else '🟡' if data['status'] == 'acceptable' else '🔴'
        print(f"• {category}: {status_emoji} {data['status'].title()}")
        print(f"  Your spending: KSh {data['your_spending']:,.2f}")
        print(f"  Optimal: KSh {data['optimal_spending']:,.2f}")
    
    # Peer insights
    print("\n👥 PEER INSIGHTS:")
    peer_insights = comparator.generate_peer_comparison_insights(comparison_data)
    for insight in peer_insights[:3]:
        print(f"• {insight}")

def demo_financial_health(df):
    """Demonstrate financial health analysis"""
    print("\n\n🏥 FINANCIAL HEALTH DEMO")
    print("=" * 50)
    
    analyzer = FinancialHealthAnalyzer()
    health_data = analyzer.calculate_financial_health_score(df)
    
    print(f"\n🎯 OVERALL HEALTH SCORE: {health_data['overall_score']:.2f}/1.00")
    print(f"📊 Grade: {health_data['grade']}")
    
    print("\n📋 INDIVIDUAL METRICS:")
    for metric, score in health_data['individual_scores'].items():
        print(f"• {metric.replace('_', ' ').title()}: {score:.2f}/1.00")
    
    print("\n💡 HEALTH RECOMMENDATIONS:")
    for rec in health_data['recommendations']:
        print(f"• {rec}")
    
    # Wellness tips
    wellness_tips = analyzer.generate_financial_wellness_tips(df)
    print("\n🌟 WELLNESS TIPS:")
    for tip in wellness_tips[:2]:
        print(f"• {tip['title']}: {tip['description']}")
        print(f"  💡 {tip['recommendation']}")

def main():
    """Run the complete demo"""
    print("🚀 M-PESA EXPENSE CUTTING FEATURES DEMO")
    print("=" * 60)
    print("This demo shows the powerful insights your users will get!")
    
    # Create sample data
    df = create_sample_data()
    print(f"\n📊 Generated {len(df)} sample transactions over 3 months")
    
    # Run all demos
    demo_budget_advisor(df)
    demo_expense_predictor(df)
    demo_spending_comparator(df)
    demo_financial_health(df)
    
    print("\n\n🎉 DEMO COMPLETE!")
    print("These are the types of actionable insights that will help")
    print("your users cut expenses and improve their financial health!")

if __name__ == "__main__":
    main()