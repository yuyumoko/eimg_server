import imghdr
import shutil
from pathlib import Path
from PIL import Image
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
)
from utils import logger, retry_log
from .config import getboolean_config, get_config, items_config


def test_jpeg(h, f):
    # https://bugs.python.org/issue28591
    """JPEG data in JFIF or Exif format"""
    if h[:2] == b"\xff\xd8":
        return "jpeg"


imghdr.tests.append(test_jpeg)

pass_suffix = get_config("auto-file-name-setting", "pass_suffix").split()
no_convert_type = get_config("auto-file-name-setting", "no_convert_type").split()

suffix = dict(items_config("auto-file-name-suffix"))


@retry(stop=stop_after_attempt(20), wait=wait_fixed(3), before=retry_log, reraise=True)
def auto_file_name(file: Path, md5: str):
    # 是否启用自动重命名
    if not getboolean_config("global", "enable_auto_file_name"):
        return

    file_type = file.suffix[1:]
    # 是否跳过该文件类型
    if file_type in pass_suffix:
        return

    # 获取图片真实后缀
    what_type = imghdr.what(file)
    if not what_type:
        what_type = file_type

    # 文件名是否与MD5相同并且后缀是否正确
    if file.stem == md5 and suffix.get(what_type) == file.suffix[1:]:
        return

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
