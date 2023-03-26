from pathlib import Path
from utils import logger, runCommand
from .helps import ncnn_result_dir


def handler_process(line, line_num):
    if line_num < 4:
        logger.info(line)


def convert_image(image_path: Path, scale, vulkan):
    logger.info(f" -> 正在使用 [realesrgan] 进行超分辨率处理: {image_path.name}")
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
        "-x",
    ]
    runCommand(cli_args, handler_process)
    logger.info(" -> 超分辨率处理完成")
