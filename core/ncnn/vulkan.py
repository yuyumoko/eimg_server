import asyncio
from threading import Thread
from pathlib import Path
from urllib.parse import urlparse
from importlib import import_module
from utils import logger, str2md5
from ..config import get_config, getboolean_config
from .helps import download_image2temp, ncnn_result_dir

Enable = getboolean_config("ncnn", "enable")


def download_vulkan(name):
    logger.info("正在下载超分辨率 [%s] 组件" % name)
    import_module(f".dl_{name}", __package__).download()


def get_ncnn(ncnn_name):
    vulkan = get_config(ncnn_name, "vulkan")
    return Path(vulkan).resolve()


init_ncnn_ok = {}


def init_ncnn(ncnn_name):
    if not Enable:
        logger.info("+ 超分辨率组件已禁用")
        return
    if not ncnn_name:
        raise ValueError("未指定超分辨率组件, 请在config.ini中配置ncnn -> default")

    if init_ncnn_ok.get(ncnn_name, False):
        return

    vulkan = get_ncnn(ncnn_name)

    if not vulkan.exists():
        download_vulkan(ncnn_name)
    else:
        logger.info("+ 超分辨率 [%s] 已启用" % ncnn_name)
        init_ncnn_ok[ncnn_name] = True


def convert_image(image_path, scale, ncnn_name=None):
    if ncnn_name is None:
        ncnn_name = get_config("ncnn", "default")

    if not Enable:
        return None
    if not ncnn_name:
        raise ValueError("未指定超分辨率组件, 请在config.ini中配置ncnn -> default")

    vulkan = get_ncnn(ncnn_name)
    output = ncnn_result_dir / image_path.name
    if output.exists():
        output.unlink()

    return import_module(f".ncnn_{ncnn_name}", __package__).convert_image(
        image_path, scale, vulkan, output
    )


def convert_image_from_url(image_url, scale, ncnn_name=None):
    init_ncnn(ncnn_name)
    image_path = download_image2temp(image_url)
    return convert_image(image_path, scale, ncnn_name)


def create_convert_image_from_url_task(image_url, scale, ncnn_name=None):
    file = Path(urlparse(image_url).path)
    file_name = file.name
    if file.suffix in [".mp4", ".webm", ".m4v", ".gif"]:
        return file_name, None, None, False
    task_id = str2md5(file_name)
    t = Thread(
        target=convert_image_from_url, args=(image_url, scale, ncnn_name), name=task_id
    )
    # t.setDaemon(True)
    t.start()

    return file_name, task_id, t, True
