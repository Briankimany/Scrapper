
import random
import time
from datetime import datetime
from typing import Optional, Tuple

import curl_cffi
from bs4 import BeautifulSoup

import numpy as np 
from urllib.parse import urlparse
from pathlib  import Path

from app.models import  DiscoveredLink,Resource ,ContentFile
from app.db_manager import create_db 
from app.extractors import Extractor

class Scraper:
    def __init__(
        self,
        db_path: str = "scraper.db",
        content_type: str = "generic",
        request_timeout: int = 10,
        sleep_range: Tuple[float, float, float] = (20, 30, 0.3),
        user_agents: Optional[list] = None,
    ):
        # Database setup
        self.Session ,self.engine = create_db(db_path)

        # Configuration
        self.content_type = content_type
        self.request_timeout = request_timeout
        self.sleep_durations = list(np.arange(sleep_range[0], sleep_range[1], step=sleep_range[2]))
        self.user_agents = user_agents or [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
        ]
        
        # State tracking
        self.start_time = None
        self.run_time = "0:00:00"
        self.stats = {
            "resources": 0,
            "content_files": 0,
            "discovered_links": 0,
            "explored_links": 0,
        }
    
    def make_request(self, url: str) -> Tuple[Optional[int], Optional[BeautifulSoup]]:
        """Make a request using curl_cffi to impersonate a browser"""
        
        assert type(url) ==str
        try:
            with curl_cffi.requests.Session() as s:
                headers = {
                    "User-Agent": random.choice(self.user_agents),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                }
                response = s.get(
                    url,
                    headers=headers,
                    timeout=self.request_timeout,
                    impersonate="chrome110",
                )
                
                if response.status_code == 404:
                    return response.status_code, None
                
                soup = BeautifulSoup(response.text, "lxml")
                soup.from_url = str(url )
                
                parsed = urlparse(url)
                soup.host_link = f"{parsed.scheme}://{parsed.netloc}"
      
                soup.resource_path = Path(parsed.path)
                
                return response.status_code, soup
                
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None, None

    def get_random_unexplored_link(self, session) -> Optional[str]:
        """Get a random unexplored link from the database"""
        link = session.query(DiscoveredLink).filter_by(explored=False).first()

        return link.url if link else None

    def update_stats(self, session):
        """Update runtime statistics"""
        self.stats = {
            "resources": session.query(Resource).count(),
            "content_files": session.query(ContentFile).count(),
            "discovered_links": session.query(DiscoveredLink).count(),
            "explored_links": session.query(DiscoveredLink).filter_by(explored=True).count(),
        }

    def print_status(self):
        """Print current status to console"""
        elapsed = datetime.utcnow() - self.start_time
        self.run_time = str(elapsed).split(".")[0]  # Remove microseconds
        
        print(
            f"\n{'=' * 80}\n"
            f"Scraper Status - {self.content_type.title()} Content\n"
            f"{'-' * 50}\n"
            f"From : {self.stats.get('url')}\n"
            f"Number of new links :{self.stats.get('num_new_links')} | Num of content files {self.stats.get("num_content_files")}\n"
            f"Runtime: {self.run_time} | Resources: {self.stats['resources']}:|"
            f"Content Files: {self.stats['content_files']}:|"
            f"Links Discovered: {self.stats['discovered_links']}:|"
            f"Links Explored: {self.stats['explored_links']}\n"
            f"{'=' * 80}\n"
        )

    def run(
        self,
        extractor:Extractor,
        starting_urls: Optional[list] = None,
       
    ):
        """Main scraping loop"""
     
        self.start_time = datetime.utcnow()
        
        with self.Session() as session:
            # Add starting URLs if provided
            if starting_urls:
                for title ,url,in starting_urls:
                    if not session.query(Resource).filter_by(url=url).first():
                        resource = Resource(url=url, content_type=self.content_type,title=title)
                        session.add(resource)
                        session.commit()
                        
                        link = DiscoveredLink(url=url, resource_id=resource.id)
                        session.add(link)
                
                session.commit()
                self.update_stats(session)
            
            while True:
                # Get a random unexplored link
                current_url = self.get_random_unexplored_link(session)
                if not current_url:
                    print("No more unexplored links!")
                    break
                
                # Mark as explored
                link = session.query(DiscoveredLink).filter_by(url=current_url).first()
                link.explored = True
                link.resource.last_checked = datetime.utcnow()
                
                # Make request
                status_code, soup = self.make_request(current_url)
                if not soup:
                    session.commit()
                    continue
                
                # Extract content and links using provided functions
               
                content_files = extractor.extract_content(soup)
                if  content_files:
                    for file_url, file_type, file_size,image_src,description in content_files:
                        if not all([file_url,file_type]):
                            continue

                        if not session.query(ContentFile).filter_by(url=file_url).first():
                            file = ContentFile(
                                url=file_url,
                                file_type=file_type,
                                file_size=file_size,
                                resource_id=link.resource_id,
                                image_src=image_src,
                                description=description
                            )
                            session.add(file)
                
                # Extract new links
                new_links = extractor.extract_links(soup)
        
                for link_url, link_title in new_links.items():
                    # Check if we already know about this resource
                    resource = session.query(Resource).filter_by(url=link_url).first()
                    if not resource:
                        resource = Resource(
                            url=link_url,
                            title=link_title,
                            content_type=self.content_type
                        )
                        session.add(resource)
                        session.flush()  # Get the ID
                    
                    # Add to discovered links if not already there
                    if not session.query(DiscoveredLink).filter_by(url=link_url).first():
                        new_link = DiscoveredLink(
                            url=link_url,
                            resource_id=resource.id
                        )
                        session.add(new_link)
                
                session.commit()
                self.update_stats(session)
                self.stats['url']=link
                self.stats['num_new_links']=len(list(new_links.items()))
                self.stats['num_content_files'] = len(content_files)
                self.print_status()
                
                # Polite delay
                time.sleep(random.choice(self.sleep_durations))
