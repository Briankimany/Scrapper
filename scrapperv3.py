
from cyber.scripts.common_functions import  clear_console 
import random
import time
from timeit import default_timer as my_timer
import os , requests 
from bs4 import BeautifulSoup as soup

from naughtyv2 import update , get_count_tracker_data
from time import perf_counter as my_timer 
from urllib.parse import urlparse

import numpy as np
import json
import tempfile

from master import generate_random_chars , get_link_default_state , convert_duration_format , change_str_deltatime , Path , timedelta , get_file_size , tqdm



class FormatLink:
    def __init__(self, link_data=None  , include_radom = False , parent_dir = None , in_data_base = True ,source_json = None , save_info = True) -> None:
        """
        Link data = (link , description , duration)
        """
        self.is_final_link = False
        self.in_data_base = in_data_base
        default_state = get_link_default_state()
        default_state.update(self.__dict__)
        [setattr(self , key , value) for key , value in default_state.items()]
        self.save_per_isnstance = save_info
        
        viable_ext = ['.mp4' , '.mp3']
        
        
        if link_data != None:
            data = link_data
            self.url = link_data[0] 
            if "http" not in data[0]:
                link_data = list(link_data)
                link_data[0] = data[1]
                link_data[1] = data[0]
                
       
            self.extension = f".{self.url.split('.')[-1]}"
            if self.extension in viable_ext:
                self.is_final_link = True
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
                    # print("setting name to none")
                    # raise ValueError("link name cant be none")
        

            if self.name != None:
                
                try:
                    j =self.name
                    j = j.encode().decode()
                    self.name = j
                except Exception as e:
                    pass
                
                
            ## clean the name and set the name to random chars if name was not given 
            self.name = self.name.replace("/" , "_") if self.name != None else f"Random_name_{generate_random_chars(k=4)}"
            if len(self.name.split(" ")) > 15:
                name_parts = self.name.split(" ")
                self.short_name = " ".join(name_parts[0:3]) + "..." + " ".join(name_parts[-3:])
            else:
                self.short_name = self.name 
                
            if parent_dir:
                self.parent_dir = Path(parent_dir)
                self.log_dir = (self.parent_dir /"LOGS")
            else:
                raise ValueError ("detination dir cant be none")
            # print(self.__dict__)
            # print("SLSLLSLSLLSLSL")
            self.short_name = Path(self.short_name)
            self.full_path = self.parent_dir/"CONTENT"/ self.short_name.with_suffix(self.extension)  if self.is_final_link else None
            self.json_path = self.parent_dir /"JSON DATA"/ Path(self.full_path.name).with_suffix(f'{self.extension}.json')  if self.is_final_link else None
            
            if self.is_final_link:
                self.json_path.parent.mkdir(parents= True , exist_ok=True)
                self.full_path.parent.mkdir(parents=True , exist_ok=True)
                
            if self.is_final_link:
                self.prepare_link()
            
        if source_json != None:
            saved_state = save_load_program_data(path=source_json)
            # print("Path given is " , source_json)
            default_state.update(saved_state)
            # print("data loaded is")
            for key , value in default_state.items():
                setattr(self , key , value)
            # print("state after updating" )
            if self.extension in viable_ext:
                self.is_final_link = True
            # [print(i) for i in self.__dict__.items()]
        
        
        if parent_dir:
            self.parent_dir = Path(parent_dir)
        else:
            raise ValueError ("detination dir cant be none")
        
        self.log_dir = self.parent_dir /"LOGS"
        self.short_name = Path(self.short_name)
        self.full_path = self.parent_dir/"CONTENT"/ self.short_name.with_suffix(self.extension) if self.is_final_link else None
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
        # [print(i) for i in self.__dict__.items()]
        # print("\n\n")
        self.parent_dir.mkdir(parents = True , exist_ok = True)
        if self.is_final_link:
            starting_data = self.get_state_data()
            # print("saving the current attr")
            save_load_program_data(path= self.json_path, data= starting_data , mode='w')

    
    def see(self):
        text = f"Saving to:{self.full_path}\tName:{self.name}\tLength:{self.length}\tFile size:{self.file_size}\tFinal link:{self.final_link}\n"
        decorations = "*" * len(text)
        print(f"{decorations}\n{text}\n{decorations}")
        
    
    def log(self , mesage):
        link = self
        link.log_dir.mkdir(exist_ok = True , parents = True)
        info = str(mesage)    
         
        if self.is_final_link:
            error_path = (link.log_dir/link.name).with_suffix(f".{link.extension}.json") 
        if not self.is_final_link:
                error_path =self.log_dir/self.name
                error_path = error_path.with_suffix(".json")
        
        # print(error_path)
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
            
    def download_bit_by_bit(self , target = None):
        max_time = timedelta(hours=5 , minutes=0 , seconds=60)
        url = self
        
        if self.file_size != None and not self.is_downloaded:
            try:
                # print("requestin file size for " , url.full_path , url.parent_dir)
                url.remainig_size_percentage = os.path.getsize(url.full_path)/(url.file_size*(1024*82)) if url.full_path.is_file() else 1
                # print("remaining paecetage" , url.remainig_size_percentage)
                remaining_size = url.remaining_size
                downloaded_size = int(url.hard_drive_file_size *(1024**2))
                string_1 = " ".join (url.name.split(" ")[0:3])
                string_2 = " ".join (url.name.split(" ")[-3:])
                desctription =  f"{string_1}...{string_2}"
                # print("here is remaining ",url.remainig_size_percentage)
                if  url.remainig_size_percentage > 0 and  url.remainig_size_percentage < 1:
                    # print("Cant downloadd a downloded file")
                    # print(f"Resuming download from {downloaded_size} Mb")
                    desctription = f"Resuming..{remaining_size}:" + desctription 
                    file = open(url.full_path, "ab")
                else:
                    file = open(url.full_path, "wb")
                response = requests.get(url.final_link, stream=True, headers={"Range": f"bytes={downloaded_size}-"} )
                # print(f"Here is the response {response.status_code} for {url.full_path} , size {url.file_size}")
                
                if response.status_code == 206:
                        with tqdm(total=round(url.file_size, ndigits=3)  ,desc= desctription) as progress_bar:    
                            progress_bar.update(downloaded_size/1024**2)  
                            start_time = time.time()
                            for chunk in response.iter_content(chunk_size=self.chunk_size):
                                
                                file.write(chunk)
                                file.flush()
                                self.save_currrent_state()
                                
                                progress_bar.update(round(len(chunk)/1024**2 , ndigits=3)) 
                                url.remaining_size -= len(chunk)/1024**2
                                url.hard_drive_file_size += len(chunk)/1024**2
                                url.remainig_size_percentage
                                
                                progress_bar.set_description(desctription)
                                duration = time.time() - start_time
                                
                                if timedelta(seconds=duration) > max_time:
                                    print("max time reached")
                                    break
                                
                        self.is_downloaded= True
                        file.close()
                        self.save_currrent_state()
                elif response.status_code == 416:
                    self.response = response
                    self.log(mesage=response)
                    print(response.status_code)
                    print("Cant resume download ")
                    return None
                    
                else:
                    self.log(mesage=response)
                    print("Failed to resume download new status code: Status code:", response.status_code)
                file.close()
                return None
            except Exception as e:
                print(str(e))
                self.log(str(e))
                self.save_currrent_state()
        else:
            self.log(mesage="Cant resume download")
            
        return None
    



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

    # try:
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
    # except Exception as e:
    #     print(f"Error saving/loading data: {e}")
    #     return None



def save_load_program_data(path , data=None , mode ='r'):
    # try:    
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
    # except KeyboardInterrupt:
    #     # print("Key board interupt but saving data before writing it " , data_before_error)
    #     pass
    # except Exception as e:
    #     print(e)



def save_load_program_data_v2(path ,data= None ,mode = 'r'):
    
    try:
        with open(path , mode) as file:
            
            if  'r' in mode:
                return json.load(file)
            elif data != None and  (mode == 'a' or  mode =='w'):
                json.dump(data , file)
                return None
            else:
                return None
    except Exception as e:
        print(f"Problem loading or saving data {str(e)}")
        


def get_starting_dict():
    link = input("Where to start From: ")
    code , data = make_request(link=link)
    
    try:
        topic = data.find("title").text
    except Exception as e:
        print(str(e) , "could not get the topic")
        topic = input("Enter topic: ")
    print("Giving host time to chill")
    time.sleep(3)
    return {link:topic }

def make_request(link , time_out =10):
    log_ = False
    if (isinstance (link , FormatLink)):
        link_url = link.url
        log_ = True
    elif not isinstance (link , FormatLink):
        link_url = link
    
    try:
        # print("making requests" , link_url)
        requested_info= requests.get(link_url , timeout=time_out)
        
        parsed_data = soup(requested_info.content , features= "lxml")
        parsed_data.from_link = link_url
        link_p = urlparse(link_url)
        host_link = link_p.scheme + "://"+ link_p.hostname
        parsed_data.host_link = host_link
        # print(requested_info.status_code)
        
        if int(requested_info.status_code) == 404:
            if log_:
                link.log(str(requested_info.status_code))
            print("404 ERROR ")
            return "404 ERROR " , "404 ERROR "

        return requested_info.status_code , parsed_data
    except TimeoutError as e:
        if log_:
            link.log(str(e))
        print("Timed out")
        return "TIME OUT" , "TIME OUT"
    except Exception as e:
        print(f"Error while fetching data from: {link_url} , {e}")
        if log_:
            link.log(str(e))
        return None , None

def initialize_files(full_database_path  , link_tracker_path , image_link_to_topics_path ,default_starting_links = None):
    """
    default_starting_links = {link , topic}
    
    return full_data_base , image_to_topic , link_tracker
    """
    if os.path.exists(full_database_path):
        full_database = save_load_program_data(path = full_database_path) 
    else:
        full_database = {}
    if os.path.exists(link_tracker_path):
            image_link_to_topics = save_load_program_data(path = image_link_to_topics_path , mode = 'r')
            link_tracker = save_load_program_data(path = link_tracker_path, mode = 'r')
           
    else:
        image_link_to_topics = default_starting_links
        link_tracker = {link:True for link in default_starting_links}    
        
    return full_database , image_link_to_topics , link_tracker
   

class Scrapper:
    """
    if you inherit this class redefine the method get_links
    """
    def __init__(self ,full_database_path  , link_tracker_path , image_link_to_topics_path , data_tracker_path , content = "num_images" , sleep_range = (20 , 30 , 0.3) , choose_link = None) -> None:
        
        self.full_database_path  = full_database_path 
        self.link_tracker_path = link_tracker_path 
        self.image_link_to_topics_path = image_link_to_topics_path
        self.data_tracker_path = data_tracker_path
        self.currnent_link = None
        self.content_type = content
        self.sleep_durations = list(np.arange(sleep_range[0] , sleep_range[1], step=sleep_range[2]))
        self.choose_link = choose_link
        
        if os.path.exists(link_tracker_path):
            default_starting_links = None
        else:
            default_starting_links = get_starting_dict()
            
        self.full_database , self.image_link_to_topics , self.link_tracker = initialize_files(full_database_path=self.full_database_path ,
                                                                            link_tracker_path=self.link_tracker_path,
                                                                            image_link_to_topics_path=self.image_link_to_topics_path,
                                                                            default_starting_links=default_starting_links
                                                                            )
        self.data_tracker  , self.content_type = get_count_tracker_data(
            full_data_basev2= self.full_database,
            link_tracker= self.link_tracker,
            relaod= True,
            explored_links_count=None,
            dict_path=data_tracker_path,
            content_type= content
        )
        # print("initialized self.datatracker" , self.data_tracker)
        
    
    
    def get_random_link(self):
        START_TIME = my_timer()
        link_tracker = save_load_program_data(path=self.link_tracker_path) if self.link_tracker_path.is_file() else  self.link_tracker
        data_ = list(link_tracker.items())
        
        link  , new = random.choice(data_)
        while new == False:        
            if (my_timer() - START_TIME) / 60 > 1.5:
                random.shuffle(data_)
                for link , new in list(data_):
                    print(f"taking some time to get a link{link,new} ")
                    if new:
                        link = link
                        break
                print("Looped throgh all data and found no new link")
                return None
            else:
                link  , new = random.choice(data_)
        return link

    
    def get_links(self,data):
       
        try:
            redirect_links = [tag['href'] for i , tag  in enumerate (data.find_all('a')) if "http" in tag["href"]][2:]
        except Exception as e:
            redirect_links = []
            
        try:
            redirect_profile_pics = []
            for i in data.find_all('a')[2:]:
                # print(i.find('img'))
                try:
                    img_link= i.find('img')['src']
                    if img_link.startswith('//'):
                        img_link = f"http:{img_link}"
                        redirect_profile_pics.append(img_link)
                    else:
                        print(img_link)
                except Exception as e:
                    pass
        except Exception as e:
            redirect_profile_pics =[]

        try:
            current_topic_tags = data.find('div' , id = "container").find_all('a' , class_="img-holder")
            current_images_links = [f"http:{i['href']}" for i in current_topic_tags if i['href'].startswith('//')]
        except Exception as e:
            current_images_links = []
            
        images_dict = dict([(link_ , None) for i , link_ in enumerate(redirect_profile_pics + current_images_links)])
        redirect_links_dict = dict([(link_ , i) for i , link_  in enumerate(redirect_links)])
        
        return redirect_links_dict , images_dict
        
    def merge_dicts_v2(self ,dict1 , dict2):
        similar_dict = {}
        max_dict = dict1
        min_dict = dict2
        
        if len(dict1.items()) < len(dict2.items()):
            max_dict = dict2
            min_dict= dict1
            
        results = max_dict.copy()
        similar = 0
        for link , topic in min_dict.items():
            if link in results:
                similar +=1
                if self.currnent_link not in similar_dict:
                    similar_dict[link] = 1
                
                else: 
                    similar_dict[self.currnent_link]+=1
            else:
                results[link] = topic
        if similar > 0  and similar/len(results.keys()) > 0.8 :
            print(f"merging dictsv2 , 1:{len(dict1.items())} , 2:{len(dict2.items())} , similar: {similar} Out going {len(list(results.keys()))}")
  
        return results
   
    def update(self):
        
        un_explored=self.data_tracker['un_explored'],
        explored=self.data_tracker['explored_links_count'],
        num_images=self.data_tracker[self.content_type],
        duration= self.run_time
        
        info = "Total Num of links: {} |Un explored: {} | Explored: {} | {}:{} | duration: {}|".format(len(list(self.link_tracker.keys())),un_explored , explored ,self.content_type , num_images , duration)
        decorations = "-" * len(info)

        print(f"{decorations}\n{info}\n{decorations}\n")
    
    def run(self):
        
        starting_time =  my_timer()
        self.run_time = 0
        window_time = my_timer()
        time_out_ = 10
        while True: 
                # print("start")
            # try:
                # if self.data_tracker['un_explored'] <= 0:
                #         print("done scrapping")
                #         break
              
                
                if self.choose_link != None:
                    link1 = self.choose_link()
                else:
                    link1 = self.get_random_link() 
                # print(link1)
                
                if link1 in self.image_link_to_topics:
                    name = self.image_link_to_topics[link1]
                else:
                    print("coul not fined a name")
                    name = None
                
                
                try:
                    link_2 = FormatLink(link_data=(link1 , name),
                                    parent_dir=Path(self.full_database_path).parent,
                                    in_data_base=True)
                except Exception as e:
                    print(str(e) , link1)
                    link_2 = link1
                # self.currnent_link = link1
                # print(link1 , name)
                status_code , parsed_data  = make_request(link=link_2 , time_out=time_out_)
                   
                if isinstance(status_code , str) :
                    self.link_tracker[link1] = False
                    print("SKipped this ;link dou to tim out")
                    self.data_tracker['explored_links_count']  +=1
                    self.data_tracker['un_explored'] = len(self.link_tracker.keys()) - self.data_tracker['explored_links_count']
                    
                    save_load_program_data(path = self.data_tracker_path , data = self.data_tracker  , mode= "w")
                    save_load_program_data(path = self.link_tracker_path , data = self.link_tracker, mode = 'w')
                    continue
                    


                # print(self.link_tracker)
                if link1 == None:
                    print("Got No link infering that all links have been explored")
                    break
                
                elif status_code == None:
                     print("status code erro" , status_code , link1)
                     time.sleep(30)
                     continue
                 
                if int(status_code) == 200:
                    # print("seting to false")
                    self.link_tracker[link1] = False
                
                
                
                if int(status_code) > 400:
                    time.sleep(300)
                    continue
                
                if "http" not in link1:
                    self.link_tracker[link1] = False
                    
                    self.data_tracker['explored_links_count']  +=1
                    self.data_tracker['un_explored'] = len(self.link_tracker.keys()) - self.data_tracker['explored_links_count']
                    
                    save_load_program_data(path = self.data_tracker_path , data = self.data_tracker  , mode= "w")
                    save_load_program_data(path = self.link_tracker_path , data = self.link_tracker, mode = 'w')
                    
                    update(un_explored=self.data_tracker['un_explored'],
                    explored=self.data_tracker['explored_links_count'],
                    num_images=self.data_tracker[self.content_type],
                    duration= run_time
                    )
                    
                    if self.data_tracker['un_explored'] <= 0:
                        print("done scrapping")
                        break
                    

                if status_code == None:
                    time.sleep(2)
                    continue
                
                self.link_tracker[link1] = False
                print(f"status code {status_code}")
                
                redirect_links_dict , images_dict = self.get_links(data=parsed_data)
                available_links = {link :True for link in redirect_links_dict.keys()}
                
                print(f"redirect links from scrapping :{len(redirect_links_dict.keys())}||{' '.join(self.content_type.split('_'))} from scrapping {len(images_dict.keys())}")
               
                 
                self.image_link_to_topics = self.merge_dicts_v2(self.image_link_to_topics , redirect_links_dict)
                self.link_tracker = self.merge_dicts_v2(available_links , self.link_tracker)
                self.full_database = self.merge_dicts_v2(self.full_database , images_dict)
                
                self.data_tracker['explored_links_count']  +=1
                self.data_tracker[self.content_type] = len(list(self.full_database.keys()))
                self.data_tracker['un_explored'] = len(self.link_tracker.keys()) - self.data_tracker['explored_links_count']
                
                save_load_program_data(path = self.full_database_path , data = self.full_database , mode='w')
                save_load_program_data(path = self.image_link_to_topics_path , data = self.image_link_to_topics , mode = "w")
                save_load_program_data(path = self.link_tracker_path , data = self.link_tracker, mode = 'w')
                save_load_program_data(path = self.data_tracker_path , data = self.data_tracker  , mode= "w")    
                  
                self.update()
                 
                if self.data_tracker['un_explored'] <= 0:
                    print("done scrapping")
                    break
                
                current_sleep_duration = round(random.choice(self.sleep_durations) , ndigits=2)
                # print(f"Slepping {current_sleep_duration} S\n")
                time.sleep(current_sleep_duration)
                
                run_time = (my_timer() - starting_time)
                
                hours = run_time//3600
                minutes = (run_time - hours * 3600)//60
                seconds = run_time - (hours * 3600 + minutes * 60)

                self.run_time = "{} hrs : {}M : {} S".format(hours ,minutes ,round(number= seconds ,ndigits=2) )
                
                if (my_timer()- window_time)/60 >=10:
                    clear_console()
                    window_time = my_timer()
                    
                
                    
            # except Exception as e:
            #     print(f"\n{str(e)}\n")
            #     time.sleep(120)
            #     pass                
            
   
    
if __name__ == "__main__":
    source_dir = Path("Version3")
    source_dir.mkdir(parents= True , exist_ok=True)
    
    full_databse_path = source_dir /"full_database_v3.json"
    link_tracker_path = source_dir/"link_tracker_v3.json" 
    image_link_to_topics_path  = source_dir/"images_links_to_topis.json"
    data_tracker_path=source_dir/"count_tracker_v3.json"
    
    scrapper = Scrapper(full_database_path=full_databse_path ,
                         link_tracker_path=link_tracker_path,
                         image_link_to_topics_path=image_link_to_topics_path,
                         data_tracker_path= data_tracker_path
                         )
    
    scrapper.run()
    

            
       
        
    
    