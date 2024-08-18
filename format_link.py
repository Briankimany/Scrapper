import os  , requests
from pathlib import Path
from tqdm.auto import tqdm
import more_itertools
from concurrent.futures import ThreadPoolExecutor , as_completed
from datetime import timedelta

from master import convert_duration_format , generate_random_chars , get_file_size , change_str_deltatime , save_load_program_data , get_link_default_state
from download_2 import download_bit_by_bit , download_files


class FormatLink:
    """
        Link data = (link , description , duration)
    """
    def __init__(self, link_data=None  , include_radom = False , parent_dir = None , in_data_base = True ,source_json = None , save_info = True , chunk_size = (1024**2)*3 , is_verified_final_link = False) -> None:

        self.is_final_link = False
        self.in_data_base = in_data_base
        self.save_per_isnstance = save_info
        
        default_state = get_link_default_state()
        default_state.update(self.__dict__)
        [setattr(self , key , value) for key , value in default_state.items()]
   
        
        viable_ext = ['.mp4' , '.mp3' , '.zip' , '.mkv' , '.nfo' , '.url' , '.iso' , '.torrent' , '.bin' , '.exe' , '.url' , '.bat']
        
        
        if link_data != None:
            data = link_data
            self.url = link_data[0] 
            if "http" not in data[0]:
                link_data = list(link_data)
                link_data[0] = data[1]
                link_data[1] = data[0]
                
       
            self.extension = f".{self.url.split('.')[-1]}"
            if self.extension.lower() in viable_ext or is_verified_final_link:
                self.is_final_link = True
                if "/" in self.extension:
                    self.extension = '.UNKNOWNEXT'
            else:
                self.extension = self.name
            
            if isinstance(link_data[1] , (tuple, list)):
                self.name = str(link_data[1][0]) +"_"+ generate_random_chars(k=4) if include_radom else  str(link_data[1][0])
                if len(link_data[1]) >= 2:
                    try:
                        self.length = convert_duration_format(link_data[1][1])
                    except Exception as e:
                        self.length = None
            else:
                if isinstance(link_data[1], (str)):
                    self.name = link_data[1] + generate_random_chars(k=4)  if include_radom else link_data[1] 
                    self.length = None
                else:
                    self.name = None
                    self.length = None
        
            if self.name != None:
                try:
                    j =self.name
                    j = j.encode().decode()
                    self.name = j
                except Exception as e:
                    pass
                
            self.name = self.name.replace(os.path.sep , "_") if self.name != None else f"Random_name_{generate_random_chars(k=4)}"
            if len(self.name.split(" ")) > 15:
                name_parts = self.name.split(" ")
                self.short_name = " ".join(name_parts[0:3]) + "..." + " ".join(name_parts[-3:])
            else:
                self.short_name = self.name 
                
            if parent_dir:
                self.parent_dir = Path(parent_dir)
                self.log_dir = self.parent_dir /"LOGS"
            else:
                raise ValueError ("detination dir cant be none")
        
            self.short_name = Path(self.short_name)
            self.full_path = self.parent_dir/self.short_name.with_suffix(self.extension)  if self.is_final_link else None
            self.json_path = self.parent_dir /"JSON DATA"/ Path(self.full_path.name).with_suffix(f'{self.extension}.json')  if self.is_final_link else None
            
            if self.is_final_link:
                self.json_path.parent.mkdir(parents= True , exist_ok=True)
                self.full_path.parent.mkdir(parents=True , exist_ok=True)
                
            if self.is_final_link:
                if chunk_size != None:
                    self.chunk_size = chunk_size
                self.prepare_link()
            
        if source_json != None:
            saved_state = save_load_program_data(path=source_json)
           
            default_state.update(saved_state)
         
            for key , value in default_state.items():
                setattr(self , key , value)
         
            if self.extension in viable_ext:
                self.is_final_link = True
           
            self.in_data_base= in_data_base
            if chunk_size != None:
                self.chunk_size = chunk_size

            if self.name != None:
                try:
                    j =self.name
                    j = j.encode().decode()
                    self.name = j
                except Exception as e:
                    pass
          
        if parent_dir:
            self.parent_dir = Path(parent_dir)
        else:
            raise ValueError ("detination dir cant be none")
        
        self.log_dir = self.parent_dir /"LOGS"
        self.short_name = Path(self.short_name)
        self.full_path = self.parent_dir/ self.short_name.with_suffix(self.extension) if self.is_final_link else None
        self.json_path = self.parent_dir /"JSON DATA"/ Path(self.full_path.name).with_suffix(f'{self.extension}.json') if self.is_final_link else None
        
        if self.is_final_link:
            self.json_path.parent.mkdir(parents= True , exist_ok=True)
            self.full_path.parent.mkdir(parents=True , exist_ok=True)
        
        
        if isinstance(self.parent_dir , Path):
            pass 
        else:
            self.parent_dir = Path(self.parent_dir)
            self.full_path = Path(self.full_path) if self.is_final_link else None
            self.log_dir = Path(self.log_dir)
        
        if self.is_final_link:
            if not isinstance(self.file_size , float):
                self.file_size = float(self.file_size) if self.file_size != None else None
                self.chunk_size = int(self.chunk_size)
                self.remaining_size = float(self.remaining_size)
                self.hard_drive_file_size = float(self.hard_drive_file_size)
                self.remainig_size_percentage = float(self.remainig_size_percentage)
            
            if not isinstance(self.length ,  timedelta) and self.length != None: 
                self.length = change_str_deltatime(self.length)
    
            self.prepare_link() 
        self.parent_dir.mkdir(parents = True , exist_ok = True)
        if self.is_final_link:
            starting_data = self.get_state_data()
      
            save_load_program_data(path= self.json_path, data= starting_data , mode='w')

    
    def see(self):
        text = f"Saving to:{self.full_path}\tName:{self.name}\tLength:{self.length}\tFile size:{self.file_size}\tFinal link:{self.final_link}\n"
        decorations = "*" * len(text)
        print(f"{decorations}\n{text}\n{decorations}")
        
    
    def log(self, message):
        link = self
        link.log_dir.mkdir(exist_ok = True , parents = True)
        info = str(message)    
         
        if self.is_final_link:
            error_path = (link.log_dir/link.name).with_suffix(f".{link.extension}.json") 
        if not self.is_final_link:
                error_path =self.log_dir/self.name
                error_path = error_path.with_suffix(".json")
  
        logs = link.get_state_data()
        logs.update({"Error":info})
        save_load_program_data(path=error_path , data=logs , mode='w')
    
    
    def prepare_link(self):
        if self.final_link == None:
            self.file_size , self.final_link =  get_file_size(link = self)  
        link = self                
        try:
            file_size = (os.path.getsize(link.full_path) / 1024**2) if link.full_path.is_file() else 0
            remaining_size = link.file_size  - file_size if link.file_size != None else 0
            
            if link.file_size != None and link.file_size > 0:
                remainig_size_percentage = remaining_size /float(link.file_size) if link.file_size != None else 0
            else:
                remainig_size_percentage  = 0
        
            link.remaining_size = remaining_size 
            link.hard_drive_file_size = file_size 
            link.remainig_size_percentage = remainig_size_percentage
            return True
        except Exception as e:
            self.log(mesage=e)  
            return False
    

    
    def get_state_data(self):
        data_to_save = {}
        for key , value in self.__dict__.items():
            if  isinstance(value , Path):
                value = str(value) 
            if isinstance(value , timedelta):
                value = str(value)
            data_to_save[key] = value
        return data_to_save
    
    def save_currrent_state(self):
        if self.is_final_link:
            self.prepare_link()
            data = self.get_state_data()
            save_load_program_data(path =self.json_path , data = data , mode='w')
                
    def start_download(self):
        if self.full_path.exists():
          
            pass
        download_bit_by_bit(self)
        return None
    
    def inspect(self):
        try:
            current_percentage = int((self.hard_drive_file_size / self.file_size) * 100)
            print("*****\nInspecting  ...")
            text = "Name: {}\nFormat: {}\nSize: {}\nDisk size: {}\nDestination: {}\nCompleted percentage: {}".format(self.short_name , self.extension, self.file_size ,
                                                                                                                    self.hard_drive_file_size, Path(self.full_path).absolute(), current_percentage)
            print(text,"\n******")
        except Exception as e:
            self.log(message=str(e))
    

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
    
    def __init__(self ,parent_dir , source:Path  = None ,scrapped_data_base_path :Path = None , max_num = 2000 , batch_size = 3) -> None:
        
        self.source_dir = Path(source) if source else None
        self.scrapped_data_base_path = Path(scrapped_data_base_path) if scrapped_data_base_path else None
        json_files =None
        link_data = None
        self.parent_dir = Path(parent_dir)
        self.all_links = []
        
        if self.source_dir != None and  self.source_dir.is_dir():
            json_dest = self.source_dir /"JSON DATA"
            json_files = list(json_dest.glob("*.json"))
  
        if self.scrapped_data_base_path != None and self.scrapped_data_base_path.is_file():
            link_data = save_load_program_data(self.scrapped_data_base_path)
            
        self.link_data = link_data
        self.json_files = json_files
        
        self.data = list(self.link_data.items()) if link_data else  self.json_files
    
        if max_num in range(len(self.data)):
            self.data = self.data[0:max_num]
             
        batched_data = list(more_itertools.batched(self.data ,batch_size)) 
   
        with tqdm(total=len(self.data) , desc="TEsting") as pbar:
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
        if self.link_data != None :
            link_data = i
            json_files = None
        if self.json_files != None:
            json_files = i 
            link_data = None
        link_data = FormatLink(link_data=link_data ,parent_dir=self.parent_dir ,in_data_base=True,source_json= json_files)
        return link_data
         
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
    from format_link import DataBase    
    d = DataBase(source="/home/brian/Videos/.backup/CLASSED SCRAPPER" ,parent_dir="database")
    d.download()
    
    