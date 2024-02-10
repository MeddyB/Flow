import logging
import os
from datetime import date

LOG_FORMAT = "%(levelname)s: %(asctime)s : %(name)s - %(message)s"

def init_logging():
    current_day = (date.today()).strftime("%d%m%Y")
    
    filepath = os.environ.get("FLOW_LOG_PATH", "~\\.flw\\<current_day>_default.log")
    filepath = os.path.expanduser(filepath)
    filepath = filepath.replace("<current_day>", current_day)
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    
    logging.basicConfig(
        filename=filepath,
        filemode="a",
        format=LOG_FORMAT,
        level=logging.DEBUG,
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

