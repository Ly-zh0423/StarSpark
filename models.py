# models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Project:
    """GitHub 项目基础信息"""
    full_name: str          # 唯一标识，如 'facebook/react'
    description: Optional[str] = None
    language: Optional[str] = None
    translated_desc: Optional[str] = None  # 翻译后的中文简介

@dataclass
class ProjectMetrics:
    """项目指标快照（用于历史记录与统计绘图）"""
    full_name: str
    period_type: str        # daily, weekly, monthly
    rank: int               # 当前榜单排名
    stars: int              # Star 数量
    forks: int              # Fork 数量
    issues: int             # Issue 数量
    crawled_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 爬取时间