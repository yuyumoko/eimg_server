import os
import sys
import hashlib
import ujson
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
    if size < 1000:
        return '%i' % size + 'B'
    elif 1000 <= size < 1000000:
        return '%.1f' % float(size / 1000) + 'KB'
    elif 1000000 <= size < 1000000000:
        return '%.1f' % float(size / 1000000) + 'MB'
    elif 1000000000 <= size < 1000000000000:
        return '%.1f' % float(size / 1000000000) + 'GB'
    elif 1000000000000 <= size:
        return '%.1f' % float(size / 1000000000000) + 'TB'