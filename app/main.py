
from app.extractors.books import BookExtractor
from app.scraper import Scraper

if __name__ == "__main__":
    scraper = Scraper(
        db_path="test2.db",
        content_type=BookExtractor.content_type())
    
    scraper.run(starting_urls=[("intitial book","https://www.gutenberg.org/ebooks/2554")],
                extractor=BookExtractor())