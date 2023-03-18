import logging
import colorlog

__all__ = ['logger']

logger = logging.getLogger('all')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(
    colorlog.ColoredFormatter(
        fmt='%(log_color)s%(levelname)-8s%(reset)s%(blue)s%(asctime)s - %(green)s %(message)s',
        datefmt='(%Y-%m-%d %H:%M:%S)',
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }))
logger.addHandler(console_handler)
