
from scrapperv3 import Path , Scrapper



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