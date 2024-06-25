

from pathlib import Path

test_dir_name = "TESTDIR"
ROOT_DIR  = Path(test_dir_name)
ROOT_DIR.mkdir(parents=True , exist_ok=True)


FULL_DATA_BASE_PATH = ROOT_DIR / "FULL_DATABASE.json"
CONTENT_LINK_TO_TOPIC = ROOT_DIR /"CONTENT_LINK_TO_TOPIC.json"
LINK_TRACKER = ROOT_DIR / "LINK_TRACKER.json"
COUNT_TRACKER = ROOT_DIR / "COUNT_TRACKER.json"
