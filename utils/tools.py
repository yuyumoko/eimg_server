import os
import re
import sys
import hashlib
import ujson
import psutil
import subprocess
from pathlib import Path

from sqlitedict import SqliteDict
from configparser import ConfigParser


def get_path(*paths):
    return os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), *paths)


db = {}


def connect_db(db_name="db", tablename="unnamed") -> SqliteDict:
    if db.get(db_name):
        return db[db_name]
    db[db_name] = SqliteDict(
        get_path("data", db_name + ".sqlite"),
        tablename=tablename,
        encode=ujson.dumps,
        decode=ujson.loads,
        autocommit=True,
    )
    return db[db_name]


class Config:
    configPath: Path
    cf: ConfigParser

    def __init__(self, configPath: Path | str):
        self.configPath = configPath
        self.cf = ConfigParser()
        if not self.cf.read(configPath, encoding="utf-8"):
            raise FileNotFoundError("配置文件不存在")

    def get(self, section: str, option: str, raw=False) -> str:
        return self.cf.get(section, option, raw=raw)

    def getint(self, section: str, option: str, raw=False) -> int:
        return self.cf.getint(section, option, raw=raw)

    def getboolean(self, section: str, option: str, raw=False) -> bool:
        return self.cf.getboolean(section, option, raw=raw)

    def items(self, section: str, raw=False):
        return self.cf.items(section, raw=raw)

    def set(self, section: str, option: str, value: str):
        if not self.cf.has_section(section):
            self.cf.add_section(section)
        self.cf.set(section, option, value)
        with self.configPath.open("w") as f:
            self.cf.write(f)


def md5(context):
    return hashlib.md5(context).hexdigest()


def str2md5(s):
    return md5(str(s).encode())


def is_md5(s):
    return bool(re.match(r"^[a-fA-F\d]{32}$", s))


def read_json_file(name):
    try:
        with open(get_path("data", name), "r") as fp:
            return ujson.loads(fp.read() or "{}")
    except FileNotFoundError:
        return {}


def write_json_file(name, data):
    with open(get_path("data", name), "w") as fp:
        fp.write(ujson.dumps(data))


def size_format(size):
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0


def runCommand(command, callback: callable = None):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    log = []
    line_num = 0
    # 实时获取输出
    while True:
        output = process.stdout.readline() or process.stderr.readline()
        return_code = process.poll()

        if not output and return_code is not None:
            break
        elif not output and return_code == 0:
            break
        elif output:
            line = output.decode("utf-8").strip()
            log.append(line)
            if callback:
                if callback(line, line_num):
                    process.wait()
                    break
            else:
                print(line)
            line_num += 1

    return log


def file_size_str(path):
    return size_format(os.stat(path).st_size)


def check_process_running(processName: Path | str):
    processName = processName.name if isinstance(processName, Path) else processName
    for proc in psutil.process_iter():
        try:
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def get_folder_size(folder_path):  # Path
    size = 0
    for path, dirs, files in os.walk(str(folder_path)):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)
    return size
