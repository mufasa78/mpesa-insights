"""
Demo script showing the enhanced income source management functionality
"""

import pandas as pd
from datetime import datetime, timedelta
import random

from categorizer import ExpenseCategorizer
from income_source_manager import IncomeSourceManager

def create_sample_data():
    """Create sample transaction data with various income sources"""
    
    # Sample income transactions with different patterns
    income_transactions = [
        # Salary from employer
        {"Date": "2024-01-31", "Details": "SALARY PAYMENT FROM ABC COMPANY LTD", "Amount": 85000},
        {"Date": "2024-02-29", "Details": "SALARY PAYMENT FROM ABC COMPANY LTD", "Amount": 85000},
        {"Date": "2024-03-31", "Details": "SALARY PAYMENT FROM ABC COMPANY LTD", "Amount": 85000},
        
        # Freelance payments
        {"Date": "2024-01-15", "Details": "PAYMENT FROM JOHN DOE CONSULTING", "Amount": 25000},
        {"Date": "2024-02-20", "Details": "FREELANCE PAYMENT TECH SOLUTIONS", "Amount": 30000},
        {"Date": "2024-03-10", "Details": "PAYMENT FROM JOHN DOE CONSULTING", "Amount": 25000},
        
        # Business income
        {"Date": "2024-01-05", "Details": "BUSINESS SALES DEPOSIT", "Amount": 15000},
        {"Date": "2024-01-20", "Details": "CUSTOMER PAYMENT RECEIVED", "Amount": 12000},
        {"Date": "2024-02-15", "Details": "BUSINESS SALES DEPOSIT", "Amount": 18000},
        
        # Investment returns
        {"Date": "2024-01-01", "Details": "DIVIDEND PAYMENT EQUITY BANK", "Amount": 5000},
        {"Date": "2024-02-01", "Details": "SACCO DIVIDEND PAYMENT", "Amount": 3000},
        
        # Side hustle
        {"Date": "2024-01-12", "Details": "UBER DRIVER PAYMENT", "Amount": 8000},
        {"Date": "2024-02-18", "Details": "UBER DRIVER PAYMENT", "Amount": 9500},
        {"Date": "2024-03-22", "Details": "UBER DRIVER PAYMENT", "Amount": 7500},
        
        # Regular transfers (family support)
        {"Date": "2024-01-10", "Details": "RECEIVED FROM MARY SMITH", "Amount": 10000},
        {"Date": "2024-02-10", "Details": "RECEIVED FROM MARY SMITH", "Amount": 10000},
        {"Date": "2024-03-10", "Details": "RECEIVED FROM MARY SMITH", "Amount": 10000},
    ]
    
    # Sample expense transactions
    expense_transactions = [
        {"Date": "2024-01-05", "Details": "NAIVAS SUPERMARKET", "Amount": -5000},
        {"Date": "2024-01-10", "Details": "UBER TRIP", "Amount": -500},
        {"Date": "2024-01-15", "Details": "KPLC ELECTRICITY BILL", "Amount": -3000},
        {"Date": "2024-02-05", "Details": "CARREFOUR SHOPPING", "Amount": -4500},
        {"Date": "2024-02-12", "Details": "SAFARICOM AIRTIME", "Amount": -1000},
        {"Date": "2024-03-08", "Details": "RESTAURANT BILL", "Amount": -2500},
    ]
    
    # Combine all transactions
    all_transactions = income_transactions + expense_transactions
    
    # Convert to DataFrame
    df = pd.DataFrame(all_transactions)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Type'] = df['Amount'].apply(lambda x: 'Credit' if x > 0 else 'Debit')
    
    return df

def demo_basic_categorization():
    """Demo basic categorization without income source configuration"""
    print("=== DEMO: Basic Categorization (Without Income Source Setup) ===\n")
    
    # Create sample data
    df = create_sample_data()
    
    # Basic categorizer
    basic_categorizer = ExpenseCategorizer()
    categorized_df = basic_categorizer.categorize_transactions(df)
    
    # Show income transactions
    income_df = categorized_df[categorized_df['Category'].str.contains('Income', na=False)]
    print("Income transactions with basic categorization:")
    print(income_df[['Date', 'Details', 'Amount', 'Category']].to_string(index=False))
    print(f"\nTotal Income: KSh {income_df['Amount'].sum():,.0f}")
    print(f"Income Sources Identified: {len(income_df['Category'].unique())}")
    print()

def demo_enhanced_categorization():
    """Demo enhanced categorization with income source configuration"""
    print("=== DEMO: Enhanced Categorization (With Income Source Setup) ===\n")
    
    # Create sample data
    df = create_sample_data()
    
    # Setup income sources
    income_sources = {
        'Salary': ['ABC COMPANY LTD', 'SALARY PAYMENT'],
        'Freelance': ['JOHN DOE CONSULTING', 'TECH SOLUTIONS', 'FREELANCE PAYMENT'],
        'Business Income': ['BUSINESS SALES', 'CUSTOMER PAYMENT'],
        'Investment Returns': ['DIVIDEND PAYMENT', 'SACCO DIVIDEND'],
        'Side Hustle': ['UBER DRIVER'],
        'Regular Transfers': ['MARY SMITH']
    }
    
    # Enhanced categorizer with income sources
    enhanced_categorizer = ExpenseCategorizer(user_income_sources=income_sources)
    categorized_df = enhanced_categorizer.categorize_transactions(df)
    
    # Show income transactions
    income_df = categorized_df[categorized_df['Category'].str.contains('Income', na=False)]
    print("Income transactions with enhanced categorization:")
    print(income_df[['Date', 'Details', 'Amount', 'Category']].to_string(index=False))
    print(f"\nTotal Income: KSh {income_df['Amount'].sum():,.0f}")
    print(f"Income Sources Identified: {len(income_df['Category'].unique())}")
    
    # Income breakdown by source
    print("\nIncome Breakdown by Source:")
    income_summary = income_df.groupby('Category')['Amount'].agg(['sum', 'count']).round(0)
    income_summary.columns = ['Total (KSh)', 'Transactions']
    income_summary['Percentage'] = (income_summary['Total (KSh)'] / income_df['Amount'].sum() * 100).round(1)
    print(income_summary.to_string())
    print()

def demo_smart_suggestions():
    """Demo smart income source suggestions"""
    print("=== DEMO: Smart Income Source Suggestions ===\n")
    
    # Create sample data
    df = create_sample_data()
    
    # Basic categorizer (no income sources configured)
    categorizer = ExpenseCategorizer()
    
    # Get suggestions
    suggestions = categorizer.suggest_income_sources_from_data(df)
    
    print("Smart suggestions based on transaction patterns:")
    for income_type, transactions in suggestions.items():
        print(f"\n{income_type}:")
        for transaction in transactions:
            print(f"  • {transaction}")
    
    print("\nThese suggestions help users quickly identify and configure their income sources!")
    print()

def demo_income_source_manager():
    """Demo the income source manager functionality"""
    print("=== DEMO: Income Source Manager ===\n")
    
    # Create sample data
    df = create_sample_data()
    
    # Initialize manager and categorizer
    manager = IncomeSourceManager()
    categorizer = ExpenseCategorizer()
    
    # Add income sources programmatically (simulating user input)
    print("Adding income sources:")
    categorizer.add_income_source('Salary', ['ABC COMPANY LTD'])
    categorizer.add_income_source('Freelance', ['JOHN DOE CONSULTING', 'TECH SOLUTIONS'])
    categorizer.add_income_source('Business Income', ['BUSINESS SALES'])
    categorizer.add_income_source('Side Hustle', ['UBER DRIVER'])
    
    print("✓ Added Salary source: ABC COMPANY LTD")
    print("✓ Added Freelance sources: JOHN DOE CONSULTING, TECH SOLUTIONS")
    print("✓ Added Business Income source: BUSINESS SALES")
    print("✓ Added Side Hustle source: UBER DRIVER")
    
    # Show current configuration
    print(f"\nCurrent income source configuration:")
    config = categorizer.get_income_sources_config()
    for income_type, payers in config.items():
        print(f"  {income_type}: {', '.join(payers)}")
    
    # Categorize with new sources
    categorized_df = categorizer.categorize_transactions(df)
    income_df = categorized_df[categorized_df['Category'].str.contains('Income', na=False)]
    
    print(f"\nResults after configuration:")
    print(f"Total Income: KSh {income_df['Amount'].sum():,.0f}")
    print(f"Income Categories: {len(income_df['Category'].unique())}")
    
    # Save configuration
    filename = manager.save_income_config(categorizer)
    print(f"\n✓ Configuration saved to {filename}")
    print()

if __name__ == "__main__":
    print("🚀 INCOME SOURCE MANAGEMENT DEMO\n")
    print("This demo shows how the enhanced system helps users better categorize their income\n")
    
    # Run all demos
    demo_basic_categorization()
    demo_enhanced_categorization()
    demo_smart_suggestions()
    demo_income_source_manager()
    
    print("=== SUMMARY ===")
    print("✅ Enhanced income categorization with user-defined sources")
    print("✅ Smart suggestions based on transaction patterns")
    print("✅ Detailed income source breakdown and analysis")
    print("✅ Easy configuration management and persistence")
    print("✅ Better financial insights and recommendations")
    print("\nThis system provides much more accurate and personalized income tracking!")