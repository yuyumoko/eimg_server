import asyncio
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from utils import logger, str2md5

from .config import get_config
from .image_detect import auto_file_name, check_file_need_rename
from .mem_data import ImgDB
from .monitor import get_img_md5

suffix_allow = get_config("global", "suffix_allow").split()


class image_watch_handler(FileSystemEventHandler):
    def on_created(self, event):
        _file = Path(event.src_path)
        if _file.suffix[1:] not in suffix_allow:
            return

        async def run_async(file: Path):
            need_rename, file_name = check_file_need_rename(file)
            try:
                if need_rename and file_name is None:
                    file_name = get_img_md5(file)
            except Exception as e:
                logger.error("生成MD5失败了, 很可能是找不到文件, 请重新保存\n文件: %s" % file)
                return
            if file.exists():
                if need_rename:
                    file = auto_file_name(file, file_name)
                
                with ImgDB() as DB:
                    DB.set_data(file_name, file)
                    
                logger.info("(%s)添加成功 文件:\n%s" % (file_name, file))

        asyncio.run(run_async(_file))
        
    # def on_deleted(self, event):
    #     file = Path(event.src_path)
    #     if file.suffix[1:] not in suffix_allow:
    #         return
        
    #     async def run_async():
    #         with ImgDB() as DB:
    #             DB.del_data(get_img_md5(file))
        
    #     asyncio.run(run_async())

def start_watch_dir(images_path):
    event_handler = image_watch_handler()
    observer = Observer()
    for img_dir in images_path:
        logger.info("监视目录: %s" % img_dir)
        observer.schedule(event_handler, img_dir, recursive=True)
    observer.start()

    
