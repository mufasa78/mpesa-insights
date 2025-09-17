import pandas as pd
import pdfplumber
import io
import re
from datetime import datetime
import streamlit as st

class DataProcessor:
    def __init__(self):
        self.column_mappings = {
            'completion time': 'Date',
            'details': 'Details',
            'paid in': 'Amount',
            'withdrawn': 'Amount',
            'balance': 'Balance',
            'receipt no.': 'Receipt',
            'transaction cost': 'Cost'
        }
    
    def process_csv(self, uploaded_file):
        """Process CSV M-Pesa statement"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError("Could not read CSV file with any supported encoding")
            
            # Clean and standardize column names
            df.columns = df.columns.str.lower().str.strip()
            
            # Map columns to standard format
            for old_col, new_col in self.column_mappings.items():
                if old_col in df.columns:
                    df = df.rename(columns={old_col: new_col})
            
            # Clean and process the data
            df = self._clean_data(df)
            
            return df
            
        except Exception as e:
            st.error(f"Error processing CSV: {str(e)}")
            return None
    
    def process_pdf(self, uploaded_file):
        """Process PDF M-Pesa statement"""
        try:
            # Read PDF content
            pdf_content = uploaded_file.read()
            
            transactions = []
            
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                for page in pdf.pages:
                    # Extract text from page
                    text = page.extract_text()
                    
                    if text:
                        # Parse transactions from text
                        page_transactions = self._parse_pdf_text(text)
                        transactions.extend(page_transactions)
            
            if not transactions:
                raise ValueError("No transactions found in PDF")
            
            # Create DataFrame
            df = pd.DataFrame(transactions)
            
            # Clean and process the data
            df = self._clean_data(df)
            
            return df
            
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return None
    
    def _parse_pdf_text(self, text):
        """Parse transaction data from PDF text"""
        transactions = []
        lines = text.split('\n')
        
        # Common M-Pesa PDF patterns
        transaction_pattern = r'(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})\s+([A-Z0-9]+)\s+(.*?)\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to match transaction pattern
            match = re.match(transaction_pattern, line)
            if match:
                date_str, time_str, receipt, details, amount_str, balance_str = match.groups()
                
                try:
                    # Parse date
                    date = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
                    
                    # Parse amounts
                    amount = float(amount_str.replace(',', ''))
                    balance = float(balance_str.replace(',', ''))
                    
                    # Determine transaction type from details
                    transaction_type = self._determine_transaction_type(details)
                    
                    # Adjust amount sign based on transaction type
                    if transaction_type in ['Send Money', 'Buy Goods', 'Pay Bill', 'Withdraw', 'Airtime']:
                        amount = -amount
                    
                    transactions.append({
                        'Date': date,
                        'Details': details.strip(),
                        'Amount': amount,
                        'Balance': balance,
                        'Receipt': receipt,
                        'Type': transaction_type
                    })
                    
                except (ValueError, TypeError):
                    continue
        
        return transactions
    
    def _determine_transaction_type(self, details):
        """Determine transaction type from details"""
        details_lower = details.lower()
        
        if 'sent to' in details_lower or 'send money' in details_lower:
            return 'Send Money'
        elif 'received from' in details_lower or 'receive money' in details_lower:
            return 'Receive Money'
        elif 'buy goods' in details_lower or 'bought from' in details_lower:
            return 'Buy Goods'
        elif 'pay bill' in details_lower or 'paid to' in details_lower:
            return 'Pay Bill'
        elif 'withdraw' in details_lower or 'agent' in details_lower:
            return 'Withdraw'
        elif 'airtime' in details_lower or 'bundle' in details_lower:
            return 'Airtime'
        elif 'deposit' in details_lower or 'cash in' in details_lower:
            return 'Deposit'
        else:
            return 'Other'
    
    def _clean_data(self, df):
        """Clean and standardize the data"""
        if df is None or df.empty:
            return df
        
        # Ensure required columns exist
        required_columns = ['Date', 'Details', 'Amount']
        for col in required_columns:
            if col not in df.columns:
                st.warning(f"Missing required column: {col}")
                return pd.DataFrame()
        
        # Clean Date column
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=True)
            df = df.dropna(subset=['Date'])
        
        # Clean Amount column
        if 'Amount' in df.columns:
            # Handle both 'Paid In' and 'Withdrawn' columns if they exist separately
            if 'paid in' in df.columns and 'withdrawn' in df.columns:
                df['Amount'] = pd.to_numeric(df['paid in'].fillna(0), errors='coerce') - pd.to_numeric(df['withdrawn'].fillna(0), errors='coerce')
            else:
                # Convert amount to numeric
                df['Amount'] = df['Amount'].astype(str)
                df['Amount'] = df['Amount'].str.replace('[KSh,\s]', '', regex=True)
                df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        
        # Clean Details column
        if 'Details' in df.columns:
            df['Details'] = df['Details'].astype(str).str.strip()
            df = df[df['Details'] != 'nan']
            df = df[df['Details'] != '']
        
        # Add transaction type if not present
        if 'Type' not in df.columns:
            df['Type'] = df['Details'].apply(self._determine_transaction_type)
        
        # Remove rows with missing critical data
        df = df.dropna(subset=['Date', 'Details', 'Amount'])
        
        # Sort by date
        df = df.sort_values('Date').reset_index(drop=True)
        
        return df
