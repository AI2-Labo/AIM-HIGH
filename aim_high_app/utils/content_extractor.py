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
        
        # Mock content for demo purposes
        if 'openstax.org' in url:
            if 'eukaryotic-cells' in url:
                title = '3.4 Unique Characteristics of Eukaryotic Cells'
                content = 'Eukaryotic cells are characterized by a complex nuclear membrane. Also, eukaryotic cells are characterized by the presence of membrane-bound organelles in the cytoplasm. Organelles such as mitochondria, the endoplasmic reticulum (ER), Golgi apparatus, lysosomes, and peroxisomes are held in place by the cytoskeleton, an internal network that directs transport of intracellular components and helps maintain cell shape. The genome of eukaryotic cells is packaged in multiple, rod-shaped chromosomes as opposed to the single, circular-shaped chromosome that characterizes most prokaryotic cells.'
            elif 'motion-and-forces' in url:
                title = '4.1 Motion and Forces'
                content = 'Forces are the driving factor behind motion. Forces are essentially pushes or pulls that cause objects to move. By conducting experiments with a hacksaw blade and a truck, the concept of forces and their effects on motion is explored. When a constant force is applied to an object, it results in a constant acceleration. Increasing the force leads to a larger acceleration, while increasing the mass of the object results in a smaller acceleration. Forces are interactions between two objects, with every force having an agent that causes the force.'
            else:
                title = 'OpenStax Content'
                content = 'This is placeholder content from an OpenStax textbook chapter. The actual content would be extracted from the page you linked to.'
        else:
            # Try to extract content from the actual page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else url
            
            # Try to find the main content
            article = soup.find('article')
            if article:
                content = article.get_text()
            else:
                main_content = soup.find('main') or soup.find(id=re.compile('content|main', re.I)) or soup.find(class_=re.compile('content|main', re.I))
                if main_content:
                    content = main_content.get_text()
                else:
                    content = soup.body.get_text() if soup.body else soup.get_text()
            
            # Clean up the text
            content = re.sub(r'\s+', ' ', content).strip()
            content = content[:1500]  # Limit content length for preview
            
        return {
            'title': title,
            'content': content
        }
    except Exception as e:
        print(f"Error extracting content: {e}")
        return {
            'title': 'Error extracting content',
            'content': f'Failed to extract content from {url}. Please check if the URL is valid and accessible. Error: {str(e)}'
        }