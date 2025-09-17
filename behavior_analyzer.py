import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from markov_predictor import MarkovChainPredictor

class BehaviorAnalyzer:
    """
    Advanced behavioral analysis using Markov Chains for financial data.
    
    Features:
    - Spending behavior modeling
    - Pattern recognition
    - Anomaly detection
    - Predictive analytics
    - Behavioral insights
    """
    
    def __init__(self):
        self.markov_model = MarkovChainPredictor(order=2)
        self.behavior_profiles = {}
        self.spending_patterns = {}
        
    def analyze_behavior(self, df: pd.DataFrame) -> Dict:
        """Comprehensive behavioral analysis"""
        print("🧠 Analyzing spending behavior with Markov Chains...")
        
        # Train the Markov model
        self.markov_model.train(df)
        
        # Perform various analyses
        analysis = {
            'behavioral_patterns': self.markov_model.analyze_behavioral_patterns(),
            'spending_predictions': self._generate_spending_predictions(df),
            'anomaly_detection': self._detect_spending_anomalies(df),
            'habit_analysis': self._analyze_spending_habits(df),
            'temporal_insights': self._analyze_temporal_behavior(df),
            'risk_assessment': self._assess_behavioral_risks(df),
            'recommendations': self._generate_behavioral_recommendations(df)
        }
        
        return analysis
    
    def _generate_spending_predictions(self, df: pd.DataFrame) -> Dict:
        """Generate various spending predictions"""
        predictions = {}
        
        # Get unique categories for predictions
        categories = df['Category'].unique()
        
        # Predict next transactions for each major category
        for category in categories[:5]:  # Top 5 categories
            category_df = df[df['Category'] == category]
            if len(category_df) > 0:
                # Get last state for this category
                df_with_states = self.markov_model.create_states(category_df)
                if not df_with_states.empty:
                    last_state = df_with_states.iloc[-1]['State_Sequence']
                    next_predictions = self.markov_model.predict_next_transaction(last_state)
                    predictions[category] = next_predictions
        
        # Predict spending sequences
        predictions['spending_sequences'] = {}
        for category in categories[:3]:
            sequences = self.markov_model.predict_spending_sequence(category, 4)
            predictions['spending_sequences'][category] = sequences
        
        # Monthly spending predictions
        predictions['monthly_forecast'] = self.markov_model.predict_monthly_spending()
        
        return predictions
    
    def _detect_spending_anomalies(self, df: pd.DataFrame) -> Dict:
        """Detect anomalous spending behavior"""
        anomalies = self.markov_model.detect_anomalies(df, threshold=0.1)
        
        analysis = {
            'total_anomalies': len(anomalies),
            'anomaly_rate': len(anomalies) / len(df) * 100 if len(df) > 0 else 0,
            'anomalies': anomalies.to_dict('records') if not anomalies.empty else [],
            'anomaly_categories': anomalies['category'].value_counts().to_dict() if not anomalies.empty else {},
            'high_risk_anomalies': anomalies[anomalies['anomaly_score'] > 0.8].to_dict('records') if not anomalies.empty else []
        }
        
        return analysis
    
    def _analyze_spending_habits(self, df: pd.DataFrame) -> Dict:
        """Analyze spending habits and patterns"""
        habits = {}
        
        # Daily spending patterns
        daily_spending = df.groupby(df['Date'].dt.day_name()).agg({
            'Amount': ['count', 'sum', 'mean'],
            'Category': lambda x: x.mode().iloc[0] if not x.empty else 'Unknown'
        }).round(2)
        
        habits['daily_patterns'] = daily_spending.to_dict()
        
        # Weekly patterns
        df['Week'] = df['Date'].dt.isocalendar().week
        weekly_spending = df.groupby('Week')['Amount'].sum()
        habits['weekly_consistency'] = {
            'std_deviation': weekly_spending.std(),
            'coefficient_variation': weekly_spending.std() / weekly_spending.mean() if weekly_spending.mean() != 0 else 0
        }
        
        # Category loyalty (how often user sticks to same categories)
        category_sequences = df['Category'].tolist()
        same_category_count = sum(1 for i in range(1, len(category_sequences)) 
                                 if category_sequences[i] == category_sequences[i-1])
        habits['category_loyalty'] = same_category_count / (len(category_sequences) - 1) if len(category_sequences) > 1 else 0
        
        # Spending velocity (transactions per day)
        date_range = (df['Date'].max() - df['Date'].min()).days
        habits['spending_velocity'] = len(df) / date_range if date_range > 0 else 0
        
        return habits
    
    def _analyze_temporal_behavior(self, df: pd.DataFrame) -> Dict:
        """Analyze temporal spending behavior"""
        temporal = {}
        
        # Hour-based analysis (if time data available)
        if 'Time' in df.columns:
            df['Hour'] = pd.to_datetime(df['Time']).dt.hour
            hourly_spending = df.groupby('Hour')['Amount'].agg(['count', 'sum', 'mean'])
            temporal['hourly_patterns'] = hourly_spending.to_dict()
        
        # Month-based trends
        df['Month'] = df['Date'].dt.month
        monthly_trends = df.groupby('Month').agg({
            'Amount': ['count', 'sum', 'mean'],
            'Category': lambda x: x.value_counts().index[0] if not x.empty else 'Unknown'
        })
        temporal['monthly_trends'] = monthly_trends.to_dict()
        
        # Weekend vs weekday behavior
        df['Is_Weekend'] = df['Date'].dt.weekday >= 5
        weekend_analysis = df.groupby('Is_Weekend').agg({
            'Amount': ['count', 'sum', 'mean'],
            'Category': lambda x: x.value_counts().to_dict()
        })
        temporal['weekend_behavior'] = weekend_analysis.to_dict()
        
        # Time between transactions
        df_sorted = df.sort_values('Date')
        time_diffs = df_sorted['Date'].diff().dt.total_seconds() / 3600  # hours
        temporal['transaction_intervals'] = {
            'mean_hours': time_diffs.mean(),
            'std_hours': time_diffs.std(),
            'median_hours': time_diffs.median()
        }
        
        return temporal
    
    def _assess_behavioral_risks(self, df: pd.DataFrame) -> Dict:
        """Assess behavioral risks based on patterns"""
        risks = {}
        
        # Impulsive spending risk (many small transactions in short time)
        df_sorted = df.sort_values('Date')
        small_transactions = df_sorted[df_sorted['Amount'].abs() < df_sorted['Amount'].abs().median()]
        
        # Check for clusters of small transactions
        time_diffs = small_transactions['Date'].diff().dt.total_seconds() / 3600
        impulsive_clusters = sum(1 for diff in time_diffs if diff < 2)  # Within 2 hours
        
        risks['impulsive_spending'] = {
            'risk_score': min(impulsive_clusters / len(df) * 10, 1.0),  # Normalize to 0-1
            'cluster_count': impulsive_clusters,
            'description': 'High' if impulsive_clusters / len(df) > 0.1 else 'Low'
        }
        
        # Budget deviation risk
        monthly_spending = df.groupby(df['Date'].dt.to_period('M'))['Amount'].sum().abs()
        spending_volatility = monthly_spending.std() / monthly_spending.mean() if monthly_spending.mean() != 0 else 0
        
        risks['spending_volatility'] = {
            'risk_score': min(spending_volatility, 1.0),
            'coefficient_variation': spending_volatility,
            'description': 'High' if spending_volatility > 0.3 else 'Medium' if spending_volatility > 0.15 else 'Low'
        }
        
        # Category concentration risk
        category_distribution = df['Category'].value_counts(normalize=True)
        concentration_risk = category_distribution.iloc[0] if not category_distribution.empty else 0
        
        risks['category_concentration'] = {
            'risk_score': concentration_risk,
            'top_category_percentage': concentration_risk * 100,
            'description': 'High' if concentration_risk > 0.6 else 'Medium' if concentration_risk > 0.4 else 'Low'
        }
        
        return risks
    
    def _generate_behavioral_recommendations(self, df: pd.DataFrame) -> List[Dict]:
        """Generate behavioral recommendations based on analysis"""
        recommendations = []
        
        # Analyze patterns for recommendations
        behavioral_patterns = self.markov_model.analyze_behavioral_patterns()
        
        # Spending habit recommendations
        habits = self._analyze_spending_habits(df)
        
        if habits['category_loyalty'] < 0.3:
            recommendations.append({
                'type': 'Spending Consistency',
                'priority': 'Medium',
                'title': 'Improve Spending Consistency',
                'description': 'Your spending patterns are quite varied. Consider establishing more consistent spending routines.',
                'action': 'Set specific days for different types of purchases (e.g., groceries on weekends)',
                'impact': 'Better budget control and reduced impulsive spending'
            })
        
        if habits['spending_velocity'] > 5:  # More than 5 transactions per day
            recommendations.append({
                'type': 'Transaction Frequency',
                'priority': 'High',
                'title': 'Reduce Transaction Frequency',
                'description': f'You average {habits["spending_velocity"]:.1f} transactions per day, which may indicate impulsive spending.',
                'action': 'Consolidate purchases and plan shopping trips',
                'impact': 'Reduced fees and better spending awareness'
            })
        
        # Temporal recommendations
        temporal = self._analyze_temporal_behavior(df)
        
        if 'weekend_behavior' in temporal:
            weekend_data = temporal['weekend_behavior']
            # Check if weekend spending is significantly higher
            if 'Amount' in weekend_data and 'sum' in weekend_data['Amount']:
                weekend_spending = weekend_data['Amount']['sum'].get(True, 0)
                weekday_spending = weekend_data['Amount']['sum'].get(False, 0)
                
                if weekend_spending > weekday_spending * 1.5:
                    recommendations.append({
                        'type': 'Weekend Spending',
                        'priority': 'Medium',
                        'title': 'Monitor Weekend Spending',
                        'description': 'Your weekend spending is significantly higher than weekdays.',
                        'action': 'Set weekend spending limits and plan leisure activities',
                        'impact': 'Better monthly budget control'
                    })
        
        # Risk-based recommendations
        risks = self._assess_behavioral_risks(df)
        
        if risks['impulsive_spending']['risk_score'] > 0.3:
            recommendations.append({
                'type': 'Impulse Control',
                'priority': 'High',
                'title': 'Control Impulsive Spending',
                'description': 'Pattern analysis shows potential impulsive spending behavior.',
                'action': 'Implement a 24-hour waiting period for non-essential purchases',
                'impact': 'Significant reduction in unnecessary expenses'
            })
        
        if risks['spending_volatility']['risk_score'] > 0.4:
            recommendations.append({
                'type': 'Budget Stability',
                'priority': 'High',
                'title': 'Stabilize Monthly Spending',
                'description': 'Your monthly spending varies significantly, making budgeting difficult.',
                'action': 'Create and stick to monthly spending limits by category',
                'impact': 'More predictable finances and better savings'
            })
        
        return recommendations
    
    def create_behavior_dashboard(self, analysis: Dict) -> Dict:
        """Create dashboard data for behavior visualization"""
        dashboard = {
            'summary_metrics': self._create_summary_metrics(analysis),
            'prediction_charts': self._create_prediction_charts(analysis),
            'pattern_visualizations': self._create_pattern_visualizations(analysis),
            'risk_indicators': self._create_risk_indicators(analysis),
            'recommendations': analysis.get('recommendations', [])
        }
        
        return dashboard
    
    def _create_summary_metrics(self, analysis: Dict) -> Dict:
        """Create summary metrics for dashboard"""
        patterns = analysis.get('behavioral_patterns', {})
        anomalies = analysis.get('anomaly_detection', {})
        risks = analysis.get('risk_assessment', {})
        
        return {
            'behavior_score': self._calculate_behavior_score(analysis),
            'predictability': self._calculate_predictability_score(patterns),
            'anomaly_rate': anomalies.get('anomaly_rate', 0),
            'risk_level': self._calculate_overall_risk(risks)
        }
    
    def _calculate_behavior_score(self, analysis: Dict) -> float:
        """Calculate overall behavior score (0-100)"""
        # Combine various factors
        risks = analysis.get('risk_assessment', {})
        anomaly_rate = analysis.get('anomaly_detection', {}).get('anomaly_rate', 0)
        
        # Start with base score
        score = 100
        
        # Deduct for risks
        for risk_type, risk_data in risks.items():
            if isinstance(risk_data, dict) and 'risk_score' in risk_data:
                score -= risk_data['risk_score'] * 20  # Max 20 points per risk
        
        # Deduct for anomalies
        score -= min(anomaly_rate * 2, 30)  # Max 30 points for anomalies
        
        return max(score, 0)
    
    def _calculate_predictability_score(self, patterns: Dict) -> float:
        """Calculate how predictable the spending behavior is"""
        # Based on transition probabilities and pattern consistency
        transitions = patterns.get('most_common_transitions', [])
        
        if not transitions:
            return 0.0
        
        # Average probability of top transitions
        avg_probability = np.mean([t['probability'] for t in transitions[:5]])
        return avg_probability * 100
    
    def _calculate_overall_risk(self, risks: Dict) -> str:
        """Calculate overall risk level"""
        if not risks:
            return 'Unknown'
        
        risk_scores = []
        for risk_data in risks.values():
            if isinstance(risk_data, dict) and 'risk_score' in risk_data:
                risk_scores.append(risk_data['risk_score'])
        
        if not risk_scores:
            return 'Low'
        
        avg_risk = np.mean(risk_scores)
        
        if avg_risk > 0.7:
            return 'High'
        elif avg_risk > 0.4:
            return 'Medium'
        else:
            return 'Low'
    
    def _create_prediction_charts(self, analysis: Dict) -> Dict:
        """Create prediction chart data"""
        predictions = analysis.get('spending_predictions', {})
        
        charts = {}
        
        # Monthly forecast chart
        monthly_forecast = predictions.get('monthly_forecast', {})
        if monthly_forecast:
            categories = list(monthly_forecast.keys())
            amounts = [data['predicted_amount'] for data in monthly_forecast.values()]
            
            charts['monthly_forecast'] = {
                'categories': categories,
                'amounts': amounts,
                'chart_type': 'bar'
            }
        
        return charts
    
    def _create_pattern_visualizations(self, analysis: Dict) -> Dict:
        """Create pattern visualization data"""
        patterns = analysis.get('behavioral_patterns', {})
        
        visualizations = {}
        
        # Top transitions
        transitions = patterns.get('most_common_transitions', [])[:10]
        if transitions:
            visualizations['top_transitions'] = {
                'labels': [f"{t['from_state']} → {t['to_state']}" for t in transitions],
                'values': [t['probability'] for t in transitions],
                'chart_type': 'horizontal_bar'
            }
        
        return visualizations
    
    def _create_risk_indicators(self, analysis: Dict) -> Dict:
        """Create risk indicator data"""
        risks = analysis.get('risk_assessment', {})
        
        indicators = {}
        
        for risk_type, risk_data in risks.items():
            if isinstance(risk_data, dict):
                indicators[risk_type] = {
                    'score': risk_data.get('risk_score', 0),
                    'level': risk_data.get('description', 'Unknown'),
                    'color': self._get_risk_color(risk_data.get('risk_score', 0))
                }
        
        return indicators
    
    def _get_risk_color(self, score: float) -> str:
        """Get color for risk score"""
        if score > 0.7:
            return 'red'
        elif score > 0.4:
            return 'orange'
        else:
            return 'green'