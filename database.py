

from pathlib import Path
from format_link import FormatLink
from tqdm.auto import tqdm
import more_itertools
from concurrent.futures import ThreadPoolExecutor , as_completed

from master import save_load_program_data
from download_2 import download_files
import config
import os
class DataBase:
    
    """
    A class that manages a database of media links and their associated data.

    This class is responsible for loading and processing link data from various sources, such as a directory of JSON files or a pre-existing database, and initializing individual `FormatLink` objects. It also provides a method to download the media files associated with the links.

    Attributes:
        source_dir (pathlib.Path): The path to the directory containing the source data (e.g., JSON files).
        
        scrapped_data_base_path (pathlib.Path): The path to the pre-existing database file.
        
        max_num (int): The maximum number of links to process.
        
        batch_size (int): The size of each batch of links to process in parallel.
        
        parent_dir (pathlib.Path): The parent directory for the downloaded media files.
        
        all_links (list): A list of lists, where each inner list contains `FormatLink` objects for a batch of links.
        
        link_data (dict): The link data loaded from the pre-existing database.
        
        json_files (list): A list of the JSON files found in the source directory.
        
        data (list): The raw link data, either from the pre-existing database or the JSON files.

    Methods:
        __init__(self, parent_dir, source: pathlib.Path = None, scrapped_data_base_path: pathlib.Path = None, max_num: int = 2000, batch_size: int = 3):
            Initializes the `DataBase` object and loads the link data from the specified sources.

        initialize_link(self, i):
            Initializes a `FormatLink` object from the link data, either from the pre-existing database or the JSON files.

        download(self):
            Initiates the download of the media files associated with the links, using the `download_files` function.
    """
    
    def __init__(self ,parent_dir , source  = None ,scrapped_data_base_path :Path = None , max_num = config.MUX_NUM , batch_size = config.BATCH_SIZE,
                 db_dict = config.DB_DICT) -> None:
        
            
        self.source_dir = Path(source) if source else None     
        self.scrapped_data_base_path = Path(scrapped_data_base_path) if scrapped_data_base_path else None
        json_files =None
        link_data = None
        self.parent_dir = Path(parent_dir)
        self.all_links = []
        
        if db_dict.exists():
            pass
        else:
            if self.scrapped_data_base_path:
               data = save_load_program_data(path=self.scrapped_data_base_path).copy()
            else:
               data = {}
            save_load_program_data(data=data ,path=db_dict , mode='w')

        
        if scrapped_data_base_path == None or self.source_dir == None and not (self.scrapped_data_base_path == self.source_dir == None):
            if self.source_dir != None and  self.source_dir.is_dir() and self.scrapped_data_base_path == None:
                json_files = sorted(list(self.source_dir.glob("*.json")))
        
            if self.scrapped_data_base_path != None and self.scrapped_data_base_path.is_file() and self.source_dir == None:
                link_data = save_load_program_data(self.scrapped_data_base_path)
            

            self.link_data = link_data
            self.json_files = json_files
            
            self.data = sorted(list(self.link_data.items()) if link_data else  self.json_files)
            
        elif self.scrapped_data_base_path == self.source_dir == None:
            link_data = save_load_program_data(config.FULL_DATA_BASE_PATH) if config.FULL_DATA_BASE_PATH.exists() else []
        else:
            link_data = save_load_program_data(self.scrapped_data_base_path)
            json_files = sorted(list(self.source_dir.glob("*.json")))
            
            self.data = json_files + sorted(list(link_data.items()))  
            
            
 
        if max_num in range(len(self.data)):
            self.data = self.data[0:max_num]
             
        batched_data = list(more_itertools.batched(self.data ,batch_size)) 
        
        for i in batched_data:
            print(i)
        with tqdm(total=len(self.data) , desc="Initializing") as pbar:
            with ThreadPoolExecutor() as executor:
                for batch in batched_data:
                    batch_links = []
                    results  = [executor.submit(self.initialize_link , i) for i in batch]
                    for result in as_completed(results):
                        link = result.result()
                        # print("here us h",link.full_path)
                        batch_links.append(link) 
                        pbar.update(1) 
                    self.all_links.append(batch_links)
                    
        
    def initialize_link(self , i):
        if  isinstance(i , (tuple,list)):
            link_data = i
            json_files = None
            return FormatLink(link_data=link_data ,parent_dir=self.parent_dir ,in_data_base=True,source_json= json_files)
        elif i.exists():
            json_files = i 
            link_data = None
            return FormatLink(link_data=link_data ,parent_dir=self.parent_dir ,in_data_base=True,source_json= json_files)
        else:
            print("Got a an unexpected input" , i)
                
    def download(self):
        try:
            download_files(self.all_links)
        except KeyboardInterrupt:
            print("BREAKING THE THREADS")
            return None
        
    def inspect(self):
        for batch in self.all_links:
            batch_names = [str(i.short_name) for i in batch]
            print(batch_names)
            
            
    
if __name__ == "__main__":
    while True:
        try:
            db = DataBase(parent_dir=config.CONTENT_LOCATION ,source= config.JSON_DATA_LOCATION ,
                          batch_size=config.BATCH_SIZE , scrapped_data_base_path=config.FULL_DATA_BASE_PATH ,
                          max_num= 100)
            db.download()
        except KeyboardInterrupt:
            break
