import os
import re
import shutil
import platform
import requests
from zipfile import ZipFile
from pathlib import Path
from aria2p import Client, Stats
from utils import logger

system_bits, _ = platform.architecture()

runtime_dir = Path("./runtime").resolve()
runtime_dir.mkdir(parents=True, exist_ok=True)

aria2c_x64 = runtime_dir / "e_aria2c_64.exe"
aria2c_x32 = runtime_dir / "e_aria2c_32.exe"

aria2c_executable = aria2c_x64 if system_bits == "64bit" else aria2c_x32


def init_aria2c():
    if platform.system() == "Linux":
        raise NotImplementedError("Linux is not supported yet")

    if aria2c_executable.exists():
        return

    logger.info("未找到aria2c")
    base_aria2_url = "https://gh-api.p3terx.com/repos/aria2/aria2/releases/latest"

    logger.info("正在获取最新aria2c版本")
    latest_releases = requests.get(base_aria2_url).json()

    tag_name = latest_releases["tag_name"]
    version = re.search(r"\d+\.\d+\.\d+", tag_name).group()

    logger.info("最新版本: " + version)
    name_tag = "win" + "-" + system_bits

    download_url = list(
        filter(lambda x: name_tag in x["name"], latest_releases["assets"])
    )[0]["browser_download_url"]
    dl_url = "https://hub.gitmirror.com/" + download_url

    zip_name = Path(dl_url).name
    dl_path = runtime_dir / zip_name

    logger.info("正在下载aria2c组件")
    # 下载aria2到runtime目录
    with open(dl_path, "wb") as f:
        f.write(requests.get(dl_url).content)

    logger.info("下载完成, 正在解压")
    aria2_dir = runtime_dir / ("aria2-%s-%s" % (version, name_tag))
    zf = ZipFile(dl_path)
    zip_file_path = list(filter(lambda n: "aria2c" in n, zf.namelist()))[0]
    zf.extract(zip_file_path, path=aria2_dir)
    zf.close()

    shutil.move(aria2_dir / zip_file_path, aria2c_executable)

    shutil.rmtree(aria2_dir)
    dl_path.unlink()

    logger.info("解压完成, aria2c组件初始化完成")


class Aria2c(Client):
    def __init__(self, dir: str = None):
        init_aria2c()
        self.dir = dir
        self.__server()
        super().__init__()

    def __server(self):
        command = f"{aria2c_executable} --dir={self.dir} -c --quiet --enable-rpc=true"
        os.popen(command)

    def close(self):
        os.popen(f"taskkill /f /im {aria2c_executable}")

    def download(self, url: str, filename: str, options={}):
        options["out"] = str(filename)
        return self.add_uri([url], options=options)

    def get_stat(self):
        """
        返回Aria2服务统计信息
        downloadSpeed: 下载速度 (byte/s)
        uploadSpeed: 上传速度(byte/s)
        numActive: 活动下载任务
        numWaiting: 等待队列任务
        numStopped: 已停止的任务（不超过--max-download-result 默认限制1000）
        numStoppedTotal: 已停止的任务（可超过--max-download-result 默认限制1000）
        """
        return Stats(self.get_global_stat())
