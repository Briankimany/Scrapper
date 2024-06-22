

from pathlib import Path
from allscrappers import Scrapper

test_dir_name = "TESTDIR"
root_dir  = Path(test_dir_name)
root_dir.mkdir(parents=True , exist_ok=True)

FULL_DATA_BASE_PATH = root_dir / "FULL_DATABASE.json"
CONTENT_LINK_TO_TOPIC = root_dir /"CONTENT_LINK_TO_TOPIC.json"
LINK_TRACKER = root_dir / "LINK_TRACKER.json"
COUNT_TRACKER = root_dir / "COUNT_TRACKER.json"
