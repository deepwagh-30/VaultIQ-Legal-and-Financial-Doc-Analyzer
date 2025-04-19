# analysis/financial_analyzer.py

import re
import pandas as pd
import numpy as np
import streamlit as st
from collections import defaultdict

# Financial keywords and patterns with improved regex
FINANCIAL_KEYWORDS = {
    "Revenue": r"(?:Annual|Total|Net)?\s*Revenue\s*(?:of|:)?\s*[\$]?([0-9,\.]+)\s*(?:million|billion|M|B)?",
    "Net Income": r"(?:Net Income|Net Profit|Net Earnings)\s*(?:of|:)?\s*[\$]?([0-9,\.]+)\s*(?:million|billion|M|B)?",
    "Total Assets": r"Total Assets\s*(?:of|:)?\s*[\$]?([0-9,\.]+)\s*(?:million|billion|M|B)?",
    "Total Liabilities": r"Total Liabilities\s*(?:of|:)?\s*[\$]?([0-9,\.]+)\s*(?:million|billion|M|B)?",
    "EBITDA": r"EBITDA\s*(?:of|:)?\s*[\$]?([0-9,\.]+)\s*(?:million|billion|M|B)?",
    "EPS": r"(?:Earnings Per Share|EPS)\s*(?:of|:)?\s*[\$]?([0-9,\.]+)",
    "Gross Profit": r"Gross Profit\s*(?:of|:)?\s*[\$]?([0-9,\.]+)\s*(?:million|billion|M|B)?",
    "Operating Income": r"Operating Income\s*(?:of|:)?\s*[\$]?([0-9,\.]+)\s*(?:million|billion|M|B)?"
}

# Periods for financial reporting
FINANCIAL_PERIODS = [
    r"FY\s?(\d{4})",  # Fiscal year
    r"Q(\d)\s?(\d{4})",  # Quarter
    r"(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)[a-z]*\s+(\d{4})"  # Month-Year
]

# Financial ratios and formulas
FINANCIAL_RATIOS = {
    "Debt-to-Asset": {"formula": lambda l, a: l / a, "inputs": ["Total Liabilities", "Total Assets"]},
    "Current Ratio": {"formula": lambda ca, cl: ca / cl, "inputs": ["Current Assets", "Current Liabilities"]},
    "Profit Margin": {"formula": lambda ni, r: ni / r, "inputs": ["Net Income", "Revenue"]},
    "ROA": {"formula": lambda ni, ta: ni / ta, "inputs": ["Net Income", "Total Assets"]}
}

@st.cache_data
def analyze_financials(text, tables=None):
    """
    Comprehensive financial analysis of document text and tables
    
    Args:
        text: The extracted text from the document
        tables: List of pandas DataFrames containing extracted tables
        
    Returns:
        dict: Financial analysis results
    """
    # Extract primary financial metrics from text
    metrics = extract_financial_metrics(text)
    
    # If tables are available, enhance extraction from tables
    if tables and len(tables) > 0:
        table_metrics = extract_metrics_from_tables(tables)
        # Merge table metrics with text metrics (table data takes precedence)
        metrics.update(table_metrics)
    
    # Calculate financial ratios where possible
    ratios = calculate_financial_ratios(metrics)
    metrics.update(ratios)
    
    # Extract trends if any
    trends = extract_financial_trends(text, tables)
    
    # Return comprehensive results
    return {
        "metrics": metrics,
        "trends": trends
    }

def extract_financial_metrics(text):
    """Extract financial metrics using regex patterns"""
    results = {}
    
    # Apply each regex pattern to extract metrics
    for key, pattern in FINANCIAL_KEYWORDS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Use the first match as the primary metric
            value = matches[0]
            # Clean and format the value
            value = value.replace(',', '')
            
            # Handle currency formatting
            try:
                float_value = float(value)
                # Format as currency with commas
                results[key] = f"${float_value:,.2f}"
            except ValueError:
                # If conversion fails, use as is
                results[key] = value
    
    # Look for additional metrics not covered by standard patterns
    # Current assets and liabilities (needed for current ratio)
    current_assets_match = re.search(r"Current Assets\s*(?:of|:)?\s*[\$]?([0-9,\.]+)", text, re.IGNORECASE)
    if current_assets_match:
        results["Current Assets"] = clean_financial_value(current_assets_match.group(1))
    
    current_liabilities_match = re.search(r"Current Liabilities\s*(?:of|:)?\s*[\$]?([0-9,\.]+)", text, re.IGNORECASE)
    if current_liabilities_match:
        results["Current Liabilities"] = clean_financial_value(current_liabilities_match.group(1))
    
    return results

def extract_metrics_from_tables(tables):
    """Extract financial metrics from tables"""
    results = {}
    
    # Iterate through each table
    for table in tables:
        # Check if this looks like a financial table
        if is_financial_table(table):
            # Search for metric rows in the table
            for index, row in table.iterrows():
                # Convert row to string and join for easier searching
                row_text = ' '.join(str(cell) for cell in row)
                
                # Check each financial keyword
                for key, pattern in FINANCIAL_KEYWORDS.items():
                    if re.search(key, row_text, re.IGNORECASE):
                        # Find the value column (usually the last or second-to-last column)
                        for i in range(len(row) - 1, 0, -1):
                            cell_value = str(row[i])
                            # Check if the cell contains a number that might be a financial value
                            if re.search(r'\d', cell_value):
                                results[key] = clean_financial_value(cell_value)
                                break
    
    return results

def is_financial_table(table):
    """Check if a table appears to be financial in nature"""
    # Convert table to string for pattern matching
    table_str = table.to_string()
    
    # Financial tables typically contain certain keywords
    financial_indicators = [
        'revenue', 'income', 'profit', 'loss', 'assets', 'liabilities',
        'equity', 'cash', 'balance', 'statement', 'financial', 'earnings'
    ]
    
    # Check for presence of financial indicators
    for indicator in financial_indicators:
        if re.search(indicator, table_str, re.IGNORECASE):
            return True
    
    # Check if the table has numbers in most cells (financial tables usually do)
    num_cells = 0
    num_cells_with_numbers = 0
    
    for _, row in table.iterrows():
        for cell in row:
            num_cells += 1
            if re.search(r'\d', str(cell)):
                num_cells_with_numbers += 1
    
    # If more than 40% of cells have numbers, likely a financial table
    return (num_cells_with_numbers / num_cells) > 0.4 if num_cells > 0 else False

def clean_financial_value(value_str):
    """Clean and format a financial value string"""
    # Remove non-numeric characters except decimal points
    value_str = re.sub(r'[^\d\.]', '', str(value_str))
    
    try:
        value = float(value_str)
        return f"${value:,.2f}"
    except ValueError:
        return value_str

def calculate_financial_ratios(metrics):
    """Calculate financial ratios based on available metrics"""
    results = {}
    
    for ratio_name, ratio_info in FINANCIAL_RATIOS.items():
        # Check if all required inputs are available
        inputs_available = True
        input_values = []
        
        for input_name in ratio_info["inputs"]:
            if input_name in metrics:
                # Extract numeric value from formatted string
                value_str = metrics[input_name].replace('$', '').replace(',', '')
                try:
                    input_values.append(float(value_str))
                except ValueError:
                    inputs_available = False
                    break
            else:
                inputs_available = False
                break
        
        # Calculate ratio if all inputs are available
        if inputs_available:
            try:
                ratio_value = ratio_info["formula"](*input_values)
                # Format the ratio appropriately
                if ratio_name in ["Debt-to-Asset", "Current Ratio"]:
                    # Format as decimal with 2 places
                    results[ratio_name] = f"{ratio_value:.2f}"
                elif ratio_name in ["Profit Margin", "ROA"]:
                    # Format as percentage
                    results[ratio_name] = f"{ratio_value * 100:.2f}%"
                else:
                    results[ratio_name] = f"{ratio_value:.2f}"
            except ZeroDivisionError:
                # Handle division by zero
                pass
    
    return results

def extract_financial_trends(text, tables=None):
    """Extract financial trends over multiple periods"""
    trends = defaultdict(dict)
    
    # Extract period information from text
    periods = []
    for period_pattern in FINANCIAL_PERIODS:
        period_matches = re.findall(period_pattern, text)
        if period_matches:
            periods.extend([match if isinstance(match, str) else ''.join(match) for match in period_matches])
    
    # For each metric and period, try to find values
    for key, pattern in FINANCIAL_KEYWORDS.items():
        for period in periods:
            # Modify pattern to include period
            period_pattern = f"{period}.*?{pattern}"
            match = re.search(period_pattern, text, re.IGNORECASE)
            if match:
                value = clean_financial_value(match.group(1))
                trends[key][period] = value
    
    # Extract trends from tables if available
    if tables and len(tables) > 0:
        table_trends = extract_trends_from_tables(tables, periods)
        # Merge table trends with text trends
        for metric, period_values in table_trends.items():
            for period, value in period_values.items():
                trends[metric][period] = value
    
    return dict(trends)

def extract_trends_from_tables(tables, periods):
    """Extract trend data from tables"""
    trends = defaultdict(dict)
    
    for table in tables:
        # Check column headers for period information
        headers = table.iloc[0]
        period_cols = []
        
        for i, header in enumerate(headers):
            header_str = str(header).strip()
            # Check if header matches any period
            for period in periods:
                if period in header_str:
                    period_cols.append((i, period))
        
        # If period columns are found
        if period_cols:
            # Find rows with financial metrics
            for index, row in table.iterrows():
                row_label = str(row[0]).strip()
                
                # Check if row contains a financial metric
                for metric in FINANCIAL_KEYWORDS.keys():
                    if re.search(metric, row_label, re.IGNORECASE):
                        # Extract values for each period
                        for col_idx, period in period_cols:
                            if col_idx < len(row):
                                value = str(row[col_idx]).strip()
                                if re.search(r'\d', value):  # Contains digits
                                    trends[metric][period] = clean_financial_value(value)
    
    return trends