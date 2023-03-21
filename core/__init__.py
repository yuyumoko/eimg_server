from utils import logger
from typing import List
from .monitor import *
from .mem_data import IMG_CACHE
from .watch_dir import start_watch_dir

def start_monitor(images_path: List[str]):
    initialize_image_dict(images_path)
    Executor.shutdown(wait=True)
    logger.info("初始化完成, 共计 %s 张图片" % len(IMG_CACHE))
    start_watch_dir(images_path)
    