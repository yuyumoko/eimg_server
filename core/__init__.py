from utils import logger
from typing import List, Callable
from .monitor import *
from .watch_dir import start_watch_dir
from .config import *

def start_monitor(images_path: List[str], file_handler: Callable=None):
    initialize_image_dict(images_path, file_handler=file_handler)
    start_watch_dir(images_path)
    