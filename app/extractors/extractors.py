from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup


class BaseExtractor(ABC):
    """Abstract base class for all scraper extractors"""
    
    @classmethod
    @abstractmethod
    def content_type(cls) -> str:
        """Return the type of content this extracts (e.g., 'book', 'movie')"""
        pass

class LinkExtractor(BaseExtractor):
    @abstractmethod
    def extract_links(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extract navigable links from a page
        
        Returns:
            Dict[absolute_url: str, link_title: str]
            Example: {"https://site.com/page1": "Page Title"}
            
        Notes:
            - Must return absolute URLs
            - Titles should be cleaned (no extra whitespace/newlines)
        """
        pass

class ContentExtractor(BaseExtractor):
    @abstractmethod
    def extract_content(self, soup: BeautifulSoup) -> List[Tuple[str, str, Optional[int]]]:
        """
        Extract downloadable content from a page
        
        Returns:
            List[Tuple[
                absolute_url: str, 
                file_type: str (lowercase extension), 
                file_size_bytes: Optional[int]
            ]]
            Example: [("https://site.com/doc.pdf", "pdf", 1024)]
        """
        pass


class Extractor(LinkExtractor,ContentExtractor):
    pass 
