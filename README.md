
## SCRAPER

* A tool written in Python for beginners to web scraping. This tool uses `curl_cffi` to make requests to the target web page and scrapes data from it. It works by simply storing links in the database and fetching data from each, then labeling the link's column `explored=True`.

* To use it, users need to write a custom class that inherits from `Extractor` in `app.extractors` and implements the abstract methods `extract_links`, `extract_content`, and `content_type`.

  * 1. `extract_links`

    * This method is used to discover links on the web page which the tool will eventually fetch data from.

  * 2. `extract_content`

    * Parses the resultant HTML and extracts downloadable media.

  * 3. `content_type`

    * A method used to specify what kind of data the scraper is looking for. An example is books.

    ***Example:***

```python
from app.extractors import Extractor

class YourExtractor(Extractor):
    def extract_links(self, data: BeautifulSoup) -> Dict[str, str]:
        pass

    def extract_content(self, data: BeautifulSoup) -> List[Tuple[str, str, Optional[int]]]:
        pass

    @classmethod
    def content_type(cls) -> str:
        return "books"

```

* Once the class has been defined, follow these steps:

  1. Import `Scraper` from `app.scraper` and create an instance.

  ```python
  from app.scraper import Scraper

  scraper = Scraper(
      db_path='mytestdb.sqlite',
      content_type=YourExtractor.content_type()
  )
  ```

  2. Start the scraping process by passing your extractor class and some starting URLs.

  ```python
  starting_urls = [("Crime and Punishment", "https://www.gutenberg.org/ebooks/2554")]

  scraper.run(
      starting_urls=starting_urls,
      extractor=YourExtractor()
  )
  ```

* The returned data from the above methods is stored in a database.

* The database has 3 tables:

  * 1. `Resource`:

    * Stores data about the URL — e.g., title, when it was discovered, and content type.

  * 2. `ContentFile`:

    * As the name suggests, it contains records of downloadable media (e.g., books, PDFs, etc.). Whether it's populated or not depends entirely on how the user defines the `extract_content` method.

  * 3. `DiscoveredLink`:

    * Stores discovered links for future exploration.

* This tool was refactored from its 2024 version after learning how to use SQLAlchemy ORM.

