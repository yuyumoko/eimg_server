import imghdr
import shutil
from pathlib import Path

from PIL import Image
from tenacity import retry, stop_after_attempt, wait_fixed

from utils import is_md5, logger, retry_log

from .config import get_config, getboolean_config, items_config
from .iwara import iwara_file_handler


def test_jpeg(h, f):
    # https://bugs.python.org/issue28591
    """JPEG data in JFIF or Exif format"""
    if h[:2] == b"\xff\xd8":
        return "jpeg"


imghdr.tests.append(test_jpeg)

pass_suffix = get_config("auto-file-name-setting", "pass_suffix").split()
no_convert_type = get_config("auto-file-name-setting", "no_convert_type").split()

suffix = dict(items_config("auto-file-name-suffix"))

image_auto_file_name = getboolean_config("images", "enable_auto_file_name")
image_path_list = get_config("images", "path").split()
image_path_list = [Path(i) for i in image_path_list]

iwara_auto_file_name = getboolean_config("iwara", "enable_auto_file_name")
iwara_path_list = get_config("iwara", "path").split()
iwara_path_list = [Path(i) for i in iwara_path_list]



def check_file_need_rename(file: Path):
    parent = file.parent
    # drive = Path(file.drive)
    
    if all([image_auto_file_name, iwara_auto_file_name]):
        return True, None
    
    if not image_auto_file_name:
        while parent != parent.parent:
            if parent in image_path_list:
                return False
            parent = parent.parent
            
    if not iwara_auto_file_name:
        while parent != parent.parent:
            if parent in iwara_path_list:
                _, video_id = iwara_file_handler(file)
                return False, video_id
            parent = parent.parent
    
    return True, None

@retry(stop=stop_after_attempt(20), wait=wait_fixed(3), before=retry_log, reraise=True)
def auto_file_name(file: Path, md5: str):
    # 是否启用自动重命名
    # if not check_file_need_rename(file):
    #     return

    file_type = file.suffix[1:]
    # 是否跳过该文件类型
    if file_type in pass_suffix:
        return file

    # 获取图片真实后缀
    what_type = imghdr.what(file)
    if not what_type:
        what_type = file_type

    if not suffix.get(what_type) and file_type and is_md5(file.stem):
        return file
    
    # 文件名是否与MD5相同并且后缀是否正确
    if file.stem == md5 and suffix.get(what_type) == file_type:
        return file

    # 设置新的文件名
    new_file = file.with_name(md5 + file.suffix)

    # 判断是否设置新的后缀
    if (suffix.get(what_type) or what_type) != file.suffix[1:]:
        new_suffix = "." + (suffix.get(what_type) or what_type)
        new_file = new_file.with_suffix(new_suffix)

        if new_file.suffix[1:] not in no_convert_type:
            # 转换图片类型
            im = Image.open(file)
            im.load()
            if (suffix.get(what_type) or what_type) in ["png", "webp"]:
                colour = "RGBA"
            else:
                colour = "RGB"
            icc_profile = im.info.get("icc_profile", "")
            im.convert(colour).save(new_file, icc_profile=icc_profile, quality=100)

            im.close()
            Path(file).unlink(missing_ok=True)
            logger.info("自动转换: %s -> %s" % (file, new_file))
            return

    # 不需要转换的直接重命名文件
    shutil.move(str(file), str(new_file))
    logger.info("自动重命名: %s -> %s" % (file, new_file))
    return new_file