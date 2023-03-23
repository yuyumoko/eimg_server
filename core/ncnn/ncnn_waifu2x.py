from pathlib import Path
from utils import logger, runCommand
from .helps import ncnn_result_dir


def convert_image(image_path: Path, scale, vulkan):
    logger.info("正在使用ncnn进行超分辨率处理")
    output = ncnn_result_dir / image_path.name
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
    ]
    runCommand(cli_args)
    logger.info("超分辨率处理完成")
