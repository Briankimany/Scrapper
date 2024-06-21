

import requests
import time
from datetime import timedelta
from tqdm.auto import tqdm
import os
import sys
import signal
import concurrent
from pathlib import Path


def download_resume(response, url, mode, downloaded_size , max_time , chunk_size = (1024**2)* 10):
    
    """
    Resumes the download of a file from a given URL.

    Args:
        url (FormatLinkobject): The URL of the file to be downloaded.
        mode (str): The mode to open the file in ('wb' for write-binary or 'ab' for append-binary).
        downloaded_size (int): The size of the already downloaded part of the file in bytes.

    Returns:
        None: Returns None if the download is successful or encounters an error.

    Raises:
        None
    """
    try:
        string_1 = " ".join(url.name.split(" ")[0:3])
        string_2 = " ".join(url.name.split(" ")[-3:])
        desctription = f"{string_1}...{string_2}"
        
        response = requests.get(url.final_link, stream=True, headers={"Range": f"bytes={downloaded_size}-"})
                
        with tqdm(total=round(url.file_size, ndigits=3), desc=desctription) as progress_bar:
            with open(url.full_path, mode) as file:
                progress_bar.update(downloaded_size / 1024 ** 2)
                start_time = time.time()
                # for chunk in response.iter_content(chunk_size=url.chunk_size):
                while True:
                    chunk = requests.get(url.final_link, stream=True, headers={"Range": f"bytes={downloaded_size}-", "Chunk-size":f"{chunk_size}"}).content
                    try:
                        file.write(chunk)
                        file.flush()
                        
                        downloaded_size = os.path.getsize(url.full_path)
                        
                        url.save_currrent_state()
                        progress_bar.update(len(chunk) / 1024 ** 2)
                        
                        url.remaining_size -= len(chunk) / 1024 ** 2
                        url.hard_drive_file_size += len(chunk) / 1024 ** 2
                        url.remainig_size_percentage
                        
                        duration = time.time() - start_time
                        current_size = os.path.getsize(url.full_path)
                        changed_size = current_size - downloaded_size
                        speed = round(changed_size / (duration * 1024 ** 2), ndigits=3)
                        desctription = f"{url.short_name} AT {speed} MB/S"
                        progress_bar.set_description(desctription)
                        
                        if timedelta(seconds=duration) > max_time:
                            print("max time reached")
                            break
                        
 
                            
                        if url.hard_drive_file_size == url.file_size:
                            break
                    except KeyboardInterrupt:
                        return "BREAK"
                    

        url.is_downloaded = True
        file.close()
        url.save_currrent_state()
        return None
    except KeyboardInterrupt:
        print("Breraking in the iner funtion")
        return "BREAK"


def manage_download(url, max_time  , parent_object = None):
    
    file_headers = requests.head(url.final_link)
    if "File-name" in file_headers.headers:
        url.full_path = Path(file_headers.headers['File-name'])

    downloaded_size = int(os.path.getsize(url.full_path)) if url.full_path.is_file() else 0
    url.remaining_size = (url.file_size * (1024**2)) - downloaded_size
    url.remainig_size_percentage =  url.remaining_size / (url.file_size * (1024**2)) 
    if not url.in_data_base:
        resumeS_from = input(f"Resume from {downloaded_size / 1000 ** 2}")
        if resumeS_from != 'y':
            return None
        
    if url.remainig_size_percentage == 0:
        print("File already present")
        return None
    if 0 < url.remainig_size_percentage < 1:
        mode = 'ab'
    elif url.remainig_size_percentage == 1:
        mode = 'wb'
        
    else:
        print("undeterministinc mode")
        mode == None
    
    response = requests.get(url.final_link, stream=True, headers={"Range": f"bytes={downloaded_size}-"})
    
    if response.status_code == 206 or response.status_code == 200:
        if response.status_code == 200:
            print("STARTING FROM SCRATCH: " ,url.full_path)
            downloaded_size =0
            mode = "wb"
        # print("Valus gottent" , mode , url.short_name , downloaded_size , max_time)
        result =  download_resume(response,url, mode, downloaded_size , max_time)
        
        if result == "BREAK":
            return None
                    
    elif response.status_code == 416:
        url.log(mesage="RANGE IS INSTATISFIABLE")
        return None
    else:
        url.log(message=response)
        print("Failed to resume download. New status code UNKNOW conditions:", response.status_code)
        if not url.in_data_base:
            raise ValueError(f"UNKNOW CONITION CHECK TH LOG FILE {url.full_path}")
    return None


def download_bit_by_bit(self):
    
    """
    Downloads a file bit by bit, allowing resumption if interrupted.

    Args:
        self (FormatLink object): The instance of the class containing file download information.
        target (object): The target object to download the file to (default is None).

    Returns:
        None: Returns None if the download is successful or encounters an error.

    Raises:
        None
    """
    max_time = timedelta(hours=15, minutes=0, seconds=60)
    url = self
    if self.file_size is not None and not self.in_data_base :
        try:
            return manage_download(url=self , max_time= max_time , parent_object=self)
        except KeyboardInterrupt:
            print("Stopping the program in the individual download")
            return None
        finally:
            self.save_currrent_state()
    
    elif self.in_data_base and self.file_size != None :
        # print("using unnnested download manager")
        return manage_download(self , max_time=max_time)
        
    else:
        self.log(message="got file size as none")
    return None




import signal

class Batches:
    def __init__(self , url_batches) -> None:
        self.batches = url_batches
        

def download_files(url_batches):
    urls = Batches(url_batches=url_batches)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for batch in urls.batches:
            batch_futures = [executor.submit(download_bit_by_bit, url)  for url in batch]
            for future in concurrent.futures.as_completed(batch_futures):
                    result = future.result()
                    if result == "BREAK":
                        # Handle the "BREAK" result by stopping further downloads in the batch
                        print("Download in the batch interrupted. Skipping remaining downloads in the batch.")
                        break
            

