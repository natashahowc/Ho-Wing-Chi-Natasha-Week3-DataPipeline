import json
import re
from datetime import datetime
from html import unescape
import unicodedata
from urllib.parse import urlparse

def remove_html_artifacts(text):
    """Remove HTML entities and artifacts from text"""
    if not text or text == 'N/A':
        return text
    
    # Decode HTML entities
    text = unescape(text)
    
    # Remove common HTML tags if any remain
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove HTML entities like &nbsp;, &amp;, etc.
    text = re.sub(r'&[a-zA-Z]+;', '', text)
    
    return text

def normalize_whitespace(text):
    """Remove extra whitespace and normalize spacing"""
    if not text or text == 'N/A':
        return text
    
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Replace multiple newlines with single newline
    text = re.sub(r'\n+', '\n', text)
    
    # Replace tabs with spaces
    text = text.replace('\t', ' ')
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)
    
    # Remove leading/trailing whitespace from entire text
    text = text.strip()
    
    return text

def normalize_text_encoding(text):
    """Normalize text encoding to UTF-8 and handle special characters"""
    if not text or text == 'N/A':
        return text
    
    # Normalize unicode characters (NFD to NFC)
    text = unicodedata.normalize('NFC', text)
    
    # Ensure UTF-8 encoding
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='ignore')
    
    return text

def parse_date_to_iso(date_str):
    """Convert various date formats to ISO format (YYYY-MM-DD)"""
    if not date_str or date_str == 'N/A':
        return None
    
    original_date_str = date_str
    # Remove common prefixes
    date_str = re.sub(r'^(Updated|Published|Posted)\s+', '', date_str, flags=re.IGNORECASE)
    date_str = date_str.strip()
    
    # Try to parse various date formats
    date_formats = [
        ('%b %d, %Y, %I:%M %p ET', lambda s: s),  # "Jan 29, 2026, 11:56 AM ET"
        ('%B %d, %Y, %I:%M %p ET', lambda s: s),  # "January 29, 2026, 11:56 AM ET"
        ('%b %d, %Y, %I:%M %p', lambda s: s.split(' ET')[0]),  # Without ET suffix
        ('%B %d, %Y, %I:%M %p', lambda s: s.split(' ET')[0]),  # Without ET suffix
        ('%b %d, %Y', lambda s: s.split(',')[0]),  # "Jan 29, 2026"
        ('%B %d, %Y', lambda s: s.split(',')[0]),  # "January 29, 2026"
        ('%Y-%m-%d', lambda s: s.split()[0]),  # "2026-01-29"
        ('%m/%d/%Y', lambda s: s.split()[0]),  # "01/29/2026"
        ('%d/%m/%Y', lambda s: s.split()[0]),  # "29/01/2026"
        ('%Y-%m-%d %H:%M:%S', lambda s: s.split()[0]),  # "2026-01-29 11:56:00"
    ]
    
    for fmt, preprocessor in date_formats:
        try:
            # Preprocess the string
            processed_str = preprocessor(date_str)
            # Try parsing with the format
            dt = datetime.strptime(processed_str.strip(), fmt)
            return dt.strftime('%Y-%m-%d')
        except (ValueError, IndexError, AttributeError):
            continue
    
    # Try to extract date from URL if it contains date pattern
    # This is a fallback for dates we can't parse
    date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', original_date_str)
    if date_match:
        year, month, day = date_match.groups()
        return f"{year}-{month}-{day}"
    
    # If all parsing fails, try to extract year-month-day pattern
    date_match = re.search(r'(\d{4})[-\s/](\d{1,2})[-\s/](\d{1,2})', original_date_str)
    if date_match:
        year, month, day = date_match.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    
    # Try to extract month day, year pattern more flexibly
    date_match = re.search(r'([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})', original_date_str)
    if date_match:
        month_str, day, year = date_match.groups()
        try:
            dt = datetime.strptime(f"{month_str} {day}, {year}", '%b %d, %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            try:
                dt = datetime.strptime(f"{month_str} {day}, {year}", '%B %d, %Y')
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                pass
    
    # Return None if we can't parse it
    return None

def handle_special_characters(text):
    """Handle special characters appropriately"""
    if not text or text == 'N/A':
        return text
    
    # Normalize quotes (smart quotes to regular quotes)
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Normalize dashes
    text = text.replace('—', '—').replace('–', '-')
    
    # Keep other special characters as they are (they're valid UTF-8)
    return text

def is_valid_url(url):
    """Validate URL format - same logic as validator.py"""
    if not url or url == 'N/A' or not isinstance(url, str):
        return False
    
    try:
        result = urlparse(url)
        # Check if URL has both scheme and netloc
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def has_unwanted_query_parameters(url):
    """Check if URL has unwanted query parameters - same logic as validator.py"""
    if not url or url == 'N/A':
        return False
    
    # Check for unwanted query parameters
    unwanted_params = ['utm_source', 'utm_medium', 'utm_campaign', 'ref=broken', 'id=']
    if '?' in url:
        query_string = url.split('?')[1]
        # Check if query string contains unwanted parameters
        return any(param in query_string for param in unwanted_params)
    
    return False

def is_url_valid(url):
    """Check if URL is valid (format and no unwanted query parameters)"""
    if not url or url == 'N/A':
        return False
    
    # Check URL format
    if not is_valid_url(url):
        return False
    
    # Check for unwanted query parameters
    if has_unwanted_query_parameters(url):
        return False
    
    return True

def clean_article(article):
    """Clean a single article"""
    cleaned = {}
    
    # Keep URL as-is (we'll filter invalid URLs in clean_data)
    cleaned['url'] = article.get('url', '').strip() if article.get('url') else ''
    
    # Clean title
    title = article.get('title', '')
    if title:
        title = normalize_text_encoding(title)
        title = remove_html_artifacts(title)
        title = handle_special_characters(title)
        title = normalize_whitespace(title)
    cleaned['title'] = title if title else 'N/A'
    
    # Clean content
    content = article.get('content', '')
    if content:
        content = normalize_text_encoding(content)
        content = remove_html_artifacts(content)
        content = handle_special_characters(content)
        content = normalize_whitespace(content)
    cleaned['content'] = content if content else 'N/A'
    
    # Clean and standardize date
    date_str = article.get('date', '')
    if date_str:
        iso_date = parse_date_to_iso(date_str)
        cleaned['date'] = iso_date if iso_date else 'N/A'
    else:
        cleaned['date'] = 'N/A'
    
    # Clean author
    author = article.get('author', '')
    if author:
        author = normalize_text_encoding(author)
        author = remove_html_artifacts(author)
        author = handle_special_characters(author)
        author = normalize_whitespace(author)
    cleaned['author'] = author if author else 'N/A'
    
    return cleaned

def clean_data(input_file, output_file):
    """Clean all articles from input file and save to output file"""
    try:
        # Read input JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Clean each article and filter out those with invalid URLs
        cleaned_articles = []
        removed_count = 0
        
        for article in data:
            # Check if URL is valid before processing
            url = article.get('url', '')
            if not is_url_valid(url):
                removed_count += 1
                continue  # Skip articles with invalid URLs
            
            # Clean the article
            cleaned_article = clean_article(article)
            cleaned_articles.append(cleaned_article)
        
        # Write cleaned data to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_articles, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully cleaned {len(cleaned_articles)} articles")
        if removed_count > 0:
            print(f"Removed {removed_count} article(s) with invalid URLs")
        print(f"Cleaned data saved to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{input_file}': {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    input_file = 'sample_data.json'
    output_file = 'cleaned_output.json'
    
    clean_data(input_file, output_file)
