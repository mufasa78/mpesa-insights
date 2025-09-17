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
                        # Also try to extract tables if available
                        tables = page.extract_tables()
                        if tables:
                            for table in tables:
                                table_transactions = self._parse_pdf_table(table)
                                transactions.extend(table_transactions)
                        
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
        
        # Enhanced M-Pesa PDF patterns - flexible patterns to handle real M-Pesa formats
        patterns = [
            # Full format: Date Time Receipt Details Amount Balance
            r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}(?:\s*[AP]M)?)\s+([A-Z0-9\-\s]{0,20}?)\s+(.*?)\s+(?:KSh\s*|KES\s*|CR\s*|DR\s*)?([\-\(]?[\d,]+\.\d{2}[\)]?)(?:\s*CR|\s*DR)?(?:\s+(?:KSh\s*|KES\s*)?([\-\(]?[\d,]+\.\d{2}[\)]?))?',
            # Date Receipt Details Amount (optional balance)
            r'(\d{1,2}/\d{1,2}/\d{4})\s+([A-Z0-9\-\s]{0,20}?)\s+(.*?)\s+(?:KSh\s*|KES\s*|CR\s*|DR\s*)?([\-\(]?[\d,]+\.\d{2}[\)]?)(?:\s*CR|\s*DR)?(?:\s+(?:KSh\s*|KES\s*)?([\-\(]?[\d,]+\.\d{2}[\)]?))?',
            # Minimal: Date Details Amount (no receipt, no balance)
            r'(\d{1,2}/\d{1,2}/\d{4})\s+(.*?)\s+(?:KSh\s*|KES\s*|CR\s*|DR\s*)?([\-\(]?[\d,]+\.\d{2}[\)]?)(?:\s*CR|\s*DR)?',
            # Fallback: Any date and reasonable amount
            r'(\d{1,2}/\d{1,2}/\d{4}).*?(.*?)(?:KSh|KES)?\s*([\-\(]?\d[\d,]*\.\d{2}[\)]?)',
        ]
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:  # Skip very short lines
                continue
            
            # Try multiple patterns
            for i, pattern in enumerate(patterns):
                match = re.search(pattern, line)
                if match:
                    groups = match.groups()
                    
                    try:
                        # Initialize default values
                        date_str = groups[0]
                        time_str = None
                        receipt = ''
                        details = ''
                        amount_str = ''
                        balance_str = None
                        
                        # Handle different group patterns
                        if len(groups) == 6:  # Full format: Date Time Receipt Details Amount Balance
                            date_str, time_str, receipt, details, amount_str, balance_str = groups
                        elif len(groups) == 5:  # Date Receipt/Time Details Amount Balance
                            if i == 0:  # First pattern with time
                                date_str, time_str, receipt, details, amount_str = groups
                            else:  # Other patterns without time
                                date_str, receipt, details, amount_str, balance_str = groups
                        elif len(groups) == 4:  # Date Receipt Details Amount OR Date Time Details Amount
                            if ':' in groups[1]:  # Has time
                                date_str, time_str, details, amount_str = groups
                            else:  # Has receipt
                                date_str, receipt, details, amount_str = groups
                        elif len(groups) == 3:  # Minimal: Date Details Amount
                            date_str, details, amount_str = groups
                        else:
                            continue
                        
                        # Parse date with optional time
                        if time_str:
                            time_str = time_str.replace(' ', '').upper()
                            if 'AM' in time_str or 'PM' in time_str:
                                try:
                                    date = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %I:%M%p")
                                except ValueError:
                                    date = datetime.strptime(f"{date_str} {time_str.replace('AM', '').replace('PM', '')}", "%d/%m/%Y %H:%M")
                            else:
                                date = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
                        else:
                            date = datetime.strptime(date_str, "%d/%m/%Y")
                        
                        # Parse amounts using helper method
                        amount = self._parse_amount_with_sign(amount_str)
                        balance = self._parse_amount_with_sign(balance_str) if balance_str else 0.0
                        
                        # Skip if essential data is missing
                        if not details.strip() or amount == 0.0:
                            continue
                        
                        # Determine transaction type from details
                        transaction_type = self._determine_transaction_type(details)
                        
                        # Only apply sign inference if no explicit sign markers were found
                        if not any(marker in str(amount_str).upper() for marker in ['CR', 'DR', '(', ')', '-']):
                            if transaction_type in ['Send Money', 'Buy Goods', 'Pay Bill', 'Withdraw', 'Airtime']:
                                amount = -abs(amount)  # Ensure negative for expenses
                        
                        transactions.append({
                            'Date': date,
                            'Details': details.strip(),
                            'Amount': amount,
                            'Balance': balance,
                            'Receipt': receipt,
                            'Type': transaction_type
                        })
                        break  # Found a match, move to next line
                        
                    except (ValueError, TypeError) as e:
                        continue
        
        return transactions
    
    def _parse_pdf_table(self, table):
        """Parse transaction data from PDF table format"""
        transactions = []
        
        if not table or len(table) < 2:
            return transactions
            
        # Try to identify column headers
        headers = None
        data_rows = table
        
        # Look for header row containing common M-Pesa column names
        for i, row in enumerate(table[:3]):  # Check first 3 rows for headers
            if row and any(col and isinstance(col, str) and 
                          any(keyword in col.lower() for keyword in ['date', 'time', 'receipt', 'details', 'amount', 'balance'])
                          for col in row if col):
                headers = [col.lower().strip() if col else '' for col in row]
                data_rows = table[i+1:]
                break
        
        if not headers:
            # Default column mapping for M-Pesa statements
            headers = ['date', 'time', 'receipt', 'details', 'amount', 'balance']
        
        # Process data rows
        for row in data_rows:
            if not row or len(row) < 4:  # Need at least date, details, amount, balance
                continue
                
            try:
                # Map columns based on position or header names
                date_col = next((i for i, h in enumerate(headers) if 'date' in h), 0)
                time_col = next((i for i, h in enumerate(headers) if 'time' in h), 1)
                receipt_col = next((i for i, h in enumerate(headers) if 'receipt' in h), 2)
                details_col = next((i for i, h in enumerate(headers) if 'detail' in h), 3)
                amount_col = next((i for i, h in enumerate(headers) if 'amount' in h), 4)
                balance_col = next((i for i, h in enumerate(headers) if 'balance' in h), 5)
                
                # Extract values
                date_str = row[date_col] if len(row) > date_col and row[date_col] else ''
                time_str = row[time_col] if len(row) > time_col and row[time_col] else '12:00'
                receipt = row[receipt_col] if len(row) > receipt_col and row[receipt_col] else ''
                details = row[details_col] if len(row) > details_col and row[details_col] else ''
                amount_str = row[amount_col] if len(row) > amount_col and row[amount_col] else '0'
                balance_str = row[balance_col] if len(row) > balance_col and row[balance_col] else '0'
                
                # Skip if essential data is missing
                if not date_str or not details or not amount_str:
                    continue
                
                # Parse date with flexible time handling
                try:
                    if isinstance(date_str, str) and '/' in date_str:
                        if time_str and ':' in str(time_str):
                            time_clean = str(time_str).replace(' ', '').upper()
                            if 'AM' in time_clean or 'PM' in time_clean:
                                try:
                                    date = datetime.strptime(f"{date_str} {time_clean}", "%d/%m/%Y %I:%M%p")
                                except ValueError:
                                    # Try without AM/PM
                                    time_only = time_clean.replace('AM', '').replace('PM', '')
                                    date = datetime.strptime(f"{date_str} {time_only}", "%d/%m/%Y %H:%M")
                            else:
                                date = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
                        else:
                            date = datetime.strptime(date_str, "%d/%m/%Y")
                    else:
                        continue
                except ValueError:
                    continue
                
                # Parse amounts using helper method  
                amount = self._parse_amount_with_sign(amount_str)
                balance = self._parse_amount_with_sign(balance_str) if balance_str else 0.0
                
                # Skip if essential data is missing
                if not details.strip() or amount == 0.0:
                    continue
                
                # Determine transaction type
                transaction_type = self._determine_transaction_type(str(details))
                
                # Only apply sign inference if no explicit sign markers were found
                original_amount_str = str(amount_str) + str(balance_str or '')
                if not any(marker in original_amount_str.upper() for marker in ['CR', 'DR', '(', ')', '-']):
                    if transaction_type in ['Send Money', 'Buy Goods', 'Pay Bill', 'Withdraw', 'Airtime']:
                        amount = -abs(amount)  # Ensure negative for expenses
                
                transactions.append({
                    'Date': date,
                    'Details': str(details).strip(),
                    'Amount': amount,
                    'Balance': balance,
                    'Receipt': str(receipt),
                    'Type': transaction_type
                })
                
            except (ValueError, TypeError, IndexError):
                continue
                
        return transactions
    
    def _parse_amount_with_sign(self, amount_str):
        """Parse amount string with proper sign detection"""
        if not amount_str:
            return 0.0
        
        amount_str = str(amount_str).strip()
        is_negative = False
        
        # Check for various negative indicators
        if amount_str.startswith('(') and amount_str.endswith(')'):
            is_negative = True
            amount_str = amount_str[1:-1]
        elif amount_str.startswith('-'):
            is_negative = True
            amount_str = amount_str[1:]
        elif 'DR' in amount_str.upper():
            is_negative = True
        elif 'CR' in amount_str.upper():
            is_negative = False
        
        # Clean amount string
        clean_amount = amount_str.replace(',', '').replace('KSh', '').replace('KES', '').replace('DR', '').replace('CR', '').strip()
        
        try:
            amount = float(clean_amount)
            return -amount if is_negative else amount
        except ValueError:
            return 0.0
    
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
                paid_in = pd.to_numeric(df['paid in'].fillna(0), errors='coerce')
                withdrawn = pd.to_numeric(df['withdrawn'].fillna(0), errors='coerce')
                df['Amount'] = paid_in - withdrawn
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
