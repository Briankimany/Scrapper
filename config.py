

from pathlib import Path
from allscrappers import Scrapper

test_dir_name = "TESTDIR"
ROOT_DIR  = Path(test_dir_name)
ROOT_DIR.mkdir(parents=True , exist_ok=True)


FULL_DATA_BASE_PATH = ROOT_DIR / '.TRACKING DATA' /"FULL_DATABASE.json"
CONTENT_LINK_TO_TOPIC = ROOT_DIR / '.TRACKING DATA' /"CONTENT_LINK_TO_TOPIC.json"
LINK_TRACKER = ROOT_DIR / '.TRACKING DATA' /"LINK_TRACKER.json"
COUNT_TRACKER = ROOT_DIR / '.TRACKING DATA' /"COUNT_TRACKER.json"

if FULL_DATA_BASE_PATH.parent.exists():
    FULL_DATA_BASE_PATH.parent = FULL_DATA_BASE_PATH
FULL_DATA_BASE_PATH.parent.mkdir(parents= True , exist_ok= True)
