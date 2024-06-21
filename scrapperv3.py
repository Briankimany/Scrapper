
from master import  clear_console  ,  update , get_count_tracker_data
import random
import time
from timeit import default_timer as my_timer
import os , requests 
from bs4 import BeautifulSoup as soup


from time import perf_counter as my_timer 
from urllib.parse import urlparse
from pathlib import Path
from tqdm.auto import tqdm

import numpy as np
import json
import tempfile

from master import generate_random_chars , get_link_default_state , convert_duration_format , change_str_deltatime  , timedelta , get_file_size , save_load_program_data
from format_link import FormatLink




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
    

            
       
        
    
    