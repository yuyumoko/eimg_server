import re
import threading
from typing import List
from progress.bar import IncrementalBar
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
)
from .config import get_config
from utils import *
from .mem_data import update_image_cache


class InitBar(IncrementalBar):
    suffix_msg = ""
    suffix = "%(percent).2f%% %(index)d/%(max)d %(suffix_msg)s"


Executor = ThreadPoolExecutor(
    max_workers=int(get_config("global", "init_thread_num")), thread_name_prefix="T"
)


Cache_md5_db = connect_db(tablename="cache_md5")
Modify_time_db = connect_db(tablename="modify_time")

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


def image_set_cache_md5(file: Path, bar: InitBar, md5_filename: bool):
    if md5_filename:
        md5 = file.stem.lower()
    else:
        md5 = get_img_md5(file, False)
    thread_name = threading.current_thread().getName()
    bar.suffix_msg = f"{thread_name}_{md5}"
    bar.next()
    return {md5: {"file": str(file)}}


@fn_use_info
def initialize_image_dict(images_path: List[str], original_name=False):
    for index, img_dir in enumerate(images_path):
        # 判断文件夹的修改时间 是否和上一次不一样, 才去重新载入词典
        modify_time_key = str2md5(img_dir)
        mt_info = Modify_time_db.get(modify_time_key)
        mtime = os.path.getmtime(img_dir)

        data = {}
        # 如果时间没变过 那直接载入之前的数据
        if mt_info and mt_info == mtime:
            data = read_json_file(modify_time_key)
            if data:
                update_image_cache(data)
                continue

        file_list_len = len(os.listdir(img_dir))
        bar = InitBar("生成词典[%s/%s]" % (index + 1, len(images_path)), max=file_list_len)

        img_dir = (img_dir, Path(img_dir))[isinstance(img_dir, str)]

        futures = []
        for file in img_dir.iterdir():
            if file.is_dir():
                initialize_image_dict([file], original_name)
                continue
            if file.suffix[1:] not in suffix_allow:
                # 如果不是允许的后缀名则跳过
                continue
            futures.append(
                Executor.submit(image_set_cache_md5, file, bar, original_name)
            )

        for x in as_completed(futures):
            data.update(x.result())

        bar.goto(file_list_len)
        bar.finish()

        # 写入缓存
        Modify_time_db[modify_time_key] = mtime
        write_json_file(modify_time_key, data)

        update_image_cache(data)
