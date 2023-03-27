from pathlib import Path
from utils import logger, runCommand


def handler_process(line, line_num):
    if line_num < 4:
        logger.info(line)


def convert_image(image_path: Path, scale, vulkan, output):
    logger.info(f" -> 正在使用 [realcugan] 进行超分辨率处理: {image_path.name}")
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
        # "-v",
    ]
    if scale == 2:
        cli_args += ["-m", "models-pro"]
    runCommand(cli_args, handler_process)
    logger.info(" -> 超分辨率处理完成")
