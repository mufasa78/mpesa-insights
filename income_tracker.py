import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import streamlit as st

class IncomeTracker:
    def __init__(self):
        self.income_categories = {
            'Salary': 'Regular monthly/weekly salary from employment',
            'Business Income': 'Revenue from business activities',
            'Freelance/Consulting': 'Income from freelance work or consulting',
            'Investment Returns': 'Dividends, interest, capital gains',
            'Rental Income': 'Income from property rentals',
            'Side Hustle': 'Income from part-time activities',
            'Gifts/Transfers': 'Money received from family/friends',
            'Refunds': 'Refunds from purchases or services',
            'Other Income': 'Other sources of income'
        }
    
    def analyze_income_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze income patterns and provide insights"""
        # Get income transactions (positive amounts or categorized as Income)
        income_df = df[
            (df['Amount'] > 0) | (df['Category'] == 'Income')
        ].copy()
        
        if income_df.empty:
            return {
                'total_income': 0,
                'monthly_average': 0,
                'income_sources': {},
                'income_stability': 'No income data',
                'recommendations': ['No income transactions detected. Please categorize your income transactions.']
            }
        
        # Ensure positive amounts for income
        income_df['Amount'] = income_df['Amount'].abs()
        
        # Monthly income analysis
        monthly_income = income_df.groupby(
            pd.Grouper(key='Date', freq='ME')
        )['Amount'].sum()
        
        # Income by source/category
        if 'Income_Category' in income_df.columns:
            income_sources = income_df.groupby('Income_Category')['Amount'].sum().to_dict()
        else:
            # Try to infer from transaction details
            income_sources = self._infer_income_sources(income_df)
        
        # Calculate stability metrics
        stability_score = self._calculate_income_stability(monthly_income)
        
        analysis = {
            'total_income': income_df['Amount'].sum(),
            'monthly_average': monthly_income.mean() if len(monthly_income) > 0 else 0,
            'monthly_income': monthly_income.to_dict(),
            'income_sources': income_sources,
            'income_stability': stability_score,
            'growth_trend': self._calculate_income_trend(monthly_income),
            'recommendations': self._generate_income_recommendations(income_df, monthly_income)
        }
        
        return analysis
    
    def _infer_income_sources(self, income_df: pd.DataFrame) -> Dict:
        """Infer income sources from transaction details"""
        sources = {}
        
        for _, transaction in income_df.iterrows():
            details = str(transaction['Details']).lower()
            amount = transaction['Amount']
            
            # Pattern matching for income sources
            if any(word in details for word in ['salary', 'wage', 'payroll']):
                sources['Salary'] = sources.get('Salary', 0) + amount
            elif any(word in details for word in ['business', 'sales', 'revenue']):
                sources['Business Income'] = sources.get('Business Income', 0) + amount
            elif any(word in details for word in ['freelance', 'consulting', 'contract']):
                sources['Freelance/Consulting'] = sources.get('Freelance/Consulting', 0) + amount
            elif any(word in details for word in ['dividend', 'interest', 'investment']):
                sources['Investment Returns'] = sources.get('Investment Returns', 0) + amount
            elif any(word in details for word in ['rent', 'rental']):
                sources['Rental Income'] = sources.get('Rental Income', 0) + amount
            elif any(word in details for word in ['received from', 'transfer from']):
                sources['Gifts/Transfers'] = sources.get('Gifts/Transfers', 0) + amount
            elif any(word in details for word in ['refund', 'return']):
                sources['Refunds'] = sources.get('Refunds', 0) + amount
            else:
                sources['Other Income'] = sources.get('Other Income', 0) + amount
        
        return sources
    
    def _calculate_income_stability(self, monthly_income: pd.Series) -> Dict:
        """Calculate income stability metrics"""
        if len(monthly_income) < 2:
            return {
                'score': 0.5,
                'description': 'Insufficient data',
                'coefficient_of_variation': 0
            }
        
        mean_income = monthly_income.mean()
        std_income = monthly_income.std()
        cv = std_income / mean_income if mean_income > 0 else float('inf')
        
        # Stability score (lower CV = higher stability)
        if cv < 0.1:
            stability = {'score': 1.0, 'description': 'Very Stable'}
        elif cv < 0.2:
            stability = {'score': 0.8, 'description': 'Stable'}
        elif cv < 0.4:
            stability = {'score': 0.6, 'description': 'Moderately Stable'}
        elif cv < 0.6:
            stability = {'score': 0.4, 'description': 'Somewhat Unstable'}
        else:
            stability = {'score': 0.2, 'description': 'Unstable'}
        
        stability['coefficient_of_variation'] = cv
        return stability
    
    def _calculate_income_trend(self, monthly_income: pd.Series) -> Dict:
        """Calculate income growth trend"""
        if len(monthly_income) < 3:
            return {'trend': 'Insufficient data', 'monthly_change': 0, 'percentage_change': 0}
        
        # Linear regression to find trend
        x = np.arange(len(monthly_income))
        coeffs = np.polyfit(x, monthly_income.values, 1)
        monthly_change = coeffs[0]
        
        # Percentage change
        avg_income = monthly_income.mean()
        percentage_change = (monthly_change / avg_income * 100) if avg_income > 0 else 0
        
        if percentage_change > 5:
            trend = 'Strong Growth'
        elif percentage_change > 2:
            trend = 'Growing'
        elif percentage_change > -2:
            trend = 'Stable'
        elif percentage_change > -5:
            trend = 'Declining'
        else:
            trend = 'Strong Decline'
        
        return {
            'trend': trend,
            'monthly_change': monthly_change,
            'percentage_change': percentage_change
        }
    
    def _generate_income_recommendations(self, income_df: pd.DataFrame, monthly_income: pd.Series) -> List[str]:
        """Generate income-related recommendations"""
        recommendations = []
        
        # Income diversification
        income_sources = self._infer_income_sources(income_df)
        if len(income_sources) == 1:
            recommendations.append("💡 Consider diversifying your income sources to reduce financial risk")
        
        # Income stability
        if len(monthly_income) >= 2:
            cv = monthly_income.std() / monthly_income.mean()
            if cv > 0.3:
                recommendations.append("📊 Your income varies significantly month-to-month. Consider building a larger emergency fund")
        
        # Income growth
        if len(monthly_income) >= 3:
            recent_avg = monthly_income.tail(3).mean()
            earlier_avg = monthly_income.head(3).mean()
            if recent_avg < earlier_avg * 0.95:
                recommendations.append("📉 Your income has been declining. Consider exploring additional income opportunities")
        
        # Low income warning
        avg_monthly = monthly_income.mean() if len(monthly_income) > 0 else 0
        if avg_monthly < 30000:  # Below average Kenyan salary
            recommendations.append("💰 Consider ways to increase your income through skills development or side hustles")
        
        return recommendations
    
    def calculate_savings_rate(self, df: pd.DataFrame) -> Dict:
        """Calculate accurate savings rate with proper income tracking"""
        # Get income and expenses
        income_df = df[(df['Amount'] > 0) | (df['Category'] == 'Income')].copy()
        expense_df = df[df['Amount'] < 0].copy()
        
        if income_df.empty:
            return {
                'savings_rate': 0,
                'monthly_savings': 0,
                'status': 'No income data available'
            }
        
        # Calculate monthly averages
        income_df['Amount'] = income_df['Amount'].abs()
        expense_df['Amount'] = expense_df['Amount'].abs()
        
        monthly_income = income_df.groupby(pd.Grouper(key='Date', freq='ME'))['Amount'].sum().mean()
        monthly_expenses = expense_df.groupby(pd.Grouper(key='Date', freq='ME'))['Amount'].sum().mean()
        
        monthly_savings = monthly_income - monthly_expenses
        savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
        
        # Determine status
        if savings_rate >= 20:
            status = 'Excellent'
        elif savings_rate >= 10:
            status = 'Good'
        elif savings_rate >= 5:
            status = 'Fair'
        elif savings_rate > 0:
            status = 'Poor'
        else:
            status = 'Negative (Spending more than earning)'
        
        return {
            'savings_rate': savings_rate,
            'monthly_savings': monthly_savings,
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses,
            'status': status
        }
    
    def suggest_income_improvements(self, income_analysis: Dict) -> List[Dict]:
        """Suggest ways to improve income"""
        suggestions = []
        
        monthly_avg = income_analysis['monthly_average']
        stability = income_analysis['income_stability']
        sources = income_analysis['income_sources']
        
        # Low income suggestions
        if monthly_avg < 50000:
            suggestions.append({
                'category': 'Income Growth',
                'suggestion': 'Consider upskilling or certification in high-demand areas like tech, digital marketing, or finance',
                'potential_impact': 'Could increase income by 30-50%',
                'effort': 'High',
                'timeframe': '6-12 months'
            })
        
        # Single income source
        if len(sources) <= 1:
            suggestions.append({
                'category': 'Income Diversification',
                'suggestion': 'Start a side hustle like online tutoring, freelance writing, or small business',
                'potential_impact': 'Additional KSh 10,000-30,000/month',
                'effort': 'Medium',
                'timeframe': '2-6 months'
            })
        
        # Unstable income
        if stability['score'] < 0.6:
            suggestions.append({
                'category': 'Income Stability',
                'suggestion': 'Look for more stable employment or create recurring revenue streams',
                'potential_impact': 'More predictable monthly income',
                'effort': 'High',
                'timeframe': '3-12 months'
            })
        
        # Investment opportunities
        if monthly_avg > 30000:
            suggestions.append({
                'category': 'Passive Income',
                'suggestion': 'Consider investing in money market funds, SACCOs, or dividend-paying stocks',
                'potential_impact': '8-15% annual returns',
                'effort': 'Low',
                'timeframe': '1-3 months to start'
            })
        
        return suggestions
    
    def create_income_dashboard_data(self, income_analysis: Dict) -> Dict:
        """Create dashboard data for income visualization"""
        return {
            'total_income': income_analysis['total_income'],
            'monthly_average': income_analysis['monthly_average'],
            'income_sources': income_analysis['income_sources'],
            'stability_score': income_analysis['income_stability']['score'],
            'stability_description': income_analysis['income_stability']['description'],
            'growth_trend': income_analysis['growth_trend']['trend'],
            'monthly_change': income_analysis['growth_trend']['monthly_change'],
            'recommendations': income_analysis['recommendations']
        }