import tempfile
from datetime import timedelta
import requests , random , time

import string
from datetime import datetime, timedelta
from pathlib import Path
import os
import json 



def save_program_data(path, data, mode='w'):
    """
    Saves or loads data to/from a JSON file.

    Args:
        path (str): The path to the JSON file.
        data (dict, optional): The data to be saved to the file. Defaults to None.
        mode (str, optional): The mode to open the file in. Can be either 'r' for reading or 'w' for writing. Defaults to 'r'.

    Returns:
        dict or None: The loaded data or None if an error occurred.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            if mode == 'w':
                for key, value in data.items():
                    json_str = (json.dumps({key: value})+ "\n").encode('utf-8')
                    temp_file.write(json_str )
            elif mode == 'r':
                full_data = {}
                for line in temp_file:
                    loaded_json = json.loads(line)
                    full_data.update(loaded_json)
                return full_data
            temp_file.flush()
        os.rename(temp_file.name, path)
    except Exception as e:
        print(f"Error saving/loading data: {e}")
        return None



def save_load_program_data(path , data=None , mode ='r'):
    return save_program_data(path=path , data= data ,mode=mode)



def get_link_default_state():
    default_state = {'parent_dir': Path('Movies'),
                    'log_dir': Path('LOGS'),
                    'url': None,
                    'extension': None,
                    'final_link':None,
                    'file_size': None,
                    'full_path': None,
                    'length': None,
                    'is_downloaded': False,
                    'in_data_base': False,
                    'chunk_size': 1024,
                    'name': None,
                    'short_name': None,
                    'remaining_size': None,
                    'hard_drive_file_size': 0,
                    'remainig_size_percentage': 1.0}
    
    return default_state
  

def get_file_size(link):
    try:
        if link.final_link == None:
          
            response = requests.head(link.url)
            g =0
            redirect_link = link.url
            while int(response.status_code) == 302:
    
                redirect_link = response.headers['Location']
                response = requests.head(redirect_link)
                g+=1
                if g == 10:
                    return None , None
            file_size = int(response.headers.get('content-length', 0)) / 1024**2
        else:
            redirect_link = link.final_link
            file_size= link.file_size
        
        return file_size , redirect_link
    except Exception as e:
        link.log(message=str(e))
        return None , None
        
        
def convert_duration_format(duration_str):
 
    try:
        hours = 0
        minutes =0
        seconds = 0
       
        if 'H' in duration_str:
            hours = int(duration_str.split('H')[0][1:])
        if 'M' in duration_str:
            minutes = int(duration_str.split('M')[0][-2:])
        if 'S' in duration_str:
            seconds = int(duration_str.split('S')[0][-2:])

        duration_timedelta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        
        return duration_timedelta
    except Exception as e:
        print(str(e))
        return None


      

def change_str_deltatime(time_delta_str):
    time_delta = datetime.strptime(time_delta_str, '%H:%M:%S')
    time_delta = timedelta(hours=time_delta.hour, minutes=time_delta.minute, seconds=time_delta.second)
    return time_delta
        

def generate_random_chars(k):
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=k))
    return random_chars




if __name__ == "__main__":
    pass