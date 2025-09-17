# M-Pesa Statement Analyzer

## Overview

The M-Pesa Statement Analyzer is a Streamlit-based web application designed to help Kenyan M-Pesa users analyze their transaction statements and gain insights into their spending patterns. The application processes M-Pesa statements (CSV/PDF format) and automatically categorizes transactions into meaningful groups like Food, Transport, Utilities, Shopping, Health, Education, and Entertainment. It provides interactive visualizations, spending analytics, and export capabilities to help users understand where their money goes and make informed financial decisions.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **UI Components**: Built-in Streamlit widgets for file uploads, data display, and user interactions
- **State Management**: Streamlit session state for maintaining user data across interactions
- **Layout**: Wide layout configuration with expandable sidebar for enhanced user experience

### Data Processing Pipeline
- **File Processing**: Multi-format support for CSV and PDF M-Pesa statements
- **Data Cleaning**: Robust column mapping and data standardization with fallback encoding support (utf-8, latin-1, cp1252)
- **Transaction Categorization**: Rule-based classification system using keyword matching for common Kenyan merchants and services
- **Custom Mappings**: Persistent user-defined category assignments stored in JSON format

### Visualization System
- **Chart Library**: Plotly for interactive visualizations
- **Chart Types**: Pie charts for category breakdowns, bar charts for spending comparisons, trend charts for temporal analysis, and monthly comparison views
- **Interactivity**: Hover tooltips, responsive design, and color-coded visualizations

### Data Storage
- **Category Mappings**: JSON file-based storage (`category_mappings.json`) for user-defined merchant categorizations
- **Session Data**: In-memory storage using Streamlit session state for processed transaction data
- **Export Options**: CSV export for transaction data and text-based summary reports

### Business Logic Components
- **DataProcessor**: Handles file parsing, data cleaning, and standardization of M-Pesa statement formats
- **ExpenseCategorizer**: Rule-based transaction classification with extensive Kenyan merchant keyword database
- **Visualizer**: Chart generation with consistent styling and interactive features
- **Utils**: Export utilities and financial calculation helpers

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework for the user interface
- **Pandas**: Data manipulation and analysis for transaction processing
- **Plotly**: Interactive visualization library for charts and graphs

### File Processing
- **pdfplumber**: PDF parsing for M-Pesa PDF statements
- **io**: In-memory file operations for data processing

### Data Persistence
- **JSON**: Standard library for category mapping storage
- **CSV**: Standard library for data export functionality

### Utilities
- **datetime**: Date/time operations for temporal analysis
- **re**: Regular expressions for text processing and categorization
- **os**: File system operations for data management

The application follows a modular architecture with clear separation of concerns, making it maintainable and extensible. The rule-based categorization system is specifically tailored for the Kenyan market, including local merchants, mobile money operators, and service providers commonly found in M-Pesa transactions.