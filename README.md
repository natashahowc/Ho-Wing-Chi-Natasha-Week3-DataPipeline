# Data Cleaning and Validation Pipeline

## Overview
This project implements a data processing pipeline that cleans raw scraped data and validates data quality. The pipeline transforms unstructured data with HTML artifacts into clean, validated JSON output.

## Pipeline Components

### 1. Data Cleaning (`cleaner.py`)
- **Purpose**: Removes HTML artifacts, normalizes text, and filters invalid records
- **Input**: `sample_data.json` - Raw data with HTML artifacts and inconsistent formatting
- **Output**: `cleaned_output.json` - Clean, structured data
- **Cleaning Operations**:
  - **HTML Removal**: Strips HTML tags (`<div>`, `<p>`, `<span>`, `<br>`) and decodes HTML entities (`&nbsp;`, `&amp;`, `&lt;`, `&gt;`)
  - **Whitespace Normalization**: Removes extra spaces, newlines, tabs, and leading/trailing whitespace
  - **Text Encoding**: Normalizes Unicode characters to UTF-8 (NFC format)
  - **Date Standardization**: Converts various date formats to ISO format (YYYY-MM-DD)
  - **URL Validation**: Removes articles with invalid URLs (missing schemes or unwanted query parameters)
  - **Special Characters**: Normalizes smart quotes and dashes

### 2. Data Validation (`validator.py`)
- **Purpose**: Validates data quality and generates comprehensive quality reports
- **Input**: `cleaned_output.json`
- **Output**: `quality_report.txt`
- **Validation Checks**:
  - Required fields (url, title, content)
  - URL format validation (must have http:// or https://)
  - URL query parameter validation (removes unwanted tracking parameters)
  - Content length (minimum 100 characters)
  - Title length (minimum 10 characters)
  - Date format (ISO format YYYY-MM-DD or 'N/A')

## Usage

### Step 1: Clean Data
```bash
python3 cleaner.py
```
Processes `sample_data.json` and outputs `cleaned_output.json`. Invalid articles are automatically removed.

### Step 2: Validate Data
```bash
python3 validator.py
```
Validates `cleaned_output.json` and generates `quality_report.txt` with detailed statistics.

## Output Files

- **sample_data.json**: Raw input data (may contain HTML artifacts, inconsistent formatting)
- **cleaned_output.json**: Clean, structured data ready for analysis
- **quality_report.txt**: Comprehensive validation report with:
  - Total records processed
  - Valid vs. invalid counts
  - Field completeness percentages
  - Common validation failures
  - Detailed error reports for invalid records

## Results

The pipeline successfully processes input data:
- **Input**: 20 raw articles with HTML artifacts and inconsistent formatting
- **After Cleaning**: 15 valid articles (5 removed due to invalid URLs)
- **Validation**: 100% of remaining articles pass all validation checks

## Dependencies

- Standard library: `json`, `re`, `datetime`, `html`, `unicodedata`, `urllib.parse`
