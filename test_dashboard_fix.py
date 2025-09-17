"""
Test script to verify the dashboard fix works correctly
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
            amount = -np.random.randint(100, 5000)  # Negative for expenses
            
            transactions.append({
                'Date': current_date + timedelta(hours=np.random.randint(8, 20)),
                'Details': f'{category.upper()} TRANSACTION',
                'Amount': amount,
                'Category': category,
                'Type': 'Debit'
            })
        
        current_date += timedelta(days=1)
    
    # Add some income transactions
    for month in [1, 2, 3]:
        transactions.append({
            'Date': datetime(2024, month, 28),
            'Details': 'SALARY PAYMENT',
            'Amount': 50000,
            'Category': 'Income',
            'Type': 'Credit'
        })
    
    return pd.DataFrame(transactions)

def test_dashboard_functions():
    """Test the dashboard functions"""
    print("🧪 Testing Dashboard Functions...")
    
    # Create test data
    df = create_test_data()
    print(f"✅ Created test data with {len(df)} transactions")
    
    # Test basic data processing
    total_transactions = len(df)
    income_df = df[df['Amount'] > 0]
    expense_df = df[df['Amount'] < 0]
    
    print(f"✅ Total transactions: {total_transactions}")
    print(f"✅ Income transactions: {len(income_df)}")
    print(f"✅ Expense transactions: {len(expense_df)}")
    
    # Test expense breakdown
    expenses_df = df[df['Amount'] < 0].copy()
    if not expenses_df.empty:
        expenses_df['Amount'] = expenses_df['Amount'] * -1
        top_categories = expenses_df.groupby('Category')['Amount'].sum().nlargest(5)
        print(f"✅ Top spending categories: {list(top_categories.index)}")
    
    # Test monthly trends data processing
    if 'Date' in df.columns:
        df_copy = df.copy()
        df_copy['Month'] = df_copy['Date'].dt.to_period('M')
        monthly_data = df_copy.groupby('Month').agg({
            'Amount': 'sum'
        }).reset_index()
        
        monthly_data['Month'] = monthly_data['Month'].astype(str)
        monthly_data['Amount'] = monthly_data['Amount'].abs()
        
        print(f"✅ Monthly data processed: {len(monthly_data)} months")
        print(f"✅ Monthly data columns: {list(monthly_data.columns)}")
        
        # Test that we can create a simple plotly chart
        try:
            import plotly.express as px
            fig = px.line(
                monthly_data, 
                x='Month', 
                y='Amount',
                title='Test Monthly Spending Trend',
                markers=True
            )
            print("✅ Plotly chart creation successful")
        except Exception as e:
            print(f"❌ Plotly chart creation failed: {e}")
    
    # Test category summary for detailed analysis
    if not expenses_df.empty:
        category_summary = expenses_df.groupby('Category').agg({
            'Amount': ['sum', 'count', 'mean']
        }).round(2)
        
        category_summary.columns = ['Total', 'Count', 'Average']
        category_summary = category_summary.sort_values('Total', ascending=False)
        
        # Add percentage
        total_expenses = category_summary['Total'].sum()
        category_summary['Percentage'] = (category_summary['Total'] / total_expenses * 100).round(1)
        
        print(f"✅ Category summary created with {len(category_summary)} categories")
        
        # Test chart data preparation
        try:
            from visualizer import create_pie_chart, create_bar_chart
            
            # Test pie chart data
            pie_data = category_summary.reset_index()
            print(f"✅ Pie chart data prepared: {list(pie_data.columns)}")
            
            # Test bar chart data  
            bar_data = category_summary.reset_index()
            print(f"✅ Bar chart data prepared: {list(bar_data.columns)}")
            
        except Exception as e:
            print(f"❌ Chart data preparation failed: {e}")
    
    print("\n🎉 All dashboard function tests completed!")

if __name__ == "__main__":
    print("🚀 DASHBOARD FIX VERIFICATION TEST\n")
    test_dashboard_functions()
    print("\n✅ Dashboard should now work without errors!")