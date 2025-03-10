# aim_high_app/utils/content_extractor.py

import requests
from bs4 import BeautifulSoup
import re

def extract_content_from_url(url):
    """
    Extract main content from a URL
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Extract title
        title = soup.title.string if soup.title else url
        
        # Try to find the main content
        # First look for article tags
        article = soup.find('article')
        if article:
            content = article.get_text()
        else:
            # Try to find main content div
            main_content = soup.find('main') or soup.find(id=re.compile('content|main', re.I)) or soup.find(class_=re.compile('content|main', re.I))
            if main_content:
                content = main_content.get_text()
            else:
                # Fallback to body text
                content = soup.body.get_text() if soup.body else soup.get_text()
        
        # Clean up the text
        content = re.sub(r'\s+', ' ', content).strip()
        
        return {
            'title': title,
            'content': content[:5000]  # Limit content length
        }
    except Exception as e:
        print(f"Error extracting content: {e}")
        return {
            'title': 'Error extracting content',
            'content': f'Failed to extract content from {url}: {str(e)}'
        }