# services/github_service.py
import os
import requests
from config import AppConfig
from crawlers.github_api import GitHubCrawler
from database.manager import DatabaseManager
from database.repositories import ProjectRepository
from utils.translate import translate_text

class GitHubService:
    def __init__(self, config: AppConfig):
        self.config = config
        self.crawler = GitHubCrawler(delay=config.crawler.request_delay)
        self.db_manager = DatabaseManager(config.database.path)
        self.repo = ProjectRepository(self.db_manager)
        # 启动时自动初始化数据库表
        self.repo.init_tables()

    def run_crawl_and_save(self):
        """执行完整的爬取、翻译、存储流程"""
        for period in self.config.crawler.periods:
            print(f"[*] 开始爬取 {period} 榜单...")
            items = self.crawler.parse_trending(period)
            
            for item in items:
                project = item["project"]
                metrics = item["metrics"]

                # 翻译项目描述（如果配置了翻译工具）
                if project.description:
                    project.translated_desc = translate_text(project.description)

                # 存入数据库
                self.repo.upsert_project(project)
                self.repo.insert_metrics(metrics)

                # 触发下载任务
                if self.config.download.auto_download:
                    self._download_project_zip(project.full_name)

            print(f"[+] {period} 榜单处理完成，共 {len(items)} 个项目。")

    def _download_project_zip(self, full_name: str):
        """下载项目的 ZIP 包，支持镜像加速，不执行解压"""
        save_dir = self.config.download.save_dir
        os.makedirs(save_dir, exist_ok=True)

        # 拼接下载链接：镜像地址 + /项目所有者/项目名/archive/refs/heads/main.zip
        base_url = self.config.download.mirror_url.rstrip("/")
        zip_url = f"{base_url}/{full_name}/archive/refs/heads/main.zip"
        
        # 文件名处理：将 'owner/repo' 替换为 'owner_repo.zip' 防止路径错误
        safe_filename = f"{full_name.replace('/', '_')}.zip"
        file_path = os.path.join(save_dir, safe_filename)

        # 如果文件已存在，跳过下载
        if os.path.exists(file_path):
            print(f"[跳过] {safe_filename} 已存在。")
            return

        try:
            print(f"[下载中] {zip_url}")
            response = requests.get(zip_url, timeout=60, stream=True)
            response.raise_for_status()
            
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"[成功] 已保存至 {file_path}")
        except requests.RequestException as e:
            print(f"[下载失败] {full_name}: {e}")