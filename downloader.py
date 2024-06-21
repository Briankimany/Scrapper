

import io , requests , os
import time
from PIL import Image
from tqdm.auto import tqdm
from naughty import save_load_program_data
from urllib.parse import urlparse
from bs4 import BeautifulSoup as Soup
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict , Tuple
import random
import more_itertools
from concurrent.futures import as_completed

from master import FullDataBase , FormatLink , format_links  , log


def save_content(requested_data , link):
    # Parse the HTML content
    path = urlparse(link).path
    full_path = os.path.join(path ,"file.html" )
    soup = Soup(requested_data.content, 'html.parser')

    # Save parsed HTML data to a file
    with open(full_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))
        

class Downloader(FullDataBase):
    
    def __init__(self,
                 complete_data_base_path = "COMPLETE.json", 
                 full_data_base_path = None, 
                 complete_destination="TESTING DIR",
                 ready_links=None, 
                 num_threads=5, 
                 max_file_size = 500 , 
                 chunk_size = 1024 , 
                 multiple = True):
        print(ready_links)
        super().__init__(complete_data_base_path = complete_data_base_path,
                         source_data_base_path = full_data_base_path,
                         complete_destination = complete_destination, 
                         ready_links = ready_links, 
                         num_threads = num_threads)
    

        
        self.destination_dir =self.parent_dir
        # self.destination_dir.mkdir(exist_ok=True ,parents=True)
        
        # self.source_data_path = source_data_path
        # self.data = list((save_load_program_data(path=self.source_data_path)).items())
        self.complete_downloads =0
        self.random_sleeps = [1,0.2, 0.3,0.5]
        self.request_counts = 0
        
        self.chunk_size = chunk_size
        self.max_file_size = max_file_size
        self.is_sequential = False
        
        
        self.multiple= multiple
    def download_bit_by_bit(self ,url:FormatLink):
            try:
                remaining_size = url.remaining_size
                downloaded_size = url.hard_drive_file_size
                string_1 = " ".join (url.name.split(" ")[0:3])
                string_2 = " ".join (url.name.split(" ")[-3:])
                desctription =  f"{string_1}...{string_2}"
                # print("here is remaining ",url.remainig_size_percentage)
                if  url.remainig_size_percentage > 0:
                    # print("Cant downloadd a downloded file")
                    # print(f"Resuming download from {downloaded_size} Mb")
                    desctription = f"Resuming..{remaining_size}:" + desctription 
                    file = open(url.full_path, "ab")
                else:
                    file = open(url.full_path, "wb")
                response = requests.get(url.final_link, stream=True, headers={"Range": f"bytes={downloaded_size}-"} )
                # print(f"Here is the response {response.status_code} for {url.full_path} , size {url.file_size}")
                if response.status_code == 206:
                    if self.multiple:
                            for chunk in response.iter_content(chunk_size=self.chunk_size):
                                file.write(chunk)
                                file.flush()  
                            self.downloded_data_dict[url.full_path] = True
                    else:
                        with tqdm(total=round(url.file_size, ndigits=3)  ,desc= desctription) as progress_bar:    
                            # progress_bar.update(downloaded_size)  
                            for chunk in response.iter_content(chunk_size=self.chunk_size):
                                file.write(chunk)
                                file.flush()
                                progress_bar.update(round(len(chunk)/1024**2 , ndigits=3)) 
                                url.remaining_size -= len(chunk)/1024**2
                                url.downloaded_size += len(chunk)/1024**2
                                
                                progress_bar.set_description(desctription)
                                
                        self.downloded_data_dict[url.full_path] = True
                        file.close()
                        if self.is_sequential:
                            save_load_program_data(path=self.downloded_data_path , data=self.downloded_data_dict)
                        # print(f"done  downloding {url.full_path}")
                elif response.status_code == 416:
                    log(link=url , mesage=response , class_="r" , path_='Logs/Downloads')
                    print("Cant resume download ")
                    return None
                    
                else:
                    log(link=url , mesage=response , class_="r" , path_='Logs/Downloads')
                    print("Failed to resume download new status code: Status code:", response.status_code)
                file.close()
                return None
            except OSError as e:
                if e.errno == 36:
                    name , ext = os.path.splittext(url.full_path)
                    name = name.split[','][0]  + ext
                    url.full_path = self.destination_dir / name
                    log(link=url , mesage=e , path_='Logs/Downloads')   
                    
                                     
    
    def download_multiple_data_sequentially(self , data:Tuple = None):
        self.is_sequential = True
        if data == None:
            data = self.non_downloded_links
        for img_data in tqdm (data):
            # try:
                out_daya = self.download_bit_by_bit(img_data)
                self.request_counts +=1
            # except Exception as e:
            #     print
            #     pass
            
                
    def threaded_download(self):
        
        num_threads = self.num_threads
        batched_data = self.batched_data
        try:
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                with tqdm(total=len(self.batched_data) , desc=f"Downloading {self.complete_downloads} // {len(self.all_links)}") as pbar:
                    for batch in list(batched_data):
                        results = [executor.submit( self.download_bit_by_bit,one_data) for one_data in batch] 
                        for i in  as_completed(results):
                            i.result()
                            pbar.set_description(desc=f"Downloading {self.complete_downloads} // {len(self.non_downloded_links)}")
                            self.complete_downloads+=1
                            pbar.update(1)                   
                        sleep_time = random.choice([3, 10, 14])
                        pbar.set_description(f"Slepping for {sleep_time}")        
                        time.sleep(sleep_time)
                        pbar.set_description(desc=f"Downloading {self.complete_downloads} // {len(self.all_links)}")
        except FileNotFoundError as e:
            print(e)
            time.sleep(10)
        except MemoryError:
            print("Memory error")
        # except Exception as e:
        #     print(str(e) ,"Sleeping for 40 seconds")
            
        #     time.sleep(3)
        
if __name__ == "__main__":
    
    base_1 =".video_data/full_data_base.json"
    base_2 = "/home/brian/Videos/.hiden/full_database_v3.json"
    formated_links = random.sample(format_links(full_data_base_path= base_1) , k = 4)
    print(formated_links)
    downloader_1 = Downloader(complete_data_base_path=None,
                              complete_destination ="TREST DIR/TEST_8/COMPLETE_TEST.json",
                              full_data_base_path = None,
                              ready_links= formated_links,
                              num_threads=5,
                              multiple=False
                              )
    
    downloader_1.prepare_full_data_base()
    downloader_1.threaded_download()
    # downloader_1.save_complete_data_base()
    # downloader_1.download_multiple_data_sequentially()
