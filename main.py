import asyncio
import sys

from core import get_config, getboolean_config, start_monitor
from core.aria2c import check_proxy
from core.iwara import iwara_file_handler
from core.mem_data import ImgDB
from core.server import run_server
from utils import logger

__version__ = "0.0.6"

aria2c_enable = getboolean_config("global", "aria2c_enable")
aria2c_proxy = get_config("global", "aria2c_proxy")


async def run():
    logger.info("正在初始化, 请稍等...")

    if aria2c_proxy and not sys.gettrace():
        logger.info("使用aria2c代理")
        check_proxy(aria2c_proxy)
        logger.info("aria2c检测代理通过")

    with ImgDB() as DB:
        images_path = get_config("images", "path").split()
        images_watch_path = get_config("images", "watch_path").split()
        start_monitor(images_path, images_watch_path, DB=DB)

        iwara_path = get_config("iwara", "path").split()
        iwara_watch_path = get_config("iwara", "watch_path").split()
        start_monitor(
            iwara_path, iwara_watch_path, file_handler=iwara_file_handler, DB=DB
        )

        if DB.is_mem_db:
            logger.info("正在保存数据库...")
            DB.save_mem_db()

        logger.info("初始化完成, 共计 %s 个词典" % len(DB.db))


if __name__ == "__main__":
    logger.info("欢迎使用图片查重工具 v%s" % __version__)
    asyncio.run(run())
    logger.info(
        "浏览器配套插件说明:\n"
        "tampermonkey安装: https://www.tampermonkey.net/\n"
        "tampermonkey脚本: https://greasyfork.org/scripts/434915-%E8%89%B2%E5%9B%BE%E6%9F%A5%E9%87%8D%E6%8F%92%E4%BB%B6/code/%E8%89%B2%E5%9B%BE%E6%9F%A5%E9%87%8D%E6%8F%92%E4%BB%B6.user.js\n"
        "iwara增强脚本: https://sleazyfork.org/scripts/422239-iwara-download-tool/code/Iwara%20Download%20Tool.user.js"
    )
    run_server()
