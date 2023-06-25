import sqlite3
from io import StringIO
from pathlib import Path
from typing import List

import ujson
from pydantic import BaseModel
from sqlitedict import SqliteDict

from utils import get_path, iterdump, str2md5


def connect_mem_db(tablename: str) -> SqliteDict:
    """
    连接内存数据库

    Args:
        tablename (str): 表名

    Returns:
        SqliteDict: 返回SqliteDict对象
    """
    return SqliteDict(
        ":memory:",
        tablename=tablename,
        encode=ujson.dumps,
        decode=ujson.loads,
        autocommit=True,
    )


def connect_file_db(filename: str, tablename: str = "unnamed") -> SqliteDict:
    """_summary_

    Args:
        filename (str): 文件路径
        tablename (str, optional): 表名. 默认为 "unnamed".

    Returns:
        SqliteDict: 返回SqliteDict对象
    """
    return SqliteDict(
        get_path(filename),
        tablename=tablename,
        encode=ujson.dumps,
        decode=ujson.loads,
        autocommit=True,
    )


class SimpleSqlite:
    db_path: Path = Path("data.db")
    db: SqliteDict = None
    db_tablename = None
    is_mem_db = False
    table_dump: List[StringIO] = []

    def save_mem_db(self):
        """
        保存内存数据库到文件, 同时保存已dump的表
        并且连接文件数据库
        """

        if not self.is_mem_db:
            return

        self.save_table(self.db)
        self.db.close()

        con_file = sqlite3.connect(self.db_path)
        cur_file = con_file.cursor()
        for str_buffer in self.table_dump:
            cur_file.executescript(str_buffer.getvalue())
        cur_file.close()

        self.is_mem_db = False
        self.set_table(self.db_tablename)

    def connect(self, tablename: str) -> SqliteDict:
        """
        连接一个数据库, 如果数据库文件不存在, 那么自动创建一个内存数据库

        Args:
            tablename (str): 表名

        Returns:
            SqliteDict: 返回SqliteDict对象
        """
        if self.is_mem_db:
            return connect_mem_db(tablename)
        else:
            return connect_file_db(self.db_path, tablename=tablename)

    def set_table(self, tablename: str):
        """
        设置主表名字, 可使用 "db" 属性访问

        Args:
            tablename (str): 表名
        """
        self.db_tablename = tablename
        self.db = self.connect(tablename)

    def __init__(self, db_path: Path = None, tablename: str = "ALL"):
        """
        连接一个sqlite3数据库, 如果数据库文件不存在, 那么自动创建一个内存数据库

        Args:
            db_path (Path, optional): 数据库文件路径, 空则创建内存数据库, 可使用 "save_mem_db" 保存到文件.
            tablename (str, optional): 连接的表名, 默认 "ALL".
        """
        self.db_path = db_path or self.db_path
        if not self.db_path.exists():
            self.is_mem_db = True
        self.set_table(tablename)

    def table(self, tablename: str) -> SqliteDict:
        """
        连接该数据库的表名

        Args:
            tablename (str): 表名

        Returns:
            SqliteDict: 返回SqliteDict对象
        """
        return self.connect(tablename)

    def save_table(self, table_db: SqliteDict) -> StringIO:
        """
        使用内存数据库时, dump表到内存用于保存到文件

        Args:
            table_db (SqliteDict): 连接表的SqliteDict对象

        Returns:
            StringIO: 返回dump表的StringIO对象
        """
        if not self.is_mem_db:
            return
        table_db.commit()
        str_buffer = StringIO()
        for line in iterdump(table_db):
            str_buffer.write("%s\n" % line)
        self.table_dump.append(str_buffer)
        return str_buffer

    def save_table_and_close(self, table_db: SqliteDict):
        """
        同 "save_table" 并且关闭数据库

        Args:
            table_db (SqliteDict): 连接表的SqliteDict对象
        """
        self.save_table(table_db)
        table_db.close()

    def get(self, key):
        return self.db.get(key)

    def set(self, key, value):
        self.db[key] = value

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.db.close()


# 自定义数据
class IMG_DATA(BaseModel):
    file: str
    hash: str
    size: int
    mtime: float


class ImgDB(SimpleSqlite):
    def __init__(self, db_path: Path = None):
        super().__init__(db_path=db_path)

    @staticmethod
    def new_data(hash: str, file: Path) -> IMG_DATA:
        file_stat = file.stat()
        return IMG_DATA(
            file=str(file),
            hash=hash,
            size=file_stat.st_size,
            mtime=file_stat.st_mtime,
        )

    @staticmethod
    def new_dir_key(name: str | Path) -> str:
        return str2md5(Path(name))

    def get_data(self, hash: str) -> IMG_DATA:
        data = self.get(hash)
        if not data:
            return None
        dir_db = self.table(data)
        return IMG_DATA(**dir_db)

    def set_data(self, hash: str, file: Path) -> IMG_DATA:
        # 设置总表的索引
        dir_key = self.new_dir_key(file.parent)
        self.set(hash, dir_key)

        # 设置子表的数据
        new_data = self.new_data(hash, file)
        dir_img_db = self.table(dir_key)
        dir_img_db[hash] = new_data.dict()
        return new_data

    def del_data(self, hash: str):
        dir_db = self.table(self.get(hash))
        dir_db.pop(hash)
        self.db.pop(hash)
