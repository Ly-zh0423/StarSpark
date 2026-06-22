# database/repositories.py
from models import Project, ProjectMetrics

class ProjectRepository:
    def __init__(self, db_manager):
        self.db = db_manager

    def init_tables(self):
        """初始化数据库表结构"""
        create_projects_sql = """
            CREATE TABLE IF NOT EXISTS projects (
                full_name TEXT PRIMARY KEY,
                description TEXT,
                language TEXT,
                translated_desc TEXT
            )
        """
        create_metrics_sql = """
            CREATE TABLE IF NOT EXISTS project_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                period_type TEXT NOT NULL,
                rank INTEGER NOT NULL,
                stars INTEGER NOT NULL,
                forks INTEGER NOT NULL,
                issues INTEGER NOT NULL,
                crawled_at TEXT NOT NULL,
                FOREIGN KEY (full_name) REFERENCES projects(full_name)
            )
        """
        # 为历史查询和绘图建立索引，大幅提升查询速度
        create_index_sql = """
            CREATE INDEX IF NOT EXISTS idx_metrics_history 
            ON project_metrics (full_name, period_type, crawled_at);
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(create_projects_sql)
            cursor.execute(create_metrics_sql)
            cursor.execute(create_index_sql)

    def upsert_project(self, project: Project):
        """插入或更新项目基础信息"""
        sql = """
            INSERT INTO projects (full_name, description, language, translated_desc)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(full_name) DO UPDATE SET
                description = excluded.description,
                language = excluded.language,
                translated_desc = excluded.translated_desc
        """
        with self.db.get_connection() as conn:
            conn.execute(sql, (project.full_name, project.description, project.language, project.translated_desc))

    def insert_metrics(self, metrics: ProjectMetrics):
        """插入项目指标快照（每次爬取都会新增一条记录）"""
        sql = """
            INSERT INTO project_metrics (full_name, period_type, rank, stars, forks, issues, crawled_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self.db.get_connection() as conn:
            conn.execute(sql, (metrics.full_name, metrics.period_type, metrics.rank, metrics.stars, metrics.forks, metrics.issues, metrics.crawled_at))

    def get_project_history(self, full_name: str, period_type: str = None):
        """获取某个项目的历史数据（专为统计绘图设计）"""
        sql = "SELECT * FROM project_metrics WHERE full_name = ?"
        params = [full_name]
        if period_type:
            sql += " AND period_type = ?"
            params.append(period_type)
        sql += " ORDER BY crawled_at ASC"
        
        with self.db.get_connection() as conn:
            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]