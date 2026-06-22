# database/manager.py
import sqlite3
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器，自动处理事务和连接关闭"""
        conn = sqlite3.connect(self.db_path)
        # 允许通过字典形式访问查询结果（可选，这里保持默认元组形式即可）
        conn.row_factory = sqlite3.Row 
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()