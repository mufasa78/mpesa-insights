import pandas as pd
import re
from typing import Dict, List

class ExpenseCategorizer:
    def __init__(self, custom_mappings: Dict[str, str] = None):
        self.custom_mappings = custom_mappings if custom_mappings is not None else {}
        
        # Default categorization rules
        self.category_rules = {
            'Food': [
                'naivas', 'carrefour', 'quickmart', 'tuskys', 'nakumatt', 'shoprite',
                'chandarana', 'eastmatt', 'cleanshelf', 'uchumi', 'choppies',
                'kfc', 'pizza', 'burger', 'restaurant', 'cafe', 'hotel',
                'food', 'meal', 'lunch', 'dinner', 'breakfast', 'snack',
                'delivery', 'glovo', 'uber eats', 'bolt food', 'jumia food'
            ],
            'Transport': [
                'uber', 'bolt', 'taxi', 'matatu', 'bus', 'transport',
                'fuel', 'petrol', 'diesel', 'parking', 'toll',
                'train', 'sgr', 'kenya railways', 'car wash',
                'insurance', 'motor', 'vehicle', 'garage', 'mechanic'
            ],
            'Utilities': [
                'kplc', 'kenya power', 'electricity', 'power',
                'nairobi water', 'water', 'sewerage',
                'zuku', 'safaricom', 'airtel', 'telkom', 'internet',
                'dstv', 'gotv', 'showmax', 'netflix', 'startimes',
                'gas', 'cooking gas', 'mykgas'
            ],
            'Shopping': [
                'amazon', 'jumia', 'kilimall', 'masoko', 'online',
                'electronics', 'computer', 'phone', 'mobile',
                'clothes', 'fashion', 'shoes', 'accessories',
                'beauty', 'cosmetics', 'salon', 'barber',
                'books', 'stationery', 'office'
            ],
            'Health': [
                'hospital', 'clinic', 'medical', 'doctor', 'pharmacy',
                'medicine', 'drugs', 'prescription', 'health',
                'dental', 'dentist', 'eye', 'optical', 'lab',
                'nhif', 'insurance', 'medical cover'
            ],
            'Education': [
                'school', 'college', 'university', 'education',
                'fees', 'tuition', 'course', 'training',
                'books', 'learning', 'exam', 'certification'
            ],
            'Entertainment': [
                'cinema', 'movie', 'film', 'concert', 'music',
                'games', 'gaming', 'sports', 'gym', 'fitness',
                'club', 'bar', 'entertainment', 'recreation',
                'betting', 'sportpesa', 'betika', 'betin'
            ],
            'Airtime': [
                'airtime', 'bundle', 'data', 'sms', 'call',
                'safaricom airtime', 'airtel airtime', 'telkom airtime'
            ],
            'Financial': [
                'bank', 'atm', 'withdraw', 'deposit', 'transfer',
                'loan', 'credit', 'savings', 'investment',
                'equity', 'kcb', 'cooperative', 'family bank',
                'stanbic', 'standard chartered', 'barclays', 'absa'
            ]
        }
    
    def categorize_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categorize transactions based on details"""
        df = df.copy()
        df['Category'] = df['Details'].apply(self._categorize_single_transaction)
        return df
    
    def _categorize_single_transaction(self, details: str) -> str:
        """Categorize a single transaction based on its details"""
        details_lower = str(details).lower()
        
        # First check custom mappings (exact match)
        if details in self.custom_mappings:
            return self.custom_mappings[details]
        
        # Then check rule-based categorization
        for category, keywords in self.category_rules.items():
            for keyword in keywords:
                if keyword in details_lower:
                    return category
        
        # Check for specific patterns
        
        # Bank/Agent codes pattern
        if re.search(r'\b[A-Z0-9]{6,}\b', details) and any(word in details_lower for word in ['agent', 'withdraw', 'deposit']):
            return 'Financial'
        
        # Paybill patterns
        if 'paybill' in details_lower or re.search(r'pay bill.*\d+', details_lower):
            return self._categorize_paybill(details_lower)
        
        # Till number patterns
        if 'buy goods' in details_lower or re.search(r'till.*\d+', details_lower):
            return self._categorize_till(details_lower)
        
        # Phone number patterns (person-to-person transfers)
        if re.search(r'\b(254|0)\d{9}\b', details) and ('sent to' in details_lower or 'received from' in details_lower):
            return 'Transfers'
        
        return 'Other'
    
    def _categorize_paybill(self, details: str) -> str:
        """Categorize paybill transactions"""
        # Common paybill numbers and their categories
        paybill_mappings = {
            'kplc': 'Utilities',
            'zuku': 'Utilities',
            'dstv': 'Utilities',
            'water': 'Utilities',
            'nhif': 'Health',
            'school': 'Education',
            'university': 'Education',
            'betting': 'Entertainment',
            'sacco': 'Financial',
            'loan': 'Financial'
        }
        
        for keyword, category in paybill_mappings.items():
            if keyword in details:
                return category
        
        return 'Other'
    
    def _categorize_till(self, details: str) -> str:
        """Categorize till number transactions"""
        # Till numbers are typically for goods/services
        # We can make educated guesses based on common patterns
        
        if any(word in details for word in ['supermarket', 'shop', 'store', 'mart']):
            return 'Food'
        elif any(word in details for word in ['petrol', 'fuel', 'station']):
            return 'Transport'
        elif any(word in details for word in ['restaurant', 'hotel', 'cafe']):
            return 'Food'
        elif any(word in details for word in ['pharmacy', 'chemist']):
            return 'Health'
        
        return 'Shopping'  # Default for till transactions
    
    def add_custom_mapping(self, details: str, category: str) -> None:
        """Add a custom mapping for a specific transaction detail"""
        self.custom_mappings[details] = category
    
    def get_unknown_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get transactions that couldn't be categorized"""
        categorized_df = self.categorize_transactions(df)
        unknown_df = categorized_df[categorized_df['Category'] == 'Other']
        return unknown_df
    
    def get_category_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get summary statistics by category"""
        categorized_df = self.categorize_transactions(df)
        
        # Filter for expenses only (negative amounts)
        expenses_df = categorized_df[categorized_df['Amount'] < 0].copy()
        if len(expenses_df) > 0:
            expenses_df['Amount'] = expenses_df['Amount'].abs()
        
        summary = expenses_df.groupby('Category').agg({
            'Amount': ['sum', 'count', 'mean'],
            'Date': ['min', 'max']
        }).round(2)
        
        summary.columns = ['Total', 'Count', 'Average', 'First_Date', 'Last_Date']
        summary = summary.sort_values('Total', ascending=False)
        
        # Add percentage
        total_expenses = summary['Total'].sum()
        summary['Percentage'] = (summary['Total'] / total_expenses * 100).round(1)
        
        return summary
