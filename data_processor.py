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
        """Parse transaction data from PDF table format based on actual M-Pesa structure"""
        transactions = []
        
        if not table or len(table) < 2:
            return transactions
            
        # Look for the detailed statement table (skip summary tables)
        headers = None
        data_rows = table
        
        # Check if this is the detailed transaction table
        for i, row in enumerate(table[:3]):
            if row and len(row) >= 6:  # M-Pesa detailed table has 7 columns
                row_str = ' '.join([str(cell) for cell in row if cell]).lower()
                if 'receipt' in row_str and 'completion' in row_str and 'details' in row_str:
                    headers = [str(cell).lower().strip() if cell else '' for cell in row]
                    data_rows = table[i+1:]
                    break
        
        if not headers:
            # Skip this table if it's not the detailed transaction table
            return transactions
        
        # Process data rows
        for row in data_rows:
            if not row or len(row) < 6:  # M-Pesa table needs at least 6 columns
                continue
                
            try:
                # M-Pesa PDF structure: Receipt No, Completion Time, Details, Transaction Status, Paid in, Withdrawn, Balance
                receipt = str(row[0]) if row[0] else ''
                completion_time = str(row[1]) if row[1] else ''
                details = str(row[2]) if row[2] else ''
                status = str(row[3]) if row[3] else ''
                paid_in = str(row[4]) if row[4] else '0.00'
                withdrawn = str(row[5]) if row[5] else '0.00'
                balance = str(row[6]) if len(row) > 6 and row[6] else '0.00'
                
                # Skip if essential data is missing or status is not COMPLETED
                if not completion_time or not details or status.upper() != 'COMPLETED':
                    continue
                
                # Parse completion time - format: "2025-07-01 19:47:53"
                try:
                    date = datetime.strptime(completion_time, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        # Try alternative format
                        date = datetime.strptime(completion_time.split()[0], "%Y-%m-%d")
                    except ValueError:
                        continue
                
                # Parse amounts
                paid_in_amount = self._parse_amount_with_sign(paid_in)
                withdrawn_amount = self._parse_amount_with_sign(withdrawn)
                balance_amount = self._parse_amount_with_sign(balance)
                
                # Calculate net amount (positive for money in, negative for money out)
                if paid_in_amount > 0:
                    amount = paid_in_amount
                elif withdrawn_amount > 0:
                    amount = -withdrawn_amount
                else:
                    continue  # Skip if no amount
                
                # Clean details - remove newlines and extra spaces
                details_clean = ' '.join(details.split())
                
                # Determine transaction type
                transaction_type = self._determine_transaction_type(details_clean)
                
                transactions.append({
                    'Date': date,
                    'Details': details_clean,
                    'Amount': amount,
                    'Balance': balance_amount,
                    'Receipt': receipt,
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
        """Determine transaction type from details based on actual M-Pesa patterns"""
        details_lower = details.lower()
        
        # Merchant payments
        if 'merchant payment' in details_lower:
            return 'Merchant Payment'
        # Customer transfers
        elif 'customer transfer' in details_lower or 'customer payment' in details_lower:
            return 'Send Money'
        # Pay Bill transactions
        elif 'pay bill' in details_lower:
            return 'Pay Bill'
        # Business payments (money received)
        elif 'business payment' in details_lower:
            return 'Receive Money'
        # Overdraft and loan repayments
        elif 'od loan repayment' in details_lower or 'overdraft' in details_lower:
            return 'Loan Repayment'
        elif 'overdraft of credit' in details_lower:
            return 'Overdraft'
        # Fuliza transactions
        elif 'fuliza' in details_lower:
            return 'Fuliza'
        # Airtime and bundles
        elif 'airtime' in details_lower or 'bundle' in details_lower or 'postpaid' in details_lower:
            return 'Airtime/Bundles'
        # Cash transactions
        elif 'cash in' in details_lower or 'deposit' in details_lower:
            return 'Cash In'
        elif 'cash out' in details_lower or 'withdraw' in details_lower:
            return 'Cash Out'
        # Charges and fees
        elif 'charge' in details_lower or 'fee' in details_lower:
            return 'Charges'
        # Send money (traditional)
        elif 'sent to' in details_lower or 'send money' in details_lower:
            return 'Send Money'
        # Receive money (traditional)
        elif 'received from' in details_lower or 'receive money' in details_lower:
            return 'Receive Money'
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
