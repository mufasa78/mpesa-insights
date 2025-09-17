import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import streamlit as st

class FinancialHealthAnalyzer:
    def __init__(self):
        self.health_metrics = {
            'expense_volatility': {'weight': 0.2, 'ideal_range': (0, 0.3)},
            'savings_rate': {'weight': 0.3, 'ideal_range': (0.2, 0.5)},
            'category_balance': {'weight': 0.2, 'ideal_range': (0.7, 1.0)},
            'spending_trend': {'weight': 0.15, 'ideal_range': (-0.05, 0.05)},
            'emergency_fund_ratio': {'weight': 0.15, 'ideal_range': (3, 6)}
        }
    
    def calculate_financial_health_score(self, df: pd.DataFrame) -> Dict:
        """Calculate overall financial health score"""
        scores = {}
        
        # 1. Expense Volatility (lower is better)
        volatility_score = self._calculate_expense_volatility(df)
        scores['expense_volatility'] = volatility_score
        
        # 2. Savings Rate (higher is better)
        savings_score = self._calculate_savings_rate(df)
        scores['savings_rate'] = savings_score
        
        # 3. Category Balance (balanced spending is better)
        balance_score = self._calculate_category_balance(df)
        scores['category_balance'] = balance_score
        
        # 4. Spending Trend (stable is better)
        trend_score = self._calculate_spending_trend(df)
        scores['spending_trend'] = trend_score
        
        # 5. Emergency Fund Ratio (estimated)
        emergency_score = self._estimate_emergency_fund_ratio(df)
        scores['emergency_fund_ratio'] = emergency_score
        
        # Calculate weighted overall score
        overall_score = sum(
            scores[metric] * self.health_metrics[metric]['weight']
            for metric in scores
        )
        
        return {
            'overall_score': overall_score,
            'individual_scores': scores,
            'grade': self._get_health_grade(overall_score),
            'recommendations': self._generate_health_recommendations(scores)
        }
    
    def _calculate_expense_volatility(self, df: pd.DataFrame) -> float:
        """Calculate expense volatility (coefficient of variation)"""
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        monthly_expenses = expenses_df.groupby(
            pd.Grouper(key='Date', freq='ME')
        )['Amount'].sum()
        
        if len(monthly_expenses) < 2:
            return 0.5  # Neutral score for insufficient data
        
        cv = monthly_expenses.std() / monthly_expenses.mean()
        
        # Convert to score (0-1, where 1 is best)
        ideal_min, ideal_max = self.health_metrics['expense_volatility']['ideal_range']
        if cv <= ideal_max:
            return 1.0
        elif cv <= ideal_max * 2:
            return 1.0 - (cv - ideal_max) / ideal_max
        else:
            return 0.0
    
    def _calculate_savings_rate(self, df: pd.DataFrame) -> float:
        """Calculate estimated savings rate"""
        income = df[df['Amount'] > 0]['Amount'].sum()
        expenses = df[df['Amount'] < 0]['Amount'].sum()
        
        if income <= 0:
            return 0.0
        
        savings_rate = (income + expenses) / income  # expenses are negative
        
        # Convert to score
        ideal_min, ideal_max = self.health_metrics['savings_rate']['ideal_range']
        if savings_rate >= ideal_min:
            return min(1.0, savings_rate / ideal_max)
        else:
            return savings_rate / ideal_min
    
    def _calculate_category_balance(self, df: pd.DataFrame) -> float:
        """Calculate how balanced spending is across categories"""
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        category_totals = expenses_df.groupby('Category')['Amount'].sum()
        total_expenses = category_totals.sum()
        
        if total_expenses == 0:
            return 0.5
        
        # Calculate entropy (higher entropy = more balanced)
        proportions = category_totals / total_expenses
        entropy = -sum(p * np.log(p) for p in proportions if p > 0)
        max_entropy = np.log(len(category_totals))
        
        balance_score = entropy / max_entropy if max_entropy > 0 else 0
        
        return balance_score
    
    def _calculate_spending_trend(self, df: pd.DataFrame) -> float:
        """Calculate spending trend (stable is better)"""
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        monthly_expenses = expenses_df.groupby(
            pd.Grouper(key='Date', freq='ME')
        )['Amount'].sum()
        
        if len(monthly_expenses) < 3:
            return 0.5
        
        # Calculate trend using linear regression
        x = np.arange(len(monthly_expenses))
        coeffs = np.polyfit(x, monthly_expenses.values, 1)
        trend = coeffs[0] / monthly_expenses.mean()  # Normalize by average
        
        # Convert to score (stable trend = high score)
        ideal_min, ideal_max = self.health_metrics['spending_trend']['ideal_range']
        if ideal_min <= trend <= ideal_max:
            return 1.0
        else:
            return max(0.0, 1.0 - abs(trend) * 10)
    
    def _estimate_emergency_fund_ratio(self, df: pd.DataFrame) -> float:
        """Estimate emergency fund ratio based on cash flow"""
        # This is a rough estimate based on available data
        monthly_expenses = df[df['Amount'] < 0].groupby(
            pd.Grouper(key='Date', freq='ME')
        )['Amount'].sum().abs().mean()
        
        # Estimate current balance from last balance in data
        if 'Balance' in df.columns:
            current_balance = df['Balance'].iloc[-1] if not df.empty else 0
        else:
            current_balance = df['Amount'].sum()  # Net flow
        
        if monthly_expenses <= 0:
            return 0.5
        
        emergency_ratio = current_balance / monthly_expenses
        
        # Convert to score
        ideal_min, ideal_max = self.health_metrics['emergency_fund_ratio']['ideal_range']
        if emergency_ratio >= ideal_min:
            return min(1.0, emergency_ratio / ideal_max)
        else:
            return emergency_ratio / ideal_min
    
    def _get_health_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 0.9:
            return 'A+'
        elif score >= 0.8:
            return 'A'
        elif score >= 0.7:
            return 'B'
        elif score >= 0.6:
            return 'C'
        elif score >= 0.5:
            return 'D'
        else:
            return 'F'
    
    def _generate_health_recommendations(self, scores: Dict) -> List[str]:
        """Generate recommendations based on scores"""
        recommendations = []
        
        if scores['expense_volatility'] < 0.6:
            recommendations.append("🎯 Your expenses are quite volatile. Try to create a monthly budget and stick to it.")
        
        if scores['savings_rate'] < 0.5:
            recommendations.append("💰 Your savings rate could be improved. Aim to save at least 20% of your income.")
        
        if scores['category_balance'] < 0.6:
            recommendations.append("⚖️ Your spending is concentrated in few categories. Consider diversifying your expenses.")
        
        if scores['spending_trend'] < 0.5:
            recommendations.append("📈 Your spending trend shows significant changes. Try to maintain consistent spending habits.")
        
        if scores['emergency_fund_ratio'] < 0.5:
            recommendations.append("🚨 Build an emergency fund covering 3-6 months of expenses.")
        
        return recommendations
    
    def generate_financial_wellness_tips(self, df: pd.DataFrame) -> List[Dict]:
        """Generate personalized financial wellness tips"""
        tips = []
        
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        # Tip 1: 50/30/20 Rule Analysis
        total_expenses = expenses_df['Amount'].sum()
        needs_categories = ['Food', 'Utilities', 'Transport', 'Health']
        wants_categories = ['Entertainment', 'Shopping']
        
        needs_spending = expenses_df[expenses_df['Category'].isin(needs_categories)]['Amount'].sum()
        wants_spending = expenses_df[expenses_df['Category'].isin(wants_categories)]['Amount'].sum()
        
        needs_percentage = (needs_spending / total_expenses * 100) if total_expenses > 0 else 0
        wants_percentage = (wants_spending / total_expenses * 100) if total_expenses > 0 else 0
        
        tips.append({
            'title': '50/30/20 Rule Analysis',
            'description': f"Needs: {needs_percentage:.1f}% (target: 50%), Wants: {wants_percentage:.1f}% (target: 30%)",
            'recommendation': "Adjust your spending to follow the 50/30/20 rule: 50% needs, 30% wants, 20% savings",
            'priority': 'high' if needs_percentage > 60 or wants_percentage > 40 else 'medium'
        })
        
        # Tip 2: Subscription Audit
        recurring_keywords = ['subscription', 'monthly', 'annual', 'netflix', 'spotify', 'dstv']
        subscriptions = expenses_df[
            expenses_df['Details'].str.contains('|'.join(recurring_keywords), case=False, na=False)
        ]
        
        if not subscriptions.empty:
            subscription_cost = subscriptions['Amount'].sum()
            tips.append({
                'title': 'Subscription Audit',
                'description': f"You spend KSh {subscription_cost:,.2f} on subscriptions",
                'recommendation': "Review all subscriptions and cancel unused ones. This could save you 20-30% monthly.",
                'priority': 'medium'
            })
        
        # Tip 3: Cash Flow Timing
        df_with_day = df.copy()
        df_with_day['Day'] = df_with_day['Date'].dt.day
        
        spending_by_day = df_with_day[df_with_day['Amount'] < 0].groupby('Day')['Amount'].sum().abs()
        
        if not spending_by_day.empty:
            peak_spending_day = spending_by_day.idxmax()
            tips.append({
                'title': 'Spending Pattern Insight',
                'description': f"You tend to spend most on day {peak_spending_day} of the month",
                'recommendation': "Be extra mindful of spending during your peak spending periods",
                'priority': 'low'
            })
        
        return tips
    
    def create_financial_health_dashboard(self, health_data: Dict) -> Dict:
        """Create dashboard data for financial health visualization"""
        scores = health_data['individual_scores']
        
        dashboard_data = {
            'overall_score': health_data['overall_score'],
            'grade': health_data['grade'],
            'metrics': [
                {
                    'name': 'Expense Stability',
                    'score': scores['expense_volatility'],
                    'description': 'How consistent your monthly expenses are',
                    'status': 'Good' if scores['expense_volatility'] > 0.7 else 'Needs Improvement'
                },
                {
                    'name': 'Savings Rate',
                    'score': scores['savings_rate'],
                    'description': 'Percentage of income saved',
                    'status': 'Good' if scores['savings_rate'] > 0.7 else 'Needs Improvement'
                },
                {
                    'name': 'Spending Balance',
                    'score': scores['category_balance'],
                    'description': 'How balanced your spending is across categories',
                    'status': 'Good' if scores['category_balance'] > 0.7 else 'Needs Improvement'
                },
                {
                    'name': 'Spending Trend',
                    'score': scores['spending_trend'],
                    'description': 'Stability of your spending over time',
                    'status': 'Good' if scores['spending_trend'] > 0.7 else 'Needs Improvement'
                },
                {
                    'name': 'Emergency Preparedness',
                    'score': scores['emergency_fund_ratio'],
                    'description': 'Estimated emergency fund coverage',
                    'status': 'Good' if scores['emergency_fund_ratio'] > 0.7 else 'Needs Improvement'
                }
            ]
        }
        
        return dashboard_data