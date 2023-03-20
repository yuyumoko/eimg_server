
from pathlib import Path
from time import monotonic
from progress.bar import IncrementalBar
from utils import size_format
from ..aria2c import Aria2c

ncnn_dir = Path("./ncnn").resolve()
ncnn_dir.mkdir(parents=True, exist_ok=True)


class InitBar(IncrementalBar):
    suffix_msg = ""
    suffix = "%(percent).2f%% %(index)d/%(max)d %(suffix_msg)s"

    def next(self, n=1):
        now = monotonic()
        dt = now - self._ts
        self.update_avg(n, dt)
        self._ts = now
        self.update()


def process_bar(aria2c: Aria2c, gid, file_size):
    bar = InitBar("下载进度")
    file_size_str = size_format(file_size)

    while True:
        dl_info = aria2c.get_files(gid)[0]
        stat = aria2c.get_stat()
        bar.max = int(dl_info["length"])
        bar.index = int(dl_info["completedLength"])
        bar.suffix_msg = "文件大小: %s  速度: %s" % (
            file_size_str,
            size_format(stat.download_speed),
        )
        bar.next()
        # asyncio.gather(asyncio.sleep(0.5))
        if bar.max == bar.index and bar.max != 0:
            break
    bar.finish()
