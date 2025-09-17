import pandas as pd
import numpy as np
from typing import Dict, List
import streamlit as st

class SpendingComparator:
    def __init__(self):
        # Benchmark data for different income levels in Kenya (monthly)
        self.income_benchmarks = {
            'low': {  # Below 50K
                'Food': {'min': 8000, 'max': 15000, 'optimal': 12000},
                'Transport': {'min': 3000, 'max': 8000, 'optimal': 5000},
                'Utilities': {'min': 2000, 'max': 5000, 'optimal': 3500},
                'Entertainment': {'min': 1000, 'max': 3000, 'optimal': 2000},
                'Shopping': {'min': 2000, 'max': 6000, 'optimal': 4000},
                'Health': {'min': 1000, 'max': 3000, 'optimal': 2000}
            },
            'medium': {  # 50K - 150K
                'Food': {'min': 15000, 'max': 30000, 'optimal': 22000},
                'Transport': {'min': 8000, 'max': 20000, 'optimal': 12000},
                'Utilities': {'min': 5000, 'max': 12000, 'optimal': 8000},
                'Entertainment': {'min': 3000, 'max': 10000, 'optimal': 6000},
                'Shopping': {'min': 6000, 'max': 15000, 'optimal': 10000},
                'Health': {'min': 3000, 'max': 8000, 'optimal': 5000}
            },
            'high': {  # Above 150K
                'Food': {'min': 25000, 'max': 50000, 'optimal': 35000},
                'Transport': {'min': 15000, 'max': 35000, 'optimal': 25000},
                'Utilities': {'min': 10000, 'max': 20000, 'optimal': 15000},
                'Entertainment': {'min': 8000, 'max': 20000, 'optimal': 12000},
                'Shopping': {'min': 10000, 'max': 30000, 'optimal': 20000},
                'Health': {'min': 5000, 'max': 15000, 'optimal': 10000}
            }
        }
    
    def estimate_income_bracket(self, df: pd.DataFrame, actual_income: float = None) -> str:
        """Estimate user's income bracket based on actual income or spending patterns"""
        
        if actual_income and actual_income > 0:
            # Use actual income if available
            estimated_income = actual_income
        else:
            # Fall back to estimation from expenses
            expenses_df = df[df['Amount'] < 0].copy()
            expenses_df['Amount'] = expenses_df['Amount'].abs()
            
            monthly_expenses = expenses_df.groupby(
                pd.Grouper(key='Date', freq='ME')
            )['Amount'].sum().mean()
            
            # Rough estimate: expenses are typically 60-80% of income
            estimated_income = monthly_expenses / 0.7
        
        if estimated_income < 50000:
            return 'low'
        elif estimated_income < 150000:
            return 'medium'
        else:
            return 'high'
    
    def compare_with_benchmarks(self, df: pd.DataFrame, actual_income: float = None) -> Dict:
        """Compare user's spending with benchmarks"""
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        # Get monthly averages by category
        monthly_spending = expenses_df.groupby([
            pd.Grouper(key='Date', freq='ME'),
            'Category'
        ])['Amount'].sum().reset_index()
        
        avg_monthly_spending = monthly_spending.groupby('Category')['Amount'].mean()
        
        # Estimate income bracket
        income_bracket = self.estimate_income_bracket(df, actual_income)
        benchmarks = self.income_benchmarks[income_bracket]
        
        comparison = {}
        
        for category, amount in avg_monthly_spending.items():
            if category in benchmarks:
                benchmark = benchmarks[category]
                
                if amount <= benchmark['optimal'] * 1.1:  # Within 10% of optimal
                    status = 'optimal'
                elif amount <= benchmark['max']:
                    status = 'acceptable'
                else:
                    status = 'high'
                
                comparison[category] = {
                    'your_spending': amount,
                    'optimal_spending': benchmark['optimal'],
                    'benchmark_range': f"{benchmark['min']:,.0f} - {benchmark['max']:,.0f}",
                    'status': status,
                    'difference_from_optimal': amount - benchmark['optimal'],
                    'percentage_of_optimal': (amount / benchmark['optimal']) * 100
                }
        
        return {
            'income_bracket': income_bracket,
            'comparisons': comparison,
            'overall_score': self._calculate_spending_score(comparison)
        }
    
    def _calculate_spending_score(self, comparison: Dict) -> Dict:
        """Calculate an overall spending efficiency score"""
        scores = []
        
        for category, data in comparison.items():
            if data['status'] == 'optimal':
                scores.append(100)
            elif data['status'] == 'acceptable':
                scores.append(75)
            else:
                # Score decreases as spending increases above optimal
                excess_percentage = (data['percentage_of_optimal'] - 100) / 100
                score = max(0, 50 - (excess_percentage * 25))
                scores.append(score)
        
        overall_score = np.mean(scores) if scores else 0
        
        if overall_score >= 85:
            grade = 'A'
            message = "Excellent spending habits!"
        elif overall_score >= 70:
            grade = 'B'
            message = "Good spending habits with room for improvement"
        elif overall_score >= 55:
            grade = 'C'
            message = "Average spending habits, consider optimization"
        else:
            grade = 'D'
            message = "Spending habits need significant improvement"
        
        return {
            'score': overall_score,
            'grade': grade,
            'message': message
        }
    
    def find_cost_saving_alternatives(self, df: pd.DataFrame) -> List[Dict]:
        """Suggest cost-saving alternatives based on spending patterns"""
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        alternatives = []
        
        # Analyze frequent merchants/services
        merchant_spending = expenses_df.groupby('Details')['Amount'].agg(['sum', 'count', 'mean']).reset_index()
        merchant_spending = merchant_spending[merchant_spending['count'] >= 3]  # At least 3 transactions
        merchant_spending = merchant_spending.sort_values('sum', ascending=False)
        
        for _, row in merchant_spending.head(10).iterrows():
            details = row['Details'].lower()
            total_spent = row['sum']
            avg_transaction = row['mean']
            
            # Food alternatives
            if any(word in details for word in ['restaurant', 'hotel', 'cafe', 'kfc', 'pizza']):
                alternatives.append({
                    'category': 'Food',
                    'current_expense': f"{row['Details']} - KSh {total_spent:,.2f}",
                    'alternative': "Cook at home or try local eateries",
                    'potential_savings': total_spent * 0.4,
                    'effort_level': 'Medium'
                })
            
            # Transport alternatives
            elif any(word in details for word in ['uber', 'bolt', 'taxi']):
                alternatives.append({
                    'category': 'Transport',
                    'current_expense': f"Ride-hailing - KSh {total_spent:,.2f}",
                    'alternative': "Use matatus or walk for short distances",
                    'potential_savings': total_spent * 0.6,
                    'effort_level': 'Medium'
                })
            
            # Shopping alternatives
            elif any(word in details for word in ['supermarket', 'mall', 'shop']):
                if avg_transaction > 2000:
                    alternatives.append({
                        'category': 'Shopping',
                        'current_expense': f"{row['Details']} - KSh {total_spent:,.2f}",
                        'alternative': "Compare prices, use shopping lists, buy in bulk",
                        'potential_savings': total_spent * 0.15,
                        'effort_level': 'Low'
                    })
        
        return alternatives
    
    def analyze_spending_efficiency(self, df: pd.DataFrame) -> Dict:
        """Analyze how efficiently money is being spent"""
        expenses_df = df[df['Amount'] < 0].copy()
        expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        # Calculate spending per transaction by category
        category_efficiency = expenses_df.groupby('Category').agg({
            'Amount': ['sum', 'count', 'mean', 'std']
        }).round(2)
        
        category_efficiency.columns = ['total', 'transactions', 'avg_per_transaction', 'std_dev']
        
        efficiency_insights = {}
        
        for category in category_efficiency.index:
            data = category_efficiency.loc[category]
            
            # Calculate coefficient of variation (std/mean) - lower is more consistent
            cv = data['std_dev'] / data['avg_per_transaction'] if data['avg_per_transaction'] > 0 else 0
            
            if cv < 0.5:
                consistency = 'Very Consistent'
            elif cv < 1.0:
                consistency = 'Consistent'
            elif cv < 1.5:
                consistency = 'Somewhat Variable'
            else:
                consistency = 'Highly Variable'
            
            efficiency_insights[category] = {
                'total_spent': data['total'],
                'number_of_transactions': data['transactions'],
                'average_per_transaction': data['avg_per_transaction'],
                'spending_consistency': consistency,
                'coefficient_of_variation': cv
            }
        
        return efficiency_insights
    
    def generate_peer_comparison_insights(self, comparison_data: Dict) -> List[str]:
        """Generate insights based on peer comparison"""
        insights = []
        
        income_bracket = comparison_data['income_bracket']
        comparisons = comparison_data['comparisons']
        
        insights.append(f"📊 Based on your spending patterns, you're in the '{income_bracket}' income bracket")
        
        # Categories where user is doing well
        optimal_categories = [cat for cat, data in comparisons.items() if data['status'] == 'optimal']
        if optimal_categories:
            insights.append(f"✅ You're spending optimally on: {', '.join(optimal_categories)}")
        
        # Categories that need attention
        high_categories = [cat for cat, data in comparisons.items() if data['status'] == 'high']
        if high_categories:
            insights.append(f"⚠️ Consider reducing spending on: {', '.join(high_categories)}")
        
        # Specific recommendations
        for category, data in comparisons.items():
            if data['status'] == 'high':
                excess = data['difference_from_optimal']
                insights.append(f"💡 {category}: You're spending KSh {excess:,.2f} above optimal. Try to reduce by 20-30%")
        
        return insights