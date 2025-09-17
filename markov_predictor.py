import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class MarkovChainPredictor:
    """
    Advanced Markov Chain system for financial behavior modeling and prediction.
    
    Features:
    - Transaction sequence prediction
    - Spending pattern analysis
    - Behavioral state modeling
    - Anomaly detection
    - Budget forecasting
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize Markov Chain predictor
        
        Args:
            order: Order of Markov chain (1=first-order, 2=second-order, etc.)
        """
        self.order = order
        self.transition_matrix = defaultdict(lambda: defaultdict(float))
        self.state_frequencies = defaultdict(int)
        self.category_transitions = defaultdict(lambda: defaultdict(float))
        self.amount_transitions = defaultdict(lambda: defaultdict(list))
        self.time_transitions = defaultdict(lambda: defaultdict(list))
        self.behavioral_states = {}
        self.is_trained = False
        
    def create_states(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create behavioral states from transaction data"""
        df = df.copy()
        
        # Create composite states combining multiple features
        df['Amount_Bin'] = pd.cut(df['Amount'].abs(), 
                                 bins=5, 
                                 labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
        
        df['Day_of_Week'] = df['Date'].dt.day_name()
        df['Hour'] = df['Date'].dt.hour if 'Time' in df.columns else 12  # Default to noon
        df['Time_Period'] = df['Hour'].apply(self._get_time_period)
        
        # Create behavioral state
        df['Behavioral_State'] = (
            df['Category'].astype(str) + '_' + 
            df['Amount_Bin'].astype(str) + '_' + 
            df['Time_Period'].astype(str)
        )
        
        # Create sequence states for higher-order chains
        if self.order > 1:
            # Create sequences manually to avoid rolling window issues with strings
            sequences = []
            for i in range(len(df)):
                start_idx = max(0, i - self.order + 1)
                sequence_states = df['Behavioral_State'].iloc[start_idx:i+1].tolist()
                sequences.append('|'.join(sequence_states))
            df['State_Sequence'] = sequences
        else:
            df['State_Sequence'] = df['Behavioral_State']
        
        return df
    
    def _get_time_period(self, hour: int) -> str:
        """Convert hour to time period"""
        if 5 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 17:
            return 'Afternoon'
        elif 17 <= hour < 21:
            return 'Evening'
        else:
            return 'Night'
    
    def train(self, df: pd.DataFrame) -> None:
        """Train the Markov chain on transaction data"""
        print("Training Markov Chain model...")
        
        # Create states
        df_with_states = self.create_states(df)
        
        # Sort by date to maintain chronological order
        df_with_states = df_with_states.sort_values('Date')
        
        # Build transition matrices
        self._build_transition_matrix(df_with_states)
        self._build_category_transitions(df_with_states)
        self._build_amount_transitions(df_with_states)
        self._build_time_transitions(df_with_states)
        self._identify_behavioral_patterns(df_with_states)
        
        self.is_trained = True
        print(f"✅ Model trained on {len(df_with_states)} transactions")
        print(f"📊 Identified {len(self.transition_matrix)} unique state transitions")
    
    def _build_transition_matrix(self, df: pd.DataFrame) -> None:
        """Build state transition matrix"""
        states = df['State_Sequence'].tolist()
        
        for i in range(len(states) - 1):
            current_state = states[i]
            next_state = states[i + 1]
            
            self.transition_matrix[current_state][next_state] += 1
            self.state_frequencies[current_state] += 1
        
        # Normalize to probabilities
        for current_state in self.transition_matrix:
            total = sum(self.transition_matrix[current_state].values())
            for next_state in self.transition_matrix[current_state]:
                self.transition_matrix[current_state][next_state] /= total
    
    def _build_category_transitions(self, df: pd.DataFrame) -> None:
        """Build category-specific transition patterns"""
        categories = df['Category'].tolist()
        
        for i in range(len(categories) - 1):
            current_cat = categories[i]
            next_cat = categories[i + 1]
            self.category_transitions[current_cat][next_cat] += 1
        
        # Normalize
        for current_cat in self.category_transitions:
            total = sum(self.category_transitions[current_cat].values())
            if total > 0:
                for next_cat in self.category_transitions[current_cat]:
                    self.category_transitions[current_cat][next_cat] /= total
    
    def _build_amount_transitions(self, df: pd.DataFrame) -> None:
        """Build amount transition patterns"""
        for i in range(len(df) - 1):
            current_state = df.iloc[i]['Behavioral_State']
            next_amount = abs(df.iloc[i + 1]['Amount'])
            self.amount_transitions[current_state]['amounts'].append(next_amount)
    
    def _build_time_transitions(self, df: pd.DataFrame) -> None:
        """Build time-based transition patterns"""
        for i in range(len(df) - 1):
            current_state = df.iloc[i]['Behavioral_State']
            time_diff = (df.iloc[i + 1]['Date'] - df.iloc[i]['Date']).total_seconds() / 3600  # hours
            self.time_transitions[current_state]['intervals'].append(time_diff)
    
    def _identify_behavioral_patterns(self, df: pd.DataFrame) -> None:
        """Identify common behavioral patterns"""
        # Group by user behavioral patterns
        try:
            patterns = df.groupby(['Day_of_Week', 'Time_Period', 'Category']).agg({
                'Amount': ['count', 'mean', 'std'],
                'Date': ['min', 'max']
            }).round(2)
        except:
            patterns = None
        
        self.behavioral_states = {
            'daily_patterns': df.groupby('Day_of_Week')['Category'].apply(list).to_dict(),
            'time_patterns': df.groupby('Time_Period')['Category'].apply(list).to_dict(),
            'category_amounts': df.groupby('Category')['Amount'].describe().to_dict('index'),
            'spending_sequences': self._find_common_sequences(df['Category'].tolist())
        }
    
    def _find_common_sequences(self, categories: List[str], min_length: int = 3) -> Dict:
        """Find common spending sequences"""
        sequences = {}
        
        for length in range(2, min_length + 1):
            for i in range(len(categories) - length + 1):
                sequence = tuple(categories[i:i + length])
                sequences[sequence] = sequences.get(sequence, 0) + 1
        
        # Return only sequences that appear more than once
        return {seq: count for seq, count in sequences.items() if count > 1}
    
    def predict_next_transaction(self, current_state: str, n_predictions: int = 5) -> List[Dict]:
        """Predict next likely transactions"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        if current_state not in self.transition_matrix:
            return [{'state': 'Unknown', 'probability': 0.0, 'category': 'Unknown'}]
        
        # Get next state probabilities
        next_states = self.transition_matrix[current_state]
        
        # Sort by probability
        sorted_states = sorted(next_states.items(), key=lambda x: x[1], reverse=True)
        
        predictions = []
        for state, probability in sorted_states[:n_predictions]:
            # Parse state to extract category and other info
            parts = state.split('_')
            category = parts[0] if parts else 'Unknown'
            amount_bin = parts[1] if len(parts) > 1 else 'Unknown'
            time_period = parts[2] if len(parts) > 2 else 'Unknown'
            
            predictions.append({
                'state': state,
                'probability': probability,
                'category': category,
                'amount_range': amount_bin,
                'time_period': time_period,
                'confidence': self._calculate_confidence(state, probability)
            })
        
        return predictions
    
    def predict_spending_sequence(self, start_category: str, sequence_length: int = 5) -> List[Dict]:
        """Predict a sequence of spending categories"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        sequence = [start_category]
        probabilities = []
        
        current_category = start_category
        
        for _ in range(sequence_length - 1):
            if current_category in self.category_transitions:
                next_categories = self.category_transitions[current_category]
                if next_categories:
                    # Choose most likely next category
                    next_category = max(next_categories.items(), key=lambda x: x[1])
                    sequence.append(next_category[0])
                    probabilities.append(next_category[1])
                    current_category = next_category[0]
                else:
                    break
            else:
                break
        
        return [{
            'sequence': sequence,
            'probabilities': probabilities,
            'overall_probability': np.prod(probabilities) if probabilities else 0.0
        }]
    
    def predict_monthly_spending(self, category: str = None) -> Dict:
        """Predict monthly spending patterns"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        predictions = {}
        
        if category:
            # Category-specific prediction
            if category in self.behavioral_states['category_amounts']:
                stats = self.behavioral_states['category_amounts'][category]
                predictions[category] = {
                    'predicted_amount': stats['mean'],
                    'confidence_interval': [stats['mean'] - stats['std'], stats['mean'] + stats['std']],
                    'transaction_count': stats['count']
                }
        else:
            # All categories
            for cat, stats in self.behavioral_states['category_amounts'].items():
                predictions[cat] = {
                    'predicted_amount': stats['mean'],
                    'confidence_interval': [stats['mean'] - stats['std'], stats['mean'] + stats['std']],
                    'transaction_count': stats['count']
                }
        
        return predictions
    
    def detect_anomalies(self, df: pd.DataFrame, threshold: float = 0.05) -> pd.DataFrame:
        """Detect anomalous transactions based on learned patterns"""
        if not self.is_trained:
            raise ValueError("Model must be trained before detecting anomalies")
        
        df_with_states = self.create_states(df)
        anomalies = []
        
        for i in range(1, len(df_with_states)):
            current_state = df_with_states.iloc[i-1]['State_Sequence']
            next_state = df_with_states.iloc[i]['State_Sequence']
            
            # Check if this transition is unusual
            if current_state in self.transition_matrix:
                transition_prob = self.transition_matrix[current_state].get(next_state, 0.0)
                
                if transition_prob < threshold:
                    anomalies.append({
                        'index': i,
                        'date': df_with_states.iloc[i]['Date'],
                        'details': df_with_states.iloc[i]['Details'],
                        'amount': df_with_states.iloc[i]['Amount'],
                        'category': df_with_states.iloc[i]['Category'],
                        'anomaly_score': 1 - transition_prob,
                        'reason': f'Unusual transition from {current_state} to {next_state}'
                    })
        
        return pd.DataFrame(anomalies)
    
    def analyze_behavioral_patterns(self) -> Dict:
        """Analyze learned behavioral patterns"""
        if not self.is_trained:
            raise ValueError("Model must be trained before analysis")
        
        analysis = {
            'most_common_transitions': self._get_top_transitions(10),
            'spending_habits': self._analyze_spending_habits(),
            'temporal_patterns': self._analyze_temporal_patterns(),
            'category_preferences': self._analyze_category_preferences(),
            'behavioral_insights': self._generate_behavioral_insights()
        }
        
        return analysis
    
    def _get_top_transitions(self, n: int = 10) -> List[Dict]:
        """Get most common state transitions"""
        all_transitions = []
        
        for current_state, transitions in self.transition_matrix.items():
            for next_state, probability in transitions.items():
                all_transitions.append({
                    'from_state': current_state,
                    'to_state': next_state,
                    'probability': probability,
                    'frequency': self.state_frequencies[current_state] * probability
                })
        
        return sorted(all_transitions, key=lambda x: x['frequency'], reverse=True)[:n]
    
    def _analyze_spending_habits(self) -> Dict:
        """Analyze spending habits from behavioral states"""
        habits = {}
        
        # Daily spending patterns
        daily_patterns = self.behavioral_states.get('daily_patterns', {})
        habits['daily_preferences'] = {
            day: Counter(categories).most_common(3) 
            for day, categories in daily_patterns.items()
        }
        
        # Time-based patterns
        time_patterns = self.behavioral_states.get('time_patterns', {})
        habits['time_preferences'] = {
            period: Counter(categories).most_common(3)
            for period, categories in time_patterns.items()
        }
        
        return habits
    
    def _analyze_temporal_patterns(self) -> Dict:
        """Analyze temporal spending patterns"""
        patterns = {}
        
        # Average time between transactions by category
        for state, intervals in self.time_transitions.items():
            if 'intervals' in intervals and intervals['intervals']:
                patterns[state] = {
                    'avg_interval_hours': np.mean(intervals['intervals']),
                    'std_interval_hours': np.std(intervals['intervals']),
                    'min_interval_hours': np.min(intervals['intervals']),
                    'max_interval_hours': np.max(intervals['intervals'])
                }
        
        return patterns
    
    def _analyze_category_preferences(self) -> Dict:
        """Analyze category transition preferences"""
        preferences = {}
        
        for category, transitions in self.category_transitions.items():
            if transitions:
                # Most likely next categories
                sorted_transitions = sorted(transitions.items(), key=lambda x: x[1], reverse=True)
                preferences[category] = {
                    'most_likely_next': sorted_transitions[:3],
                    'transition_entropy': self._calculate_entropy(list(transitions.values()))
                }
        
        return preferences
    
    def _calculate_entropy(self, probabilities: List[float]) -> float:
        """Calculate entropy of probability distribution"""
        probabilities = [p for p in probabilities if p > 0]
        if not probabilities:
            return 0.0
        return -sum(p * np.log2(p) for p in probabilities)
    
    def _calculate_confidence(self, state: str, probability: float) -> str:
        """Calculate confidence level for prediction"""
        if probability > 0.7:
            return 'High'
        elif probability > 0.4:
            return 'Medium'
        elif probability > 0.2:
            return 'Low'
        else:
            return 'Very Low'
    
    def _generate_behavioral_insights(self) -> List[str]:
        """Generate insights about user behavior"""
        insights = []
        
        # Analyze spending sequences
        sequences = self.behavioral_states.get('spending_sequences', {})
        if sequences:
            most_common_seq = max(sequences.items(), key=lambda x: x[1])
            insights.append(f"Most common spending sequence: {' → '.join(most_common_seq[0])} (occurs {most_common_seq[1]} times)")
        
        # Analyze category preferences
        category_amounts = self.behavioral_states.get('category_amounts', {})
        if category_amounts and isinstance(category_amounts, dict):
            # Check if it's a nested dict structure
            valid_categories = {}
            for cat, data in category_amounts.items():
                if isinstance(data, dict) and 'mean' in data:
                    valid_categories[cat] = data
            
            if valid_categories:
                highest_spending = max(valid_categories.items(), key=lambda x: x[1]['mean'])
                insights.append(f"Highest average spending category: {highest_spending[0]} (KSh {highest_spending[1]['mean']:.0f})")
        
        # Analyze temporal patterns
        daily_patterns = self.behavioral_states.get('daily_patterns', {})
        if daily_patterns:
            busiest_day = max(daily_patterns.items(), key=lambda x: len(x[1]))
            insights.append(f"Most active spending day: {busiest_day[0]} ({len(busiest_day[1])} transactions)")
        
        return insights
    
    def save_model(self, filename: str) -> None:
        """Save trained model to file"""
        model_data = {
            'order': self.order,
            'transition_matrix': dict(self.transition_matrix),
            'state_frequencies': dict(self.state_frequencies),
            'category_transitions': dict(self.category_transitions),
            'behavioral_states': self.behavioral_states,
            'is_trained': self.is_trained
        }
        
        with open(filename, 'w') as f:
            json.dump(model_data, f, indent=2, default=str)
    
    def load_model(self, filename: str) -> None:
        """Load trained model from file"""
        with open(filename, 'r') as f:
            model_data = json.load(f)
        
        self.order = model_data['order']
        self.transition_matrix = defaultdict(lambda: defaultdict(float), model_data['transition_matrix'])
        self.state_frequencies = defaultdict(int, model_data['state_frequencies'])
        self.category_transitions = defaultdict(lambda: defaultdict(float), model_data['category_transitions'])
        self.behavioral_states = model_data['behavioral_states']
        self.is_trained = model_data['is_trained']
    
    def get_model_stats(self) -> Dict:
        """Get statistics about the trained model"""
        if not self.is_trained:
            return {'status': 'Not trained'}
        
        return {
            'status': 'Trained',
            'order': self.order,
            'total_states': len(self.state_frequencies),
            'total_transitions': sum(len(transitions) for transitions in self.transition_matrix.values()),
            'categories_learned': len(self.category_transitions),
            'behavioral_patterns': len(self.behavioral_states.get('spending_sequences', {}))
        }