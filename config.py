# config.py
import os
import yaml
from dataclasses import dataclass, field
from typing import List

@dataclass
class DatabaseConfig:
    path: str = "star_spark.db"

@dataclass
class CrawlerConfig:
    periods: List[str] = field(default_factory=lambda: ["daily"])
    request_delay: float = 2.0

@dataclass
class DownloadConfig:
    auto_download: bool = False
    mirror_url: str = "https://gh.xmly.dev"
    save_dir: str = "./downloads"

@dataclass
class SchedulerConfig:
    start_hour: int = 20
    start_minute: int = 0
    end_hour: int = 22
    end_minute: int = 30
    check_interval: int = 60

@dataclass
class AppConfig:
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    crawler: CrawlerConfig = field(default_factory=CrawlerConfig)
    download: DownloadConfig = field(default_factory=DownloadConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig) # 新增调度器配置

def load_config(config_path: str = "config.yaml") -> AppConfig:
    """加载并解析 YAML 配置文件"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件 {config_path} 未找到！")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        raw_config = yaml.safe_load(f)
    
    return AppConfig(
        database=DatabaseConfig(**raw_config.get('database', {})),
        crawler=CrawlerConfig(**raw_config.get('crawler', {})),
        download=DownloadConfig(**raw_config.get('download', {})),
        scheduler=SchedulerConfig(**raw_config.get('scheduler', {})) # 加载调度器配置
    )