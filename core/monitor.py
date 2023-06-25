import re
import threading
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List

from progress.bar import IncrementalBar
from tenacity import retry, stop_after_attempt, wait_fixed

from utils import *

from .config import get_config
from .mem_data import IMG_DATA, ImgDB


class InitBar(IncrementalBar):
    suffix_msg = ""
    suffix = "%(percent).2f%% %(index)d/%(max)d %(suffix_msg)s"


Cache_md5_db = {}

suffix_allow = get_config("global", "suffix_allow").split()


@retry(stop=stop_after_attempt(20), wait=wait_fixed(3), before=retry_log, reraise=True)
def get_img_md5(file: Path, print_log=True):
    file_name = file.stem
    if len(file_name) > 32 or not re.findall(r"([a-fA-F\d]{32})", file_name):
        cache_key = str2md5(file)
        cache_md5_info = Cache_md5_db.get(cache_key)
        if cache_md5_info:
            print_log and logger.info("使用缓存..")
            file_name = cache_md5_info
        else:
            print_log and logger.info("生成MD5...")
            with open(file, "rb") as fp:
                file_name = md5(fp.read())

            Cache_md5_db[cache_key] = file_name
    return file_name


def image_set_cache_md5(file: Path, bar: InitBar, md5_filename: bool, set_md5=None):
    if md5_filename:
        md5 = file.stem.lower()
    elif set_md5:
        md5 = set_md5
    else:
        md5 = get_img_md5(file, False)

    thread_name = threading.current_thread().getName()
    bar.suffix_msg = f"{thread_name}_{md5}"
    bar.next()
    return ImgDB.new_data(md5, file)


Executor = ThreadPoolExecutor(
    max_workers=int(get_config("global", "init_thread_num")), thread_name_prefix="T"
)

DirectoryInfo = namedtuple("DirectoryInfo", ["path", "mtime"])


# @fn_use_info
def initialize_image_dict(
    images_path: List[str],
    original_name=False,
    file_handler: Callable = None,
    DB: ImgDB = None,
):
    if not DB:
        raise ValueError("数据库初始化失败")

    for index, img_dir in enumerate(images_path):
        directory_info_db = DB.table("directory_info")

        # 判断文件夹的修改时间 是否和上一次不一样, 才去重新载入词典
        dir_key = DB.new_dir_key(img_dir)
        di_db = directory_info_db.get(dir_key)
        if di_db:
            di_db = DirectoryInfo(**di_db)

        mtime = os.path.getmtime(img_dir)
        # 如果时间没变过 那直接载入之前的数据
        if di_db and di_db.mtime == mtime:
            continue

        di_db = DirectoryInfo(path=str(img_dir), mtime=mtime)

        file_list_len = len(os.listdir(img_dir))

        bar = None

        img_dir = (img_dir, Path(img_dir))[isinstance(img_dir, str)]

        futures = []
        for file in img_dir.iterdir():
            if file.is_dir():
                initialize_image_dict([file], original_name, file_handler, DB)
                continue
            if file.suffix[1:] not in suffix_allow:
                # 如果不是允许的后缀名则跳过
                continue
            if not bar:
                bar = InitBar(
                    "生成词典[%s/%s]" % (index + 1, len(images_path)), max=file_list_len
                )

            set_md5 = None
            if file_handler:
                file, set_md5 = file_handler(file)
            futures.append(
                Executor.submit(image_set_cache_md5, file, bar, original_name, set_md5)
            )

        if bar:
            bar.goto(file_list_len)
            bar.finish()

        dir_img_db = DB.table(dir_key)
        current_hash = []
        bar = InitBar("保存数据", max=len(futures))
        for x in as_completed(futures):
            img_data: IMG_DATA = x.result()
            current_hash.append(img_data.hash)

            bar.suffix_msg = f"{img_data.hash}"
            bar.next()
            if not DB.is_mem_db:
                data_img: IMG_DATA = dir_img_db.get(img_data.hash)
                if data_img:
                    data_img = IMG_DATA(**data_img)

                if data_img and img_data.mtime == data_img.mtime:
                    continue

            dir_img_db[img_data.hash] = img_data.dict()
            DB.set(img_data.hash, dir_key)

        directory_info_db[dir_key] = di_db._asdict()

        # 处理被删除的数据
        db_hash_list = dir_img_db.keys()
        for hash in db_hash_list:
            if hash not in current_hash:
                dir_img_db.pop(hash)
                DB.db.pop(hash)

        # 保存数据库
        DB.save_table_and_close(dir_img_db)
        DB.save_table_and_close(directory_info_db)

        bar.goto(len(futures))
        bar.finish()
