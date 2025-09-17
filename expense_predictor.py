import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import streamlit as st

class ExpensePredictor:
    def __init__(self):
        pass
    
    def predict_monthly_expenses(self, df: pd.DataFrame) -> Dict:
        """Predict next month's expenses based on historical data"""
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        # Group by month and category
        monthly_data = expenses_df.groupby([
            pd.Grouper(key='Date', freq='ME'),
            'Category'
        ])['Amount'].sum().reset_index()
        
        predictions = {}
        
        for category in monthly_data['Category'].unique():
            category_data = monthly_data[monthly_data['Category'] == category]
            
            if len(category_data) >= 2:
                amounts = category_data['Amount'].values
                
                # Simple trend-based prediction
                if len(amounts) >= 3:
                    # Use linear regression for trend
                    x = np.arange(len(amounts))
                    coeffs = np.polyfit(x, amounts, 1)
                    next_month_pred = coeffs[0] * len(amounts) + coeffs[1]
                else:
                    # Use average of last 2 months
                    next_month_pred = np.mean(amounts[-2:])
                
                # Add seasonal adjustment (simple)
                current_month = datetime.now().month
                seasonal_factor = self._get_seasonal_factor(category, current_month)
                next_month_pred *= seasonal_factor
                
                predictions[category] = {
                    'predicted_amount': max(0, next_month_pred),
                    'historical_average': np.mean(amounts),
                    'trend': 'increasing' if len(amounts) >= 2 and amounts[-1] > amounts[-2] else 'stable',
                    'confidence': min(len(amounts) / 6, 1.0)  # Higher confidence with more data
                }
        
        return predictions
    
    def _get_seasonal_factor(self, category: str, month: int) -> float:
        """Apply seasonal adjustments to predictions"""
        seasonal_factors = {
            'Food': {12: 1.2, 1: 1.1, 4: 1.0, 7: 1.0, 10: 1.0},  # Higher in Dec/Jan
            'Transport': {12: 1.3, 1: 1.1, 4: 1.0, 7: 1.1, 10: 1.0},  # Higher in holidays
            'Entertainment': {12: 1.5, 1: 0.8, 4: 1.0, 7: 1.2, 10: 1.0},  # Higher in Dec, July
            'Shopping': {11: 1.3, 12: 1.4, 1: 0.9, 4: 1.0, 7: 1.1, 10: 1.0},  # Black Friday, Christmas
            'Utilities': {6: 1.2, 7: 1.3, 8: 1.2, 12: 1.1, 1: 1.1, 2: 1.0}  # Higher in hot/cold months
        }
        
        factors = seasonal_factors.get(category, {})
        return factors.get(month, 1.0)
    
    def set_savings_goals(self, current_expenses: Dict, target_reduction: float = 0.15) -> Dict:
        """Set realistic savings goals based on current spending"""
        goals = {}
        
        for category, amount in current_expenses.items():
            if category in ['Food', 'Transport', 'Entertainment', 'Shopping']:
                # These categories have more flexibility for reduction
                potential_savings = amount * target_reduction
                goals[category] = {
                    'current_monthly': amount,
                    'target_monthly': amount - potential_savings,
                    'monthly_savings_goal': potential_savings,
                    'annual_savings_potential': potential_savings * 12,
                    'difficulty': 'Medium' if target_reduction <= 0.2 else 'Hard'
                }
            elif category in ['Utilities', 'Health']:
                # These have less flexibility
                potential_savings = amount * (target_reduction * 0.5)
                goals[category] = {
                    'current_monthly': amount,
                    'target_monthly': amount - potential_savings,
                    'monthly_savings_goal': potential_savings,
                    'annual_savings_potential': potential_savings * 12,
                    'difficulty': 'Hard'
                }
        
        return goals
    
    def track_goal_progress(self, df: pd.DataFrame, goals: Dict) -> Dict:
        """Track progress towards savings goals"""
        current_month_expenses = df[
            (df['Date'] >= pd.Timestamp.now().replace(day=1)) &
            (df['Amount'] < 0)
        ].copy()
        
        if current_month_expenses.empty:
            return {}
        
        current_month_expenses['Amount'] = current_month_expenses['Amount'].abs()
        current_spending = current_month_expenses.groupby('Category')['Amount'].sum()
        
        progress = {}
        
        for category, goal_data in goals.items():
            current_amount = current_spending.get(category, 0)
            target_amount = goal_data['target_monthly']
            
            if target_amount > 0:
                progress_percentage = min(100, (target_amount - current_amount) / target_amount * 100)
            else:
                progress_percentage = 100 if current_amount == 0 else 0
            
            progress[category] = {
                'current_spending': current_amount,
                'target_spending': target_amount,
                'progress_percentage': max(0, progress_percentage),
                'on_track': current_amount <= target_amount,
                'days_remaining': (pd.Timestamp.now().replace(day=1) + pd.DateOffset(months=1) - pd.Timestamp.now()).days
            }
        
        return progress
    
    def generate_spending_alerts(self, df: pd.DataFrame, goals: Dict) -> List[Dict]:
        """Generate alerts when spending approaches limits"""
        alerts = []
        
        # Current month spending
        current_month_start = pd.Timestamp.now().replace(day=1)
        current_month_expenses = df[
            (df['Date'] >= current_month_start) &
            (df['Amount'] < 0)
        ].copy()
        
        if current_month_expenses.empty:
            return alerts
        
        current_month_expenses['Amount'] = current_month_expenses['Amount'].abs()
        current_spending = current_month_expenses.groupby('Category')['Amount'].sum()
        
        days_passed = (pd.Timestamp.now() - current_month_start).days
        days_in_month = pd.Timestamp.now().days_in_month
        month_progress = days_passed / days_in_month
        
        for category, goal_data in goals.items():
            current_amount = current_spending.get(category, 0)
            target_amount = goal_data['target_monthly']
            expected_amount = target_amount * month_progress
            
            if current_amount > expected_amount * 1.2:  # 20% over expected
                alerts.append({
                    'type': 'overspending',
                    'category': category,
                    'message': f"You're spending faster than planned in {category}. Current: KSh {current_amount:,.2f}, Expected: KSh {expected_amount:,.2f}",
                    'severity': 'high' if current_amount > target_amount else 'medium'
                })
            elif current_amount > target_amount * 0.8:  # 80% of monthly target reached
                alerts.append({
                    'type': 'approaching_limit',
                    'category': category,
                    'message': f"You're approaching your {category} budget limit. Remaining: KSh {target_amount - current_amount:,.2f}",
                    'severity': 'medium'
                })
        
        return alerts
    
    def suggest_micro_savings(self, df: pd.DataFrame) -> List[Dict]:
        """Suggest small daily changes that add up to significant savings"""
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        suggestions = []
        
        # Daily coffee/tea expenses
        coffee_transactions = expenses_df[
            expenses_df['Details'].str.contains('coffee|cafe|tea|starbucks', case=False, na=False)
        ]
        if not coffee_transactions.empty:
            daily_coffee_cost = coffee_transactions['Amount'].mean()
            monthly_savings = daily_coffee_cost * 20 * 0.5  # Save 50% by making coffee at home
            suggestions.append({
                'category': 'Food',
                'suggestion': f"Make coffee at home instead of buying. Average cost: KSh {daily_coffee_cost:.2f}",
                'potential_monthly_savings': monthly_savings,
                'potential_annual_savings': monthly_savings * 12,
                'effort': 'Low'
            })
        
        # Transport optimization
        transport_expenses = expenses_df[expenses_df['Category'] == 'Transport']
        if not transport_expenses.empty:
            avg_transport_cost = transport_expenses['Amount'].mean()
            suggestions.append({
                'category': 'Transport',
                'suggestion': f"Walk or cycle for short distances. Average trip cost: KSh {avg_transport_cost:.2f}",
                'potential_monthly_savings': avg_transport_cost * 8,  # 8 trips per month
                'potential_annual_savings': avg_transport_cost * 8 * 12,
                'effort': 'Medium'
            })
        
        # Subscription services
        recurring_payments = expenses_df[
            expenses_df['Details'].str.contains('subscription|netflix|spotify|dstv', case=False, na=False)
        ]
        if not recurring_payments.empty:
            monthly_subscriptions = recurring_payments['Amount'].sum()
            suggestions.append({
                'category': 'Entertainment',
                'suggestion': f"Review and cancel unused subscriptions. Current monthly cost: KSh {monthly_subscriptions:.2f}",
                'potential_monthly_savings': monthly_subscriptions * 0.3,
                'potential_annual_savings': monthly_subscriptions * 0.3 * 12,
                'effort': 'Low'
            })
        
        return suggestions