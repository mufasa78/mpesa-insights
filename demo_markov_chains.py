"""
Demo script showing the Markov Chain behavior analysis functionality
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

from markov_predictor import MarkovChainPredictor
from behavior_analyzer import BehaviorAnalyzer

def create_realistic_transaction_data():
    """Create realistic transaction data with behavioral patterns"""
    
    # Set random seed for reproducible results
    np.random.seed(42)
    random.seed(42)
    
    transactions = []
    start_date = datetime(2024, 1, 1)
    
    # Define user behavioral patterns
    patterns = {
        'morning': ['Food', 'Transport', 'Airtime'],
        'afternoon': ['Food', 'Shopping', 'Health'],
        'evening': ['Food', 'Entertainment', 'Transport'],
        'night': ['Entertainment', 'Food']
    }
    
    weekday_patterns = {
        'Monday': ['Transport', 'Food', 'Utilities'],
        'Tuesday': ['Food', 'Shopping'],
        'Wednesday': ['Food', 'Health', 'Transport'],
        'Thursday': ['Food', 'Entertainment'],
        'Friday': ['Food', 'Entertainment', 'Shopping'],
        'Saturday': ['Shopping', 'Entertainment', 'Food'],
        'Sunday': ['Food', 'Entertainment']
    }
    
    # Generate 6 months of realistic transactions
    current_date = start_date
    transaction_id = 1
    
    while current_date < start_date + timedelta(days=180):
        # Determine number of transactions for this day (1-5)
        num_transactions = random.choices([1, 2, 3, 4, 5], weights=[10, 30, 35, 20, 5])[0]
        
        day_name = current_date.strftime('%A')
        
        for _ in range(num_transactions):
            # Determine time of day
            hour = random.choices(
                [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
                weights=[5, 10, 15, 10, 15, 10, 15, 10, 5, 5, 5, 5, 3, 2]
            )[0]
            
            # Determine time period
            if 5 <= hour < 12:
                time_period = 'morning'
            elif 12 <= hour < 17:
                time_period = 'afternoon'
            elif 17 <= hour < 21:
                time_period = 'evening'
            else:
                time_period = 'night'
            
            # Choose category based on patterns
            day_categories = weekday_patterns.get(day_name, ['Food', 'Transport'])
            time_categories = patterns.get(time_period, ['Food'])
            
            # Combine and weight the categories
            all_categories = day_categories + time_categories
            category = random.choice(all_categories)
            
            # Generate realistic transaction details and amounts
            details, amount = generate_transaction_details(category, day_name, time_period)
            
            # Add some income transactions
            if random.random() < 0.05:  # 5% chance of income
                if day_name == 'Friday' and random.random() < 0.8:  # Salary on Friday
                    details = "SALARY PAYMENT FROM TECH CORP LTD"
                    amount = 75000
                    category = "Income"
                elif random.random() < 0.3:  # Freelance income
                    details = "FREELANCE PAYMENT CLIENT ABC"
                    amount = random.randint(15000, 35000)
                    category = "Income"
                else:  # Other income
                    details = "BUSINESS PAYMENT RECEIVED"
                    amount = random.randint(5000, 20000)
                    category = "Income"
            
            transaction_time = current_date.replace(hour=hour, minute=random.randint(0, 59))
            
            transactions.append({
                'Date': transaction_time,
                'Details': details,
                'Amount': amount if category == 'Income' else -amount,
                'Category': category,
                'Type': 'Credit' if amount > 0 else 'Debit'
            })
            
            transaction_id += 1
        
        current_date += timedelta(days=1)
    
    # Add some anomalous transactions
    anomaly_transactions = [
        {
            'Date': start_date + timedelta(days=45),
            'Details': 'EXPENSIVE ELECTRONICS PURCHASE',
            'Amount': -85000,
            'Category': 'Shopping',
            'Type': 'Debit'
        },
        {
            'Date': start_date + timedelta(days=90),
            'Details': 'LATE NIGHT GAMBLING',
            'Amount': -25000,
            'Category': 'Entertainment',
            'Type': 'Debit'
        },
        {
            'Date': start_date + timedelta(days=120),
            'Details': 'EMERGENCY MEDICAL BILL',
            'Amount': -45000,
            'Category': 'Health',
            'Type': 'Debit'
        }
    ]
    
    transactions.extend(anomaly_transactions)
    
    # Convert to DataFrame and sort by date
    df = pd.DataFrame(transactions)
    df = df.sort_values('Date').reset_index(drop=True)
    
    return df

def generate_transaction_details(category, day_name, time_period):
    """Generate realistic transaction details and amounts"""
    
    details_map = {
        'Food': {
            'morning': [('BREAKFAST AT JAVA HOUSE', 800), ('NAIVAS GROCERIES', 2500), ('MILK AND BREAD', 300)],
            'afternoon': [('LUNCH AT KFC', 1200), ('CARREFOUR SHOPPING', 4500), ('RESTAURANT BILL', 1800)],
            'evening': [('DINNER AT PIZZA INN', 2200), ('UBER EATS DELIVERY', 1500), ('GROCERY SHOPPING', 3200)],
            'night': [('LATE NIGHT SNACKS', 500), ('24HR SUPERMARKET', 800)]
        },
        'Transport': {
            'morning': [('UBER TO OFFICE', 450), ('MATATU FARE', 100), ('FUEL STATION', 3000)],
            'afternoon': [('TAXI RIDE', 600), ('BUS FARE', 80), ('PARKING FEE', 200)],
            'evening': [('UBER HOME', 520), ('MATATU FARE', 120), ('FUEL TOP UP', 2000)],
            'night': [('LATE NIGHT TAXI', 800), ('UBER RIDE', 650)]
        },
        'Entertainment': {
            'morning': [('GYM MEMBERSHIP', 3000), ('SPORTS BETTING', 500)],
            'afternoon': [('CINEMA TICKET', 800), ('GAMING', 1200)],
            'evening': [('BAR BILL', 2500), ('CLUB ENTRY', 1000), ('MOVIE NIGHT', 1500)],
            'night': [('NIGHTCLUB BILL', 4000), ('LATE NIGHT ENTERTAINMENT', 2000)]
        },
        'Shopping': {
            'morning': [('PHARMACY PURCHASE', 800), ('BOOKSHOP', 1500)],
            'afternoon': [('CLOTHING STORE', 3500), ('ELECTRONICS SHOP', 8000), ('JUMIA ORDER', 2200)],
            'evening': [('SUPERMARKET SHOPPING', 4200), ('FASHION STORE', 2800)],
            'night': [('ONLINE SHOPPING', 1800)]
        },
        'Utilities': [
            ('KPLC ELECTRICITY BILL', 2800),
            ('SAFARICOM POSTPAID', 1500),
            ('ZUKU INTERNET', 3500),
            ('NAIROBI WATER', 1200),
            ('DSTV SUBSCRIPTION', 2200)
        ],
        'Health': [
            ('HOSPITAL VISIT', 3500),
            ('PHARMACY MEDICINE', 1200),
            ('DENTAL CHECKUP', 4000),
            ('LAB TESTS', 2500),
            ('NHIF CONTRIBUTION', 1500)
        ],
        'Airtime': [
            ('SAFARICOM AIRTIME', 500),
            ('DATA BUNDLE', 1000),
            ('AIRTEL AIRTIME', 300),
            ('INTERNET BUNDLE', 1500)
        ]
    }
    
    if category in ['Utilities', 'Health', 'Airtime']:
        detail, amount = random.choice(details_map[category])
    else:
        time_options = details_map[category].get(time_period, details_map[category]['afternoon'])
        detail, base_amount = random.choice(time_options)
        # Add some variation to amounts
        amount = base_amount + random.randint(-int(base_amount*0.2), int(base_amount*0.3))
    
    return detail, max(amount, 50)  # Minimum amount of 50

def demo_markov_training():
    """Demo Markov Chain training process"""
    print("=== DEMO: Markov Chain Training ===\n")
    
    # Create sample data
    df = create_realistic_transaction_data()
    print(f"Created {len(df)} transactions over 6 months")
    print(f"Categories: {df['Category'].unique()}")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    
    # Initialize and train Markov model
    markov_model = MarkovChainPredictor(order=2)
    markov_model.train(df)
    
    # Show model statistics
    stats = markov_model.get_model_stats()
    print(f"\nModel Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print()

def demo_behavior_prediction():
    """Demo behavior prediction capabilities"""
    print("=== DEMO: Behavior Prediction ===\n")
    
    # Create and train model
    df = create_realistic_transaction_data()
    markov_model = MarkovChainPredictor(order=2)
    markov_model.train(df)
    
    # Get a recent state for prediction
    df_with_states = markov_model.create_states(df)
    recent_state = df_with_states.iloc[-1]['State_Sequence']
    
    print(f"Current state: {recent_state}")
    print("\nNext transaction predictions:")
    
    predictions = markov_model.predict_next_transaction(recent_state, n_predictions=5)
    
    for i, pred in enumerate(predictions, 1):
        print(f"{i}. Category: {pred['category']}")
        print(f"   Probability: {pred['probability']:.1%}")
        print(f"   Confidence: {pred['confidence']}")
        print(f"   Amount Range: {pred['amount_range']}")
        print(f"   Time Period: {pred['time_period']}")
        print()

def demo_spending_sequences():
    """Demo spending sequence prediction"""
    print("=== DEMO: Spending Sequence Prediction ===\n")
    
    # Create and train model
    df = create_realistic_transaction_data()
    markov_model = MarkovChainPredictor(order=2)
    markov_model.train(df)
    
    # Predict sequences for different starting categories
    categories = ['Food', 'Transport', 'Entertainment']
    
    for category in categories:
        print(f"Starting with {category}:")
        sequences = markov_model.predict_spending_sequence(category, sequence_length=4)
        
        if sequences:
            sequence_data = sequences[0]
            sequence = sequence_data['sequence']
            probability = sequence_data['overall_probability']
            
            sequence_str = " → ".join(sequence)
            print(f"  Likely sequence: {sequence_str}")
            print(f"  Overall probability: {probability:.1%}")
        print()

def demo_anomaly_detection():
    """Demo anomaly detection"""
    print("=== DEMO: Anomaly Detection ===\n")
    
    # Create and train model
    df = create_realistic_transaction_data()
    markov_model = MarkovChainPredictor(order=2)
    markov_model.train(df)
    
    # Detect anomalies
    anomalies = markov_model.detect_anomalies(df, threshold=0.1)
    
    print(f"Detected {len(anomalies)} anomalous transactions:")
    print(f"Anomaly rate: {len(anomalies)/len(df)*100:.1f}%")
    
    if not anomalies.empty:
        print("\nTop anomalies:")
        top_anomalies = anomalies.nlargest(5, 'anomaly_score')
        
        for _, anomaly in top_anomalies.iterrows():
            print(f"• {anomaly['date'].strftime('%Y-%m-%d')}: {anomaly['details']}")
            print(f"  Amount: KSh {anomaly['amount']:,.0f}")
            print(f"  Anomaly Score: {anomaly['anomaly_score']:.1%}")
            print(f"  Reason: {anomaly['reason']}")
            print()

def demo_behavioral_analysis():
    """Demo comprehensive behavioral analysis"""
    print("=== DEMO: Comprehensive Behavioral Analysis ===\n")
    
    # Create data and analyzer
    df = create_realistic_transaction_data()
    analyzer = BehaviorAnalyzer()
    
    # Perform analysis
    analysis = analyzer.analyze_behavior(df)
    
    # Show key insights
    print("Key Behavioral Insights:")
    insights = analysis['behavioral_patterns']['behavioral_insights']
    for insight in insights:
        print(f"• {insight}")
    
    print("\nRisk Assessment:")
    risks = analysis['risk_assessment']
    for risk_type, risk_data in risks.items():
        if isinstance(risk_data, dict):
            print(f"• {risk_type.replace('_', ' ').title()}: {risk_data['description']} ({risk_data['risk_score']:.1%})")
    
    print("\nRecommendations:")
    recommendations = analysis['recommendations']
    for rec in recommendations[:3]:  # Show top 3
        print(f"• {rec['title']} ({rec['priority']} Priority)")
        print(f"  Action: {rec['action']}")
        print(f"  Impact: {rec['impact']}")
        print()

def demo_monthly_forecasting():
    """Demo monthly spending forecasting"""
    print("=== DEMO: Monthly Spending Forecasting ===\n")
    
    # Create and train model
    df = create_realistic_transaction_data()
    markov_model = MarkovChainPredictor(order=2)
    markov_model.train(df)
    
    # Get monthly predictions
    monthly_forecast = markov_model.predict_monthly_spending()
    
    print("Monthly Spending Forecast:")
    print("-" * 60)
    print(f"{'Category':<15} {'Predicted':<12} {'Range':<20} {'Transactions':<12}")
    print("-" * 60)
    
    for category, data in monthly_forecast.items():
        predicted = data['predicted_amount']
        conf_interval = data['confidence_interval']
        transactions = data['transaction_count']
        
        range_str = f"{conf_interval[0]:.0f} - {conf_interval[1]:.0f}"
        
        print(f"{category:<15} KSh {predicted:<8.0f} KSh {range_str:<15} {transactions:<12.0f}")
    
    print()

if __name__ == "__main__":
    print("🧠 MARKOV CHAIN BEHAVIOR ANALYSIS DEMO\n")
    print("This demo shows how Markov Chains can model and predict financial behavior\n")
    
    # Run all demos
    demo_markov_training()
    demo_behavior_prediction()
    demo_spending_sequences()
    demo_anomaly_detection()
    demo_behavioral_analysis()
    demo_monthly_forecasting()
    
    print("=== SUMMARY ===")
    print("✅ Markov Chain model training with behavioral states")
    print("✅ Next transaction prediction with confidence levels")
    print("✅ Spending sequence forecasting")
    print("✅ Anomaly detection for unusual transactions")
    print("✅ Comprehensive behavioral risk assessment")
    print("✅ Monthly spending forecasting with confidence intervals")
    print("✅ Personalized recommendations based on behavior patterns")
    print("\nMarkov Chains provide powerful insights into spending behavior and enable")
    print("predictive analytics for better financial planning and risk management!")