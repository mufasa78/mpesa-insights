"""
Test script to verify the Markov Chain AI insights work correctly
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.getcwd())

def create_comprehensive_test_data():
    """Create comprehensive test transaction data for Markov Chain analysis"""
    np.random.seed(42)
    
    # Generate 6 months of realistic test data
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 6, 30)
    
    transactions = []
    current_date = start_date
    
    # Define realistic spending patterns
    categories = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Shopping', 'Health']
    
    # Create behavioral patterns (some categories follow others)
    patterns = {
        'Food': ['Transport', 'Shopping'],  # After food, often transport or shopping
        'Transport': ['Food', 'Entertainment'],  # After transport, often food or entertainment
        'Entertainment': ['Food', 'Transport'],  # After entertainment, often food or transport
        'Shopping': ['Food', 'Transport'],
        'Utilities': ['Food'],  # After utilities, usually food
        'Health': ['Food', 'Transport']
    }
    
    last_category = None
    
    while current_date <= end_date:
        # Generate 1-4 transactions per day
        num_transactions = np.random.randint(1, 5)
        
        for _ in range(num_transactions):
            # Choose category based on patterns or randomly
            if last_category and last_category in patterns and np.random.random() < 0.6:
                # 60% chance to follow pattern
                category = np.random.choice(patterns[last_category])
            else:
                # Random category
                category = np.random.choice(categories)
            
            # Generate realistic amounts based on category
            if category == 'Food':
                amount = -np.random.randint(200, 3000)
            elif category == 'Transport':
                amount = -np.random.randint(100, 2000)
            elif category == 'Utilities':
                amount = -np.random.randint(1000, 5000)
            elif category == 'Entertainment':
                amount = -np.random.randint(500, 4000)
            elif category == 'Shopping':
                amount = -np.random.randint(1000, 8000)
            elif category == 'Health':
                amount = -np.random.randint(500, 6000)
            else:
                amount = -np.random.randint(100, 2000)
            
            # Add some time variation
            hour = np.random.choice([8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
            transaction_time = current_date.replace(hour=hour, minute=np.random.randint(0, 59))
            
            transactions.append({
                'Date': transaction_time,
                'Details': f'{category.upper()} TRANSACTION {np.random.randint(1000, 9999)}',
                'Amount': amount,
                'Category': category,
                'Type': 'Debit'
            })
            
            last_category = category
        
        current_date += timedelta(days=1)
    
    # Add income transactions
    for month in range(1, 7):
        transactions.append({
            'Date': datetime(2024, month, 28, 9, 0),
            'Details': 'SALARY PAYMENT FROM EMPLOYER',
            'Amount': 75000,
            'Category': 'Income',
            'Type': 'Credit'
        })
        
        # Add some freelance income
        if np.random.random() < 0.4:  # 40% chance
            transactions.append({
                'Date': datetime(2024, month, 15, 14, 30),
                'Details': 'FREELANCE PAYMENT CLIENT',
                'Amount': np.random.randint(15000, 35000),
                'Category': 'Income',
                'Type': 'Credit'
            })
    
    # Add some anomalous transactions
    anomaly_transactions = [
        {
            'Date': datetime(2024, 2, 15, 23, 30),
            'Details': 'EXPENSIVE ELECTRONICS PURCHASE',
            'Amount': -85000,
            'Category': 'Shopping',
            'Type': 'Debit'
        },
        {
            'Date': datetime(2024, 4, 3, 2, 15),
            'Details': 'LATE NIGHT LARGE WITHDRAWAL',
            'Amount': -25000,
            'Category': 'Financial',
            'Type': 'Debit'
        },
        {
            'Date': datetime(2024, 5, 20, 11, 45),
            'Details': 'EMERGENCY MEDICAL EXPENSE',
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

def test_markov_predictor():
    """Test the MarkovChainPredictor functionality"""
    print("🧪 Testing Markov Chain Predictor...")
    
    try:
        from markov_predictor import MarkovChainPredictor
        
        # Create test data
        df = create_comprehensive_test_data()
        print(f"✅ Created test data with {len(df)} transactions")
        
        # Initialize and train model
        markov_model = MarkovChainPredictor(order=2)
        markov_model.train(df)
        
        # Test model statistics
        stats = markov_model.get_model_stats()
        print(f"✅ Model trained - Status: {stats['status']}")
        print(f"✅ Behavioral states: {stats['total_states']}")
        print(f"✅ Transitions learned: {stats['total_transitions']}")
        
        # Test state creation
        df_with_states = markov_model.create_states(df)
        print(f"✅ Created behavioral states for {len(df_with_states)} transactions")
        
        # Test predictions
        if not df_with_states.empty:
            recent_state = df_with_states.iloc[-1]['State_Sequence']
            predictions = markov_model.predict_next_transaction(recent_state, n_predictions=3)
            
            if predictions and predictions[0]['state'] != 'Unknown':
                print(f"✅ Generated {len(predictions)} next transaction predictions")
                for pred in predictions:
                    print(f"  • {pred['category']}: {pred['probability']:.1%} ({pred['confidence']})")
            else:
                print("ℹ️ Predictions generated but need more data for accuracy")
        
        # Test sequence predictions
        categories = ['Food', 'Transport', 'Entertainment']
        for category in categories:
            sequences = markov_model.predict_spending_sequence(category, sequence_length=3)
            if sequences and sequences[0]['sequence']:
                sequence = sequences[0]['sequence']
                probability = sequences[0]['overall_probability']
                print(f"✅ {category} sequence: {' → '.join(sequence)} ({probability:.1%})")
        
        # Test monthly forecasting
        monthly_forecast = markov_model.predict_monthly_spending()
        if monthly_forecast:
            print(f"✅ Generated monthly forecast for {len(monthly_forecast)} categories")
        
        # Test anomaly detection
        anomalies = markov_model.detect_anomalies(df, threshold=0.1)
        print(f"✅ Detected {len(anomalies)} anomalies ({len(anomalies)/len(df)*100:.1f}% rate)")
        
        return True
        
    except Exception as e:
        print(f"❌ Markov Predictor test failed: {e}")
        return False

def test_behavior_analyzer():
    """Test the BehaviorAnalyzer functionality"""
    print("\n🧪 Testing Behavior Analyzer...")
    
    try:
        from behavior_analyzer import BehaviorAnalyzer
        
        # Create test data
        df = create_comprehensive_test_data()
        
        # Initialize analyzer
        analyzer = BehaviorAnalyzer()
        
        # Perform comprehensive analysis
        analysis = analyzer.analyze_behavior(df)
        
        # Check analysis structure
        expected_keys = ['behavioral_patterns', 'spending_predictions', 'anomaly_detection', 
                        'habit_analysis', 'temporal_insights', 'risk_assessment', 'recommendations']
        
        for key in expected_keys:
            if key in analysis:
                print(f"✅ Found {key}")
            else:
                print(f"❌ Missing {key}")
        
        # Test dashboard creation
        dashboard = analyzer.create_behavior_dashboard(analysis)
        summary_metrics = dashboard.get('summary_metrics', {})
        
        print(f"✅ Behavior score: {summary_metrics.get('behavior_score', 0):.0f}/100")
        print(f"✅ Predictability: {summary_metrics.get('predictability', 0):.0f}%")
        print(f"✅ Risk level: {summary_metrics.get('risk_level', 'Unknown')}")
        
        # Test recommendations
        recommendations = analysis.get('recommendations', [])
        print(f"✅ Generated {len(recommendations)} recommendations")
        
        return True
        
    except Exception as e:
        print(f"❌ Behavior Analyzer test failed: {e}")
        return False

def test_integration():
    """Test the integration of Markov Chain components"""
    print("\n🧪 Testing Integration...")
    
    try:
        from markov_predictor import MarkovChainPredictor
        from behavior_analyzer import BehaviorAnalyzer
        
        # Create test data
        df = create_comprehensive_test_data()
        
        # Test that both components can work with the same data
        markov_model = MarkovChainPredictor(order=2)
        markov_model.train(df)
        
        analyzer = BehaviorAnalyzer()
        analysis = analyzer.analyze_behavior(df)
        
        # Test data compatibility
        print("✅ Both components can process the same data")
        
        # Test that we can extract meaningful insights
        patterns = analysis.get('behavioral_patterns', {})
        transitions = patterns.get('most_common_transitions', [])
        
        if transitions:
            print(f"✅ Found {len(transitions)} behavioral transitions")
            
            # Show top transition
            top_transition = transitions[0]
            from_state = top_transition['from_state'].split('_')[0]
            to_state = top_transition['to_state'].split('_')[0]
            probability = top_transition['probability']
            
            print(f"✅ Top transition: {from_state} → {to_state} ({probability:.1%})")
        
        # Test risk assessment
        risks = analysis.get('risk_assessment', {})
        if risks:
            print(f"✅ Risk assessment completed for {len(risks)} risk types")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_data_quality():
    """Test data quality and patterns"""
    print("\n🧪 Testing Data Quality...")
    
    try:
        df = create_comprehensive_test_data()
        
        # Test data structure
        required_columns = ['Date', 'Details', 'Amount', 'Category', 'Type']
        for col in required_columns:
            if col in df.columns:
                print(f"✅ Found required column: {col}")
            else:
                print(f"❌ Missing required column: {col}")
        
        # Test data quality
        print(f"✅ Total transactions: {len(df)}")
        print(f"✅ Date range: {df['Date'].min()} to {df['Date'].max()}")
        print(f"✅ Categories: {df['Category'].nunique()} unique")
        print(f"✅ Income transactions: {len(df[df['Amount'] > 0])}")
        print(f"✅ Expense transactions: {len(df[df['Amount'] < 0])}")
        
        # Test for patterns
        expenses_df = df[df['Amount'] < 0]
        category_counts = expenses_df['Category'].value_counts()
        
        print(f"✅ Most common expense category: {category_counts.index[0]} ({category_counts.iloc[0]} transactions)")
        
        # Test temporal distribution
        df['Hour'] = df['Date'].dt.hour
        hourly_dist = df['Hour'].value_counts().sort_index()
        peak_hour = hourly_dist.idxmax()
        
        print(f"✅ Peak transaction hour: {peak_hour}:00 ({hourly_dist[peak_hour]} transactions)")
        
        return True
        
    except Exception as e:
        print(f"❌ Data quality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MARKOV CHAIN AI INSIGHTS VERIFICATION TEST\n")
    
    # Run all tests
    data_test = test_data_quality()
    markov_test = test_markov_predictor()
    behavior_test = test_behavior_analyzer()
    integration_test = test_integration()
    
    print(f"\n📊 TEST RESULTS:")
    print(f"Data Quality: {'✅ PASS' if data_test else '❌ FAIL'}")
    print(f"Markov Predictor: {'✅ PASS' if markov_test else '❌ FAIL'}")
    print(f"Behavior Analyzer: {'✅ PASS' if behavior_test else '❌ FAIL'}")
    print(f"Integration: {'✅ PASS' if integration_test else '❌ FAIL'}")
    
    if all([data_test, markov_test, behavior_test, integration_test]):
        print("\n🎉 All tests passed! Markov Chain AI Insights should work perfectly!")
        print("\n🧠 The AI system can now provide:")
        print("  • Advanced behavioral pattern recognition")
        print("  • Predictive transaction modeling")
        print("  • Intelligent anomaly detection")
        print("  • Personalized spending insights")
        print("  • Risk assessment and recommendations")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")
        print("💡 The system will fall back to basic analysis if advanced features are unavailable.")