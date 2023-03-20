import asyncio
from pathlib import Path
from importlib import import_module
from utils import logger
from ..config import get_config

default_ncnn = get_config("ncnn", "default")


def download_vulkan(name):
    logger.info("正在下载超分辨率 [%s] 组件, 请稍等..." % name)

    asyncio.gather(import_module(f".dl_{name}", __package__).download())


def get_ncnn(ncnn_name):
    vulkan = get_config(ncnn_name, "vulkan")
    params = get_config(ncnn_name, "params")
    return Path(vulkan).resolve(), params


def init_ncnn(ncnn_name=default_ncnn):
    vulkan, params = get_ncnn(ncnn_name)

    if not vulkan.exists():
        download_vulkan(ncnn_name)
    else:
        logger.info("超分辨率 [%s] 已启用" % ncnn_name)