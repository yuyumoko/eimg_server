from pathlib import Path
from utils import logger, runCommand

def handler_process(line, line_num):
    logger.info(line)


def convert_image(image_path: Path, scale, vulkan, output):
    logger.info(f" -> 正在使用 [waifu2x] 进行超分辨率处理: {image_path.name}")
    # output = output.with_stem(output.stem + "_x" + str(scale))
    cli_args = [
        str(vulkan),
        "-i",
        str(image_path),
        "-o",
        str(output),
        "-s",
        str(scale),
        "-n",
        "0",
        "-x",
        # "-v"
    ]
    runCommand(cli_args, handler_process)
    logger.info(" -> 超分辨率处理完成")
