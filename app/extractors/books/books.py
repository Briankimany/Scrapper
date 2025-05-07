from app.extractors import Extractor
from bs4 import BeautifulSoup
from typing import Dict,Optional,List ,Tuple

from pathlib import Path
from bs4 import BeautifulSoup
from app.utils import get_logger


def parse_book_li(data,book):
    try:
        title = book.find('span',class_='title').text
        sub_title = book.find('span',class_='subtitle').text
        link =data.host_link+book.find('a',class_='link')['href']

        return {link:f"{title.strip()}({sub_title.strip()})"}
    except Exception as e:
    
        return {}

def get_next_page(data):
    try:
        next_page = data.find('li',class_='statusline').find('a')
        link = data.host_link+next_page['href']
        page = link.split('=')[-1]
        return {link:f'next-page-{page}'}
    except Exception as e:
        return {}
def get_img_src(data):
    try:
        return data.find('div',id='cover').find('img').get('src')
    except Exception as e:
        return None

def parse_similar_books(data):
   
    def get_similar_books(anchor):
        try:
            link = anchor['href']
            title = anchor.find('span',class_='title').text
            return {data.host_link+link :title}
        except Exception as e:
            return {}
    results = {}
    try:
        [results.update(get_similar_books(anchor=i)) for i in  data.find('div',id='more_stuff').find_all('a') ]
    except Exception as e:
        pass 
    return results

def get_books(data):
    books_link = data.find_all('li',class_='booklink')
    return_data = {}
    [return_data.update(parse_book_li(data,i)) for i in books_link]
    return return_data 

def get_description(data):
    try:
        description = data.find('span',class_="readmore-container")
        description=description.text.strip("\n")
        return description
    except Exception as e:
        return None


def get_download_link(data):
    try:
        downloadable_link = data.find(
            'div',class_ ='page-body'
        ).find('td',content='application/zip').find('a').get('href')

        return data.host_link + downloadable_link
    except Exception as e:
        return None 


def get_file_size(data: BeautifulSoup, content_type: str = 'zip') -> str:
    """Extract file size from first matching download link in the entire HTML"""
    try:
        return next(
            row.find('td', class_='right').get('content', '').strip("'")
            for row in data.find_all('tr', class_='even')
            if (a := row.find('a')) and a.get('href', '').endswith(content_type)
        )
    except StopIteration:
        return 'N/A'

class BookExtractor(Extractor):
    log_dir = Path().cwd()/'LOGS'/'BOOK-EXTRACTOR'

    logger = get_logger(log_dir)

    @classmethod
    def extract_book_links_metadata(cls,data: BeautifulSoup) -> dict:
        final_data = {}
        try:
            book_data = data.find('div',id='bibrec').find('table',id='about_book_table')
            author_rows = book_data.find_all('a')
            def parse_book_info(a):
                try:
                    link = data.host_link +a['href']
                    return {link:a.text.strip()} if a.text.strip() else {}
                except Exception as e:
                    return {}

            
            [final_data.update(parse_book_info(i)) for i in author_rows]
            return final_data
        except Exception as e:
            return final_data


    @classmethod
    def content_type(lcs) -> str:
        return "zip"
    @classmethod
    def extract_links(cls,soup) -> Dict[str, str]:

        next_page =  get_next_page(data=soup)
        authors = cls.extract_book_links_metadata(soup)
        books = get_books(soup)

        next_page.update(authors)

        next_page.update(books)
        next_page.update(parse_similar_books(soup))
        return  next_page
        
    
    @classmethod
    def extract_content1(cls,soup: BeautifulSoup) -> List[Tuple[str, str, Optional[int]]]:
 
        resource_path =  cls.log_dir/soup.resource_path

        content_type = cls.content_type()
        data = soup
        try:
            download_div = data.find('div', id='download')
            if not download_div:
                raise ValueError("No download div found")
                
            try:
               
                down = download_div.find_all('tr', class_='even')
                if len(down) < 2:
                    raise ValueError(f"Expected ≥2 rows, found {len(down)}")
                    
                for div in down:
                    try:
                    
                        anchor = div.find('a')
                        if not anchor:
                            continue
                            
                        href = anchor.get('href', '')
                        image_src=get_img_src(data) 

                        if href.endswith(content_type):
                            try:
                            
                                size_td = div.find('td', class_='right')
                                size = size_td.get('content', '').strip("'") if size_td else 'N/A'
                                return [(data.host_link+href ,
                                         content_type,
                                         size,image_src ,
                                         get_description(data))]
                            
                            except Exception as size_error:
                            
                                cls.logger.error(f"Size extraction failed in {resource_path.name}: {size_error}")
                                continue
                                
                    except Exception as row_error:
                
                        cls.logger.error(f"Row processing failed in {resource_path.name}: {row_error}")
                        continue
                        
                raise ValueError(f"No {content_type} link found in valid rows")
                
            except Exception as table_error:
            
                cls.logger.error(f"Table processing failed in {resource_path.name}: {table_error}")
                
        except Exception as global_error:
            cls.logger.error(f'global error {global_error}')
        
        return None 
    

    @classmethod
    def extract_content(cls,soup):
        download_link = get_download_link(soup)
        size = get_file_size(soup,cls.content_type())
        image_src = get_img_src(soup)
        description = get_description(soup)

        is_book =soup.from_url.split("/")[-2] == 'ebooks'
        if not is_book:
            return [] 
        if all([download_link,image_src]):
            return [(download_link,
                    cls.content_type(),
                    size,
                    image_src ,
                    description)]
        else:
            print("could not find downlaod link for ",soup.from_link)
            print("invalid data",download_link,image_src,description)
            return []