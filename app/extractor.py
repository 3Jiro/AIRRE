# Text extraction engine - 
# Takes different file types (PDF, HTML, TXT) and extracts plain text from them. 
# Each file type has its own extraction method.
import PyPDF2
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextExtractor:
    """Extract text from various file types"""
    
    def __init__(self):
        self.supported_types = ['pdf', 'html', 'text']
    
    def extract_from_pdf(self, file_path: Path) -> Optional[str]:
        """Extract text from PDF file"""
        try:
            text = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text.append(f"--- Page {page_num + 1} ---\n{page_text}")
            
            return "\n\n".join(text) if text else None
        except Exception as e:
            logger.error(f"Error extracting PDF {file_path}: {e}")
            return None
    
    def extract_from_html(self, file_path: Path) -> Optional[str]:
        """Extract text from HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                
                # Remove script and style elements
                for element in soup(["script", "style", "nav", "footer"]):
                    element.decompose()
                
                # Get text and clean it up
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                return text if text else None
        except Exception as e:
            logger.error(f"Error extracting HTML {file_path}: {e}")
            return None
    
    def extract_from_text(self, file_path: Path) -> Optional[str]:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting text {file_path}: {e}")
            return None
    
    def extract_from_url(self, url: str) -> Optional[str]:
        """Extract text from URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for element in soup(["script", "style", "nav", "footer"]):
                element.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text if text else None
        except Exception as e:
            logger.error(f"Error extracting URL {url}: {e}")
            return None
    
    def extract(self, file_path: Path, file_type: str) -> Optional[str]:
        """Main extraction method"""
        extractors = {
            'pdf': self.extract_from_pdf,
            'html': self.extract_from_html,
            'text': self.extract_from_text
        }
        
        extractor = extractors.get(file_type)
        if extractor:
            return extractor(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_type}")
            return None