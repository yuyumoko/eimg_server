import shutil
import platform
import requests
from pathlib import Path
from zipfile import ZipFile
from utils import logger
from .helps import *
from ..aria2c import Aria2c


def download():
    logger.info(" - 正在获取 [realcugan] 最新版本")
    base_url = "https://gh-api.p3terx.com/repos/nihui/realcugan-ncnn-vulkan/releases"
    releases = requests.get(base_url).json()

    system = platform.system()
    if system == "Linux":
        system = "ubuntu"
    elif system == "Windows":
        system = "windows"
    elif system == "Darwin":
        system = "macos"

    for release in releases:
        assets = release["assets"]
        if not assets:
            continue
        else:
            version = release["tag_name"]
            asset = list(filter(lambda x: system in x["name"], assets))[0]
            break

    logger.info(f" - 正在下载 [realcugan {version}]")

    aria2c = Aria2c(ncnn_dir)
    dl_url = "https://hub.gitmirror.com/" + asset["browser_download_url"]
    file_name = Path(dl_url).name
    gid = aria2c.download(dl_url, file_name)

    process_bar(aria2c, gid, asset["size"])

    logger.info(" - 下载完成, 正在解压")
    zip_path = ncnn_dir / file_name
    zf = ZipFile(zip_path)
    zf.extractall(ncnn_dir)
    zf.close()

    zip_path.unlink()
    shutil.move(zip_path.with_suffix(""), ncnn_dir / "realcugan-ncnn-vulkan")
    
    logger.info(" - 组件 [realcugan] 安装成功")
