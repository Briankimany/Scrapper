
from typing import Dict, Optional, Tuple
from pathlib import Path
from bs4 import BeautifulSoup
from app.extractors import Extractor
from app.utils import get_logger
from .books import BookExtractor as BE1

class BookExtractor(Extractor):
    log_dir = Path.cwd() / 'LOGS' / 'BOOK-EXTRACTOR'
    logger = get_logger(log_dir)
    CONTENT_TYPE = "zip"

    @classmethod
    def content_type(cls) -> str:
        return cls.CONTENT_TYPE

    @classmethod
    def _parse_book_li(cls, data: BeautifulSoup, book) -> Dict[str, str]:
        """Extract book title and link from list item"""
        try:
            title = book.find('span', class_='title').text.strip()
            sub_title = book.find('span', class_='subtitle').text.strip()
            link = data.host_link + book.find('a', class_='link')['href']
            return {link: f"{title} ({sub_title})"}
        except Exception as e:
            cls.logger.debug(f"Failed parsing book list item: {str(e)}")
            return {}

    @classmethod
    def _get_next_page(cls, data: BeautifulSoup) -> Dict[str, str]:
        """Extract pagination link"""
        try:
            next_page = data.find('li', class_='statusline').find('a')
            link = data.host_link + next_page['href']
            page = link.split('=')[-1]
            return {link: f'next-page-{page}'}
        except Exception as e:
            cls.logger.debug("No next page found")
            return {}

    @classmethod
    def _get_img_src(cls, data: BeautifulSoup) -> Optional[str]:
        """Extract cover image URL"""
        try:
            return data.find('div', id='cover').find('img').get('src')
        except Exception as e:
            cls.logger.debug("No cover image found")
            return None

    @classmethod
    def _parse_similar_books(cls, data: BeautifulSoup) -> Dict[str, str]:
        """Extract similar books links"""
        def parse_anchor(anchor):
            try:
                link = data.host_link + anchor['href']
                title = anchor.find('span', class_='title').text.strip()
                return {link: title}
            except Exception as e:
                return {}

        try:
            similar_books = data.find('div', id='more_stuff').find_all('a')
            return {k: v for anchor in similar_books for k, v in parse_anchor(anchor).items()}
        except Exception as e:
            cls.logger.debug("No similar books section found")
            return {}

    @classmethod
    def _get_books(cls, data: BeautifulSoup) -> Dict[str, str]:
        """Extract all book links from page"""
        books = data.find_all('li', class_='booklink')
        return {k: v for book in books for k, v in cls._parse_book_li(data, book).items()}

    @classmethod
    def _get_description(cls, data: BeautifulSoup) -> Optional[str]:
        """Extract book description"""
        try:
            return data.find('span', class_="readmore-container").text.strip("\n").strip()
        except Exception as e:
            cls.logger.debug("No description found")
            return None

    @classmethod
    def extract_book_links_metadata(cls, data: BeautifulSoup) -> Dict[str, str]:
        """Extract author and metadata links"""
        try:
            book_data = data.find('div', id='bibrec').find('table', id='about_book_table')
            return {
                data.host_link + a['href']: a.text.strip()
                for a in book_data.find_all('a')
                if a.text.strip() and a.has_attr('href')
            }
        except Exception as e:
            cls.logger.error(f"Metadata extraction failed: {str(e)}")
            return {}

    @classmethod
    def extract_links(cls, soup: BeautifulSoup) -> Dict[str, str]:
        """Aggregate all discoverable links from page"""

        links = {}
        links.update(cls._get_next_page(soup))
        links.update(cls.extract_book_links_metadata(soup))
        links.update(cls._get_books(soup))
        links.update(cls._parse_similar_books(soup))
        return links


    @classmethod
    def extract_content(cls,soup):
        
        return BE1.extract_content(soup=soup)