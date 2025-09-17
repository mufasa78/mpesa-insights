import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import streamlit as st

class BudgetAdvisor:
    def __init__(self):
        self.budget_rules = {
            'Food': 0.30,  # 30% of income
            'Transport': 0.15,  # 15% of income
            'Utilities': 0.10,  # 10% of income
            'Entertainment': 0.05,  # 5% of income
            'Shopping': 0.10,  # 10% of income
            'Health': 0.05,  # 5% of income
        }
    
    def analyze_spending_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze spending patterns and identify areas for improvement"""
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        # Monthly analysis
        monthly_spending = expenses_df.groupby([
            pd.Grouper(key='Date', freq='ME'),
            'Category'
        ])['Amount'].sum().reset_index()
        
        # Calculate trends
        insights = {
            'overspending_categories': self._identify_overspending(expenses_df),
            'spending_trends': self._analyze_trends(monthly_spending),
            'unusual_transactions': self._find_unusual_transactions(expenses_df),
            'savings_opportunities': self._find_savings_opportunities(expenses_df),
            'budget_recommendations': self._generate_budget_recommendations(expenses_df)
        }
        
        return insights
    
    def _identify_overspending(self, expenses_df: pd.DataFrame) -> List[Dict]:
        """Identify categories where user is overspending"""
        category_totals = expenses_df.groupby('Category')['Amount'].sum()
        total_expenses = category_totals.sum()
        
        overspending = []
        for category, amount in category_totals.items():
            percentage = (amount / total_expenses) * 100
            recommended_percentage = self.budget_rules.get(category, 0.05) * 100
            
            if percentage > recommended_percentage * 1.2:  # 20% over recommended
                overspending.append({
                    'category': category,
                    'current_percentage': percentage,
                    'recommended_percentage': recommended_percentage,
                    'excess_amount': amount - (total_expenses * self.budget_rules.get(category, 0.05)),
                    'potential_savings': amount * 0.2  # Suggest 20% reduction
                })
        
        return sorted(overspending, key=lambda x: x['excess_amount'], reverse=True)
    
    def _analyze_trends(self, monthly_spending: pd.DataFrame) -> Dict:
        """Analyze spending trends over time"""
        trends = {}
        
        for category in monthly_spending['Category'].unique():
            category_data = monthly_spending[monthly_spending['Category'] == category]
            if len(category_data) >= 2:
                amounts = category_data['Amount'].values
                trend = np.polyfit(range(len(amounts)), amounts, 1)[0]
                
                trends[category] = {
                    'trend': 'increasing' if trend > 0 else 'decreasing',
                    'monthly_change': trend,
                    'latest_amount': amounts[-1],
                    'average_amount': np.mean(amounts)
                }
        
        return trends
    
    def _find_unusual_transactions(self, expenses_df: pd.DataFrame) -> List[Dict]:
        """Find unusually high transactions that might be one-time expenses"""
        unusual = []
        
        for category in expenses_df['Category'].unique():
            category_data = expenses_df[expenses_df['Category'] == category]
            if len(category_data) < 3:
                continue
                
            mean_amount = category_data['Amount'].mean()
            std_amount = category_data['Amount'].std()
            threshold = mean_amount + (2 * std_amount)  # 2 standard deviations
            
            outliers = category_data[category_data['Amount'] > threshold]
            
            for _, transaction in outliers.iterrows():
                unusual.append({
                    'date': transaction['Date'],
                    'category': category,
                    'amount': transaction['Amount'],
                    'details': transaction['Details'],
                    'times_above_average': transaction['Amount'] / mean_amount
                })
        
        return sorted(unusual, key=lambda x: x['amount'], reverse=True)[:10]
    
    def _find_savings_opportunities(self, expenses_df: pd.DataFrame) -> List[Dict]:
        """Identify specific savings opportunities"""
        opportunities = []
        
        # Frequent small transactions that add up
        frequent_transactions = expenses_df.groupby('Details').agg({
            'Amount': ['sum', 'count', 'mean']
        }).round(2)
        frequent_transactions.columns = ['total', 'count', 'average']
        frequent_transactions = frequent_transactions[frequent_transactions['count'] >= 5]
        frequent_transactions = frequent_transactions.sort_values('total', ascending=False)
        
        for details, row in frequent_transactions.head(10).iterrows():
            if row['total'] > 1000:  # Only significant amounts
                opportunities.append({
                    'type': 'frequent_expense',
                    'description': f"You spent KSh {row['total']:,.2f} on '{details}' in {row['count']} transactions",
                    'suggestion': f"Consider reducing frequency or finding alternatives. Potential monthly savings: KSh {row['total'] * 0.3:,.2f}",
                    'potential_savings': row['total'] * 0.3
                })
        
        # High-cost categories
        category_totals = expenses_df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        for category, amount in category_totals.head(3).items():
            if amount > 5000:  # Significant spending
                opportunities.append({
                    'type': 'high_category',
                    'description': f"High spending in {category}: KSh {amount:,.2f}",
                    'suggestion': f"Review {category} expenses for optimization opportunities",
                    'potential_savings': amount * 0.15
                })
        
        return opportunities
    
    def _generate_budget_recommendations(self, expenses_df: pd.DataFrame) -> Dict:
        """Generate personalized budget recommendations"""
        total_expenses = expenses_df['Amount'].sum()
        category_totals = expenses_df.groupby('Category')['Amount'].sum()
        
        recommendations = {}
        
        for category, current_amount in category_totals.items():
            recommended_amount = total_expenses * self.budget_rules.get(category, 0.05)
            
            recommendations[category] = {
                'current_amount': current_amount,
                'recommended_amount': recommended_amount,
                'difference': current_amount - recommended_amount,
                'status': 'over' if current_amount > recommended_amount else 'under',
                'adjustment_needed': abs(current_amount - recommended_amount)
            }
        
        return recommendations
    
    def generate_expense_cutting_tips(self, insights: Dict) -> List[str]:
        """Generate actionable expense cutting tips"""
        tips = []
        
        # Tips based on overspending categories
        for overspend in insights['overspending_categories'][:3]:
            category = overspend['category']
            if category == 'Food':
                tips.append(f"🍽️ Food spending is {overspend['current_percentage']:.1f}% of expenses. Try meal planning and cooking at home more often.")
            elif category == 'Transport':
                tips.append(f"🚗 Transport costs are high. Consider carpooling, using public transport, or combining trips.")
            elif category == 'Entertainment':
                tips.append(f"🎬 Entertainment spending is above recommended levels. Look for free activities or set a monthly entertainment budget.")
            elif category == 'Shopping':
                tips.append(f"🛍️ Shopping expenses are high. Try the 24-hour rule before purchases and compare prices.")
        
        # Tips based on unusual transactions
        if insights['unusual_transactions']:
            tips.append("💡 You have some unusually high transactions. Review these for one-time vs recurring expenses.")
        
        # Tips based on trends
        increasing_categories = [cat for cat, data in insights['spending_trends'].items() 
                               if data['trend'] == 'increasing']
        if increasing_categories:
            tips.append(f"📈 Your spending is increasing in: {', '.join(increasing_categories[:3])}. Monitor these closely.")
        
        return tips