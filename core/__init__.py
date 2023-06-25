from typing import Callable, List

from utils import logger

from .config import *
from .monitor import *
from .watch_dir import start_watch_dir


def start_monitor(
    images_path: List[str], 
    watch_path: List[str],
    file_handler: Callable = None, 
    DB: ImgDB = None
):
    initialize_image_dict(images_path, file_handler=file_handler, DB=DB)
    start_watch_dir(watch_path)
