import tempfile

from datetime import timedelta
import requests , random , time
from tqdm.auto import tqdm
import string
from datetime import datetime, timedelta
from pathlib import Path
import os
import json 

try:
    import tkinter as tk
    from tkinter import filedialog
except Exception as e:
    import tk
    from tk import  filedialog


def clear_console():
    # Clear console output based on operating system
    os.system('cls' if os.name == 'nt' else 'clear')



def read_single_file(*args):
    try:
        global root_dir
        root = tk.Tk()

        if args:
            root_dir = args[0]

        root.title("Reading single file")
        root.withdraw()
        root.configure(bg='purple')
        root.geometry('800x600')

        file_path = filedialog.askopenfilename(
            filetypes=[("All Files", "*.*")],
            initialdir=root_dir,
            title="Select file"
        )

        root.destroy()  # Close the Tkinter window and exit the program
        return file_path
    except KeyboardInterrupt:
        print("good bye")


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
    try:    
        if mode =='r':
            with open(path, 'r') as file:      
                full_data = {}
                for line in file:
                    # try:
                        loaded_json = json.loads(line)
                        full_data.update(loaded_json)
                    # except json.JSONDecodeError:
                        # print("Error decoding JSON:", line)
                        # return {}
                # print("loded data", list(full_data.items()), path)
                return full_data
        elif mode =='w':
            save_program_data(path=path , data= data)
    except KeyboardInterrupt:
        # print("Key board interupt but saving data before writing it " , data_before_error)
        pass
    except Exception as e:
        print(e)



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
            # print(link.url , link.name)
            response = requests.head(link.url)
            g =0
            redirect_link = link.url
            while int(response.status_code) == 302:
                # time.sleep(1.5)
                # print(response.status_code , link)
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
    # Parse the duration string
    try:
        hours = 0
        minutes =0
        seconds = 0
        # Extract hours, minutes, and seconds from the duration string
        if 'H' in duration_str:
            hours = int(duration_str.split('H')[0][1:])
        if 'M' in duration_str:
            minutes = int(duration_str.split('M')[0][-2:])
        if 'S' in duration_str:
            seconds = int(duration_str.split('S')[0][-2:])

        # Construct a timedelta object
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



def save_load_logs(data , mode , path):
    # Open a file in write mode
    with open(path, mode) as file:
        # Iterate through each key-value pair in the JSON object
        for key, value in data.items():
            # Convert key-value pair to JSON string
            json_str = json.dumps({key: str(value)})
            # Write JSON string to file followed by a newline character
            file.write(json_str + "\n")


def get_count_tracker_data(full_data_basev2 ,link_tracker  ,  dict_path , explored_links_count = None , content_type = "img" , relaod = False ):
    
    while True:
        if content_type == "img":
            dict_key = "num_images" 
            break
        elif content_type == "vid":
            dict_key = "num_videos"  
            break
        else:
            in_type = input(f"Invalid key {content_type} Enter right key  (1=images , 2 = videos)")
            if in_type == "1":
                content_type = "img"
            elif in_type == "2":
                content_type = "vif"
                
    
    if os.path.exists(dict_path) and not relaod and explored_links_count == None:
            count_tracker = save_load_program_data(path = 'count_tracker.json')  
            
            full_lengh_of_new_list= count_tracker['full_lengh_of_new_list']
            explored_links_count= count_tracker['explored_links_count']
            un_explored= count_tracker['un_explored']
            num_images= count_tracker[dict_key]
            
    elif explored_links_count != None and type(explored_links_count) == int :
        
        explored_links_count = explored_links_count
        full_lengh_of_new_list =  len(list(link_tracker.keys()))

        un_explored = full_lengh_of_new_list - explored_links_count
        num_images = len(list(full_data_basev2.values()))
        
        count_tracker = {
            "full_lengh_of_new_list":full_lengh_of_new_list,
            "explored_links_count" :explored_links_count,
            "un_explored":un_explored,
            dict_key:num_images     
        }  
        
        print(count_tracker , "after given the int")
          
    else:
        print("Reloading program data...")
        explored_links_count = 0
        full_lengh_of_new_list =  len(list(link_tracker.keys()))

        for i in link_tracker:
            if not link_tracker[i]:
                explored_links_count += 1

        un_explored = full_lengh_of_new_list - explored_links_count
        num_images = len(list(full_data_basev2.values()))
        
        count_tracker = {
            "full_lengh_of_new_list":full_lengh_of_new_list,
            "explored_links_count" :explored_links_count,
            "un_explored":un_explored,
            dict_key:num_images     
        }
        print(f"Starting count tracker at {count_tracker}")
        
        save_load_program_data(path = dict_path , data= count_tracker  , mode='w')
        

        return count_tracker , dict_key


def update(un_explored , explored , num_images , duration = None):
    info = "|Un explored: {} | Explored: {} | Total Num of images:{} | duration: {}|".format(un_explored , explored , num_images , duration)
    decorations = "-" * len(info)

    print(f"{decorations}\n{info}\n{decorations}\n")



def merge_class_data_base_dict(dict1 ,dict2):
    """
    Input = {link :{....}
            }
    """
    if isinstance(dict1 , Path):
        dict1 = save_load_program_data(path = dict1)
        dict2 = save_load_program_data(path=dict2)
        
    max_dict = dict1
    min_dict = dict2
    
    if len(list(dict2.keys())) > len(list(dict1.keys())) :
        max_dict = dict2
        min_dict = dict1
        
    result_dict = max_dict.copy()
    for key in min_dict:
        if key in result_dict:
            pass
        else:
            result_dict[key] = min_dict[key]
    print(len(list(dict1.keys())) , len(list(dict2.keys())) , len(list(result_dict.keys())))
    return result_dict    




if __name__ == "__main__":
    pass