import json
import re
from urllib.parse import urlparse
from datetime import datetime

def is_valid_url(url):
    """Validate URL format"""
    if not url or url == 'N/A' or not isinstance(url, str):
        return False
    
    try:
        result = urlparse(url)
        # Check if URL has both scheme and netloc
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def validate_required_fields(article, index):
    """Check for required fields: title, content, url"""
    errors = []
    
    # Check URL
    if 'url' not in article or not article['url'] or article['url'] == 'N/A':
        errors.append(f"Record {index}: Missing or empty 'url' field")
    
    # Check title
    if 'title' not in article or not article['title'] or article['title'] == 'N/A':
        errors.append(f"Record {index}: Missing or empty 'title' field")
    
    # Check content
    if 'content' not in article or not article['content'] or article['content'] == 'N/A':
        errors.append(f"Record {index}: Missing or empty 'content' field")
    
    return errors

def validate_url_format(article, index):
    """Validate URL format"""
    errors = []
    
    if 'url' in article and article['url'] and article['url'] != 'N/A':
        if not is_valid_url(article['url']):
            errors.append(f"Record {index}: Invalid URL format: '{article['url']}'")
    
    return errors

def validate_url_query_parameters(article, index):
    """Check for unwanted query parameters in URLs"""
    errors = []
    
    if 'url' in article and article['url'] and article['url'] != 'N/A':
        url = article['url']
        # Check for unwanted query parameters
        unwanted_params = ['utm_source', 'utm_medium', 'utm_campaign', 'ref=broken', 'id=']
        if '?' in url:
            query_string = url.split('?')[1]
            # Check if query string contains unwanted parameters
            has_unwanted = any(param in query_string for param in unwanted_params)
            if has_unwanted:
                errors.append(f"Record {index}: URL contains unwanted query parameters: '{url}'")
    
    return errors

def validate_content_length(article, index, min_length=100):
    """Check content length minimums"""
    errors = []
    
    if 'content' in article and article['content'] and article['content'] != 'N/A':
        content_length = len(article['content'].strip())
        if content_length < min_length:
            errors.append(f"Record {index}: Content too short ({content_length} characters, minimum: {min_length})")
    
    return errors

def validate_title_length(article, index, min_length=10):
    """Check title length minimums"""
    errors = []
    
    if 'title' in article and article['title'] and article['title'] != 'N/A':
        title_length = len(article['title'].strip())
        if title_length < min_length:
            errors.append(f"Record {index}: Title too short ({title_length} characters, minimum: {min_length})")
    
    return errors

def validate_date_format(article, index):
    """Validate date format (should be ISO format YYYY-MM-DD or None)"""
    errors = []
    
    if 'date' in article:
        date_value = article['date']
        if date_value and date_value != 'N/A':
            # Check if it's a valid ISO date format
            try:
                datetime.strptime(date_value, '%Y-%m-%d')
            except (ValueError, TypeError):
                errors.append(f"Record {index}: Invalid date format: '{date_value}' (expected YYYY-MM-DD or N/A)")
    
    return errors

def validate_article(article, index, min_content_length=100, min_title_length=10):
    """Validate a single article and return all errors"""
    all_errors = []
    
    # Check required fields
    all_errors.extend(validate_required_fields(article, index))
    
    # Validate URL format (only if URL exists)
    all_errors.extend(validate_url_format(article, index))
    
    # Check for unwanted query parameters
    all_errors.extend(validate_url_query_parameters(article, index))
    
    # Check content length
    all_errors.extend(validate_content_length(article, index, min_content_length))
    
    # Check title length
    all_errors.extend(validate_title_length(article, index, min_title_length))
    
    # Validate date format
    all_errors.extend(validate_date_format(article, index))
    
    return all_errors

def generate_quality_report(input_file, output_file, min_content_length=100, min_title_length=10):
    """Generate a quality report for the cleaned data"""
    try:
        # Read input JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("ERROR: Input file does not contain a valid JSON array\n")
            return
        
        total_records = len(data)
        invalid_records = []
        all_errors = []
        
        # Track field completeness
        field_counts = {
            'url': 0,
            'title': 0,
            'content': 0,
            'date': 0,
            'author': 0
        }
        
        # Track common validation failures
        failure_types = {
            'Missing or empty url': 0,
            'Missing or empty title': 0,
            'Missing or empty content': 0,
            'Invalid URL format': 0,
            'Unwanted query parameters': 0,
            'Content too short': 0,
            'Title too short': 0,
            'Invalid date format': 0
        }
        
        statistics = {
            'total_records': total_records,
            'valid_records': 0,
            'invalid_records': 0,
            'records_with_missing_fields': 0,
            'records_with_invalid_urls': 0,
            'records_with_unwanted_query_params': 0,
            'records_with_short_content': 0,
            'records_with_short_titles': 0,
            'records_with_invalid_dates': 0
        }
        
        # Validate each article
        for index, article in enumerate(data, 1):
            # Track field completeness
            if article.get('url') and article.get('url') != 'N/A':
                field_counts['url'] += 1
            if article.get('title') and article.get('title') != 'N/A':
                field_counts['title'] += 1
            if article.get('content') and article.get('content') != 'N/A':
                field_counts['content'] += 1
            if article.get('date') and article.get('date') != 'N/A':
                field_counts['date'] += 1
            if article.get('author') and article.get('author') != 'N/A':
                field_counts['author'] += 1
            errors = validate_article(article, index, min_content_length, min_title_length)
            
            if errors:
                invalid_records.append({
                    'index': index,
                    'url': article.get('url', 'N/A'),
                    'title': article.get('title', 'N/A')[:100] + '...' if len(article.get('title', '')) > 100 else article.get('title', 'N/A'),
                    'errors': errors
                })
                all_errors.extend(errors)
                statistics['invalid_records'] += 1
                
                # Count error types
                for error in errors:
                    if 'Missing or empty' in error:
                        statistics['records_with_missing_fields'] += 1
                        if "'url'" in error:
                            failure_types['Missing or empty url'] += 1
                        elif "'title'" in error:
                            failure_types['Missing or empty title'] += 1
                        elif "'content'" in error:
                            failure_types['Missing or empty content'] += 1
                    elif 'Invalid URL format' in error:
                        statistics['records_with_invalid_urls'] += 1
                        failure_types['Invalid URL format'] += 1
                    elif 'unwanted query parameters' in error:
                        statistics['records_with_unwanted_query_params'] += 1
                        failure_types['Unwanted query parameters'] += 1
                    elif 'Content too short' in error:
                        statistics['records_with_short_content'] += 1
                        failure_types['Content too short'] += 1
                    elif 'Title too short' in error:
                        statistics['records_with_short_titles'] += 1
                        failure_types['Title too short'] += 1
                    elif 'Invalid date format' in error:
                        statistics['records_with_invalid_dates'] += 1
                        failure_types['Invalid date format'] += 1
            else:
                statistics['valid_records'] += 1
        
        # Generate report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("DATA QUALITY VALIDATION REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            # Summary statistics
            f.write("SUMMARY STATISTICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Records Processed: {statistics['total_records']}\n")
            f.write(f"Valid Records: {statistics['valid_records']} ({statistics['valid_records']/total_records*100:.1f}%)\n")
            f.write(f"Invalid Records: {statistics['invalid_records']} ({statistics['invalid_records']/total_records*100:.1f}%)\n")
            f.write(f"\n")
            
            # Field Completeness
            f.write("FIELD COMPLETENESS\n")
            f.write("-" * 80 + "\n")
            for field, count in field_counts.items():
                percentage = (count / total_records * 100) if total_records > 0 else 0
                f.write(f"{field.capitalize()}: {count}/{total_records} ({percentage:.1f}%)\n")
            f.write(f"\n")
            
            # Common Validation Failures
            f.write("COMMON VALIDATION FAILURES\n")
            f.write("-" * 80 + "\n")
            sorted_failures = sorted(failure_types.items(), key=lambda x: x[1], reverse=True)
            for failure_type, count in sorted_failures:
                if count > 0:
                    f.write(f"{failure_type}: {count} occurrence(s)\n")
            if all(count == 0 for count in failure_types.values()):
                f.write("No validation failures found.\n")
            f.write(f"\n")
            
            # Error breakdown (detailed counts)
            f.write("ERROR BREAKDOWN (BY CATEGORY)\n")
            f.write("-" * 80 + "\n")
            f.write(f"Records with missing required fields: {statistics['records_with_missing_fields']}\n")
            f.write(f"Records with invalid URL format: {statistics['records_with_invalid_urls']}\n")
            f.write(f"Records with unwanted query parameters: {statistics['records_with_unwanted_query_params']}\n")
            f.write(f"Records with content below minimum length ({min_content_length} chars): {statistics['records_with_short_content']}\n")
            f.write(f"Records with title below minimum length ({min_title_length} chars): {statistics['records_with_short_titles']}\n")
            f.write(f"Records with invalid date format: {statistics['records_with_invalid_dates']}\n")
            f.write(f"\n")
            
            # Detailed error report
            if invalid_records:
                f.write("=" * 80 + "\n")
                f.write("DETAILED ERROR REPORT\n")
                f.write("=" * 80 + "\n\n")
                
                for record in invalid_records:
                    f.write(f"Record #{record['index']}\n")
                    f.write(f"  URL: {record['url']}\n")
                    f.write(f"  Title: {record['title']}\n")
                    f.write(f"  Errors ({len(record['errors'])}):\n")
                    for error in record['errors']:
                        f.write(f"    - {error}\n")
                    f.write("\n")
            else:
                f.write("=" * 80 + "\n")
                f.write("DETAILED ERROR REPORT\n")
                f.write("=" * 80 + "\n\n")
                f.write("No errors found! All records passed validation.\n\n")
            
            # Validation criteria
            f.write("=" * 80 + "\n")
            f.write("VALIDATION CRITERIA\n")
            f.write("=" * 80 + "\n")
            f.write("1. Required Fields: All records must have 'url', 'title', and 'content' fields\n")
            f.write("2. URL Format: URLs must be valid HTTP/HTTPS URLs\n")
            f.write("3. URL Query Parameters: URLs should not contain unwanted query parameters (utm_source, utm_medium, utm_campaign, ref=broken, id=)\n")
            f.write(f"4. Content Length: Content must be at least {min_content_length} characters\n")
            f.write(f"5. Title Length: Title must be at least {min_title_length} characters\n")
            f.write("6. Date Format: Dates must be in ISO format (YYYY-MM-DD) or 'N/A'\n")
            f.write("\n")
            
            # Overall status
            f.write("=" * 80 + "\n")
            if statistics['invalid_records'] == 0:
                f.write("OVERALL STATUS: ✓ ALL RECORDS PASSED VALIDATION\n")
            else:
                f.write(f"OVERALL STATUS: ✗ {statistics['invalid_records']} RECORD(S) FAILED VALIDATION\n")
            f.write("=" * 80 + "\n")
        
        print(f"Validation complete!")
        print(f"Total records: {statistics['total_records']}")
        print(f"Valid records: {statistics['valid_records']}")
        print(f"Invalid records: {statistics['invalid_records']}")
        print(f"Quality report saved to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{input_file}': {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    input_file = 'cleaned_output.json'
    output_file = 'quality_report.txt'
    
    # Minimum content length: 100 characters
    # Minimum title length: 10 characters
    generate_quality_report(input_file, output_file, min_content_length=100, min_title_length=10)
