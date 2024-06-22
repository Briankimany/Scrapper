

import numpy as np
from allscrappers import Scrapper
import config
import links_extractor


if __name__ == "__main__":
        test = Scrapper(full_database_path=config.FULL_DATA_BASE_PATH , link_tracker_path=config.LINK_TRACKER ,
                        image_link_to_topics_path=config.CONTENT_LINK_TO_TOPIC ,data_tracker_path=config.COUNT_TRACKER , link_extractor=links_extractor.fmovies)
            

        test.run()
        
    
    