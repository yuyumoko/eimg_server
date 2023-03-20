import shutil
import platform
import requests
from pathlib import Path
from zipfile import ZipFile
from utils import logger
from .helps import *
from ..aria2c import Aria2c


async def download():
    logger.info("正在获取 [waifu2x] 最新版本...")

    base_url = (
        "https://gh-api.p3terx.com/repos/nihui/waifu2x-ncnn-vulkan/releases/latest"
    )
    latest_releases = requests.get(base_url).json()
    version = latest_releases["tag_name"]

    system = platform.system()
    if system == "Linux":
        system = "ubuntu"
    elif system == "Windows":
        system = "windows"
    elif system == "Darwin":
        system = "macos"

    asset = list(
        filter(lambda x: f"{version}-{system}" in x["name"], latest_releases["assets"])
    )[0]

    logger.info(f"正在下载 [waifu2x {version}] , 请稍等...")
    
    aria2c = Aria2c(ncnn_dir)
    dl_url = "https://hub.gitmirror.com/" + asset["browser_download_url"]
    file_name = Path(dl_url).name
    gid = aria2c.download(dl_url, file_name)

    process_bar(aria2c, gid, asset["size"])
    aria2c.close()

    logger.info("下载完成, 正在解压...")
    zip_path = ncnn_dir / file_name
    zf = ZipFile(zip_path)
    zf.extractall(ncnn_dir)
    zf.close()

    zip_path.unlink()
    shutil.move(zip_path.with_suffix(""), ncnn_dir / "waifu2x-ncnn-vulkan")

    logger.info("组件 [waifu2x] 安装成功")
