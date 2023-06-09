from PIL import Image
from pathlib import Path
from urllib.parse import urlparse
from time import monotonic
from progress.bar import IncrementalBar
from utils import size_format, logger, file_size_str,  get_folder_size
from ..aria2c import Aria2c

ncnn_dir = Path("./ncnn").resolve()
ncnn_dir.mkdir(parents=True, exist_ok=True)

cache_dir = Path("./cache").resolve()

ncnn_temp_dir = cache_dir / "ncnn/temp"
ncnn_result_dir = cache_dir / "ncnn/result"

ncnn_temp_dir.mkdir(parents=True, exist_ok=True)
ncnn_result_dir.mkdir(parents=True, exist_ok=True)

Image.MAX_IMAGE_PIXELS = 3000000000

def clear_cache():
    for file in ncnn_temp_dir.iterdir():
        file.unlink()
    for file in ncnn_result_dir.iterdir():
        file.unlink()

# clear_cache()

class InitBar(IncrementalBar):
    suffix_msg = ""
    suffix = "%(percent).2f%% %(index)d/%(max)d %(suffix_msg)s"

    def next(self, n=1):
        now = monotonic()
        dt = now - self._ts
        self.update_avg(n, dt)
        self._ts = now
        self.update()


def process_bar(aria2c: Aria2c, gid, file_size=None):
    bar = InitBar("下载进度")
    file_size_str = size_format(file_size) if file_size else None

    while True:
        dl_info = aria2c.get_files(gid)[0]
        stat = aria2c.get_stat()
        bar.max = int(dl_info["length"])
        bar.index = int(dl_info["completedLength"])
        
        
        if file_size_str is None:
            file_size_str = size_format(int(dl_info["length"]))

        bar.suffix_msg = "文件大小: %s  速度: %s" % (
            file_size_str,
            size_format(stat.download_speed),
        )
        bar.next()
        # asyncio.gather(asyncio.sleep(0.5))
        if bar.max == bar.index and bar.max != 0:
            break
    bar.finish()


def download_image2temp(image_url, force=False):
    if get_folder_size(ncnn_result_dir) > 104857600 * 3: # 缓存文件夹大于300M时清空
        logger.info("缓存文件夹大于300M，正在清空")
        clear_cache()
    
    file_name = Path(urlparse(image_url).path).name
    temp_image_path = ncnn_temp_dir / file_name
    if temp_image_path.exists() and not force:
        return temp_image_path
    
    logger.info(" - 正在下载图片 : %s" % file_name)
    aria2c = Aria2c(ncnn_temp_dir)
    
    gid = aria2c.download(image_url, file_name)
    process_bar(aria2c, gid)
    logger.info(" - 图片下载完成 : %s" % file_name)
    return temp_image_path


def get_image_info(image_path): # 获取图片信息
    image = Image.open(image_path)
    return image.width, image.height, image.format, file_size_str(image_path)
    