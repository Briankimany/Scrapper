

from pathlib import Path
from allscrappers import Scrapper

test_dir_name = "TESTDIR"
ROOT_DIR  = Path(test_dir_name)
ROOT_DIR.mkdir(parents=True , exist_ok=True)

TRACKING_DATA_fOLDER = ROOT_DIR /'. TRACKING DATA'
FULL_DATA_BASE_PATH = TRACKING_DATA_fOLDER /"FULL_DATABASE.json"
CONTENT_LINK_TO_TOPIC = TRACKING_DATA_fOLDER /"CONTENT_LINK_TO_TOPIC.json"
LINK_TRACKER = ROOT_DIR /TRACKING_DATA_fOLDER/"LINK_TRACKER.json"
COUNT_TRACKER = ROOT_DIR/ TRACKING_DATA_fOLDER /"COUNT_TRACKER.json"
DB_DICT = TRACKING_DATA_fOLDER /'DB.json'

CONTENT_LOCATION = ROOT_DIR/"CONTENT"
JSON_DATA_LOCATION = CONTENT_LOCATION/"JSON DATA"

CHUNK_SIZE = (1024**2) * 3
BATCH_SIZE = 10
MUX_NUM = 200

FULL_DATA_BASE_PATH.parent.mkdir(parents= True , exist_ok= True)

print("Her is __nae__" , __name__)