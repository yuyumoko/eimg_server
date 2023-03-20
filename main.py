import asyncio
from utils import logger
from core import start_monitor, get_config
from core.server import run_server

__version__ = "0.0.1"


async def run():
    start_monitor(get_config("images", "path").split())


if __name__ == "__main__":
    logger.info("欢迎使用图片查重工具 v%s" % __version__)
    asyncio.run(run())
    logger.info(
        "浏览器配套插件说明:\n"
        "tampermonkey安装: https://www.tampermonkey.net/\n"
        "tampermonkey脚本: https://greasyfork.org/scripts/434915-%E8%89%B2%E5%9B%BE%E6%9F%A5%E9%87%8D%E6%8F%92%E4%BB%B6/code/%E8%89%B2%E5%9B%BE%E6%9F%A5%E9%87%8D%E6%8F%92%E4%BB%B6.user.js"
    )
    run_server()
