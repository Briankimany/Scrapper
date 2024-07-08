import os  
from pathlib import Path
from tqdm.auto import tqdm
from datetime import timedelta

from master import convert_duration_format , generate_random_chars , get_file_size , change_str_deltatime , save_load_program_data , get_link_default_state
from download_2 import download_bit_by_bit , download_files



    
class FormatLink:
    def __init__(self, link_data=None  , include_radom = False , parent_dir = None , in_data_base = True ,source_json = None , save_info = True , chunk_size = (1024**2)*3 , is_verified_final_link = False) -> None:
        """
        Link data = (link , description , duration)
        """
        self.is_final_link = False
        self.in_data_base = in_data_base
        self.save_per_isnstance = save_info
        
        default_state = get_link_default_state()
        default_state.update(self.__dict__)
        [setattr(self , key , value) for key , value in default_state.items()]
   
        
        viable_ext = ['.mp4' , '.mp3' , '.zip' , '.mkv' , '.nfo' , '.url' , '.iso' , '.torrent' , '.bin' , '.exe' , '.url' , '.bat', '.jpg' , '.jpeg']
        
        
        
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
                
                
            ## clean the name and set the name to random chars if name was not given 
            self.name = self.name.replace("/" , "_") if self.name != None else f"Random_name_{generate_random_chars(k=4)}"
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
            self.short_name = str(self.short_name)
            
            if self.is_final_link:
                self.json_path.parent.mkdir(parents= True , exist_ok=True)
                self.full_path.parent.mkdir(parents=True , exist_ok=True)
                
            if self.is_final_link:
                if chunk_size != None:
                    self.chunk_size = chunk_size
                
                if self.json_path.exists() and self.json_path.is_file():
                    self.load_state_from_file(source_json= self.json_path , chunk_size=chunk_size , viable_ext=viable_ext , 
                                      in_data_base=in_data_base , default_state=default_state)
                else:
                    self.prepare_link()
            
        if source_json != None:
            self.load_state_from_file(source_json= source_json , chunk_size=chunk_size , viable_ext=viable_ext , 
                                      in_data_base=in_data_base , default_state=default_state)
        
          

        if parent_dir:
            self.parent_dir = Path(parent_dir)
        else:
            raise ValueError ("detination dir cant be none")
        
        self.log_dir = self.parent_dir /"LOGS"
        self.short_name = Path(self.short_name)
        self.full_path = self.parent_dir/ self.short_name.with_suffix(self.extension) if self.is_final_link else None
        self.json_path = self.parent_dir /"JSON DATA"/ Path(self.full_path.name).with_suffix(f'{self.extension}.json') if self.is_final_link else None
        self.short_name = str(self.short_name)
        
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

    
    def load_state_from_file(self , source_json , default_state , chunk_size , viable_ext , in_data_base):
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
            return self
    
    
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
                value = value.absolute()
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
            # print(f"Resuming download from : {self.hard_drive_file_size}")
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
            
    def delete(self , all = False):
        if self.remainig_size_percentage == 0:
            os.remove(self.json_path) if self.json_path.exists() else None
            if all and self.full_path.exists():
                os.remove(self.full_path)
            



        
        
    

    