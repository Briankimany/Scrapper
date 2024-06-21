
from naughty3 import save_load_program_data
from pathlib import Path
from format_link import FormatLink

def save_categorical_data(new_data , destination_path: Path):
            if destination_path.is_file():
                loded_data = save_load_program_data(path=destination_path)
            else:
                loded_data ={}
                
            for dict_key , values  in  new_data :
                if len (values) > 1:
                    if dict_key not in loded_data:
                        loded_data[dict_key] = dict(values)
                    else:
                        loded_data[dict_key].update(dict(values))
                    
            destination_path.parent.mkdir(parents= True , exist_ok=True)
            save_load_program_data(path = destination_path , data=loded_data ,mode='w') 


def verify_for_dwonload(link , l_name):
    names =['mia' , 'osa' , 'skin diamond' , 'natasha' , 'brazzers' , 'pornstar' , 'sarah-banks' , 'forced' , 'mom']
    for name in names :
        if name in l_name or name in link:
            return True
    return False

class AllScrapper:
    def __init__(self):
        pass

    def RedWap(self):
        
        def get_header_data(data , page_link = True):
            try:
                "Red wap3"
                head_data = data.find("head")
                title = data.find("title").text
                link = head_data.find("link" , rel="video_src")['href']
                return data.from_link , title if page_link else  link , title
            except Exception as e:
                return []
            
        def get_other_videos(data):
            try:
                related_videos = data.find("div" , id = "related_videos_col").find_all("a")
                # print(related_videos[0])
                links = [(data.host_link +i['href'] , i['title']) for i in related_videos]
                
                return links
            except Exception as e:
                return []

        def get_pages_2(data):
            try:
                dat =[]
                f =  data.find("div" , class_ ="trendloud")
                for i in f.find_all("a"):
                    link = data.host_link + i['href']
                    name = i.text
                    dat.append((link , name))
                return dat
            except Exception as e:
                return []
            
        def get_menu(data):
            if  data.from_link.strip("/").endswith('.com'):
                menu_id ="menul"
            else:
                menu_id ='catmenu'
                
            try:
                dat =[]
                f =  data.find("body").find('div' , id = menu_id)
                for i in f.find_all("a"):
                    link = data.host_link + i['href']
                    name = i.text
                    dat.append((link , name))
                
                return dat
                
            except Exception as e:
                return []    

        def get_links_2(data , SAVE_PATH = None):
            
            H = get_header_data(data)
            V = get_other_videos(data)
            P = get_pages_2(data)
            Q = get_menu(data)
            
            total = V + P + Q
            if len(H) > 1:
                H_dict =dict([H])
            else:
                H_dict ={}
            
            data = [["HEADERS" , [H]] ,
                    ["LISTED VIDEOS" , V],
                    ["PAGES DATA" , P],
                    ["MENU DATA" , Q]]
            save_categorical_data(new_data=data , destination_path=SAVE_PATH)
            # 
            if len(H)==2:
                if verify_for_dwonload(H[0] , H[1]):
                    link_data = get_header_data(data , page_link=False)
                    link_f = FormatLink(parent_dir=SAVE_PATH, link_data=link_data)
                    print("DOwnloadingg this link" , H)
                    link_f.download_bit_by_bit()
            
            return dict(total)  ,H_dict
        
        return get_links_2
    
    
    
if __name__ == "__main__":
    pass
        