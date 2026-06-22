# crawlers/github_api.py
import time
import random
import requests
from bs4 import BeautifulSoup
from models import Project, ProjectMetrics

class GitHubCrawler:
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

    def _fetch_page(self, url: str) -> str:
        """发送请求并获取页面内容，包含延迟与容错机制"""
        try:
            response = requests.get(url, headers=self.headers, verify=False, timeout=15)
            response.raise_for_status()
            # 请求间增加固定延迟 + 随机延迟，防止被封禁
            time.sleep(self.delay + random.uniform(0, 0.5))
            return response.text
        except requests.RequestException as e:
            print(f"[爬虫错误] 请求 {url} 失败: {e}")
            return ""

    def parse_trending(self, period: str) -> list[dict]:
        """
        解析 GitHub Trending 页面
        注意：由于 GitHub 网页结构可能变动，以下 CSS 选择器基于当前主流结构，
        实际使用时可能需要根据最新网页微调。
        """
        url = f"https://github.com/trending?since={period}"
        html = self._fetch_page(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        articles = soup.select("article.Box-row")
        parsed_data = []

        for rank, article in enumerate(articles, start=1):
            try:
                # 提取项目名称 (owner/repo)
                h2_tag = article.select_one("h2 a")
                full_name = "".join(h2_tag.text.strip().split())

                # 提取描述
                desc_tag = article.select_one("p")
                description = desc_tag.text.strip() if desc_tag else ""
                print("description: ", description)

                # 提取编程语言
                lang_tag = article.select_one("[itemprop='programmingLanguage']")
                language = lang_tag.text.strip() if lang_tag else ""

                # 提取 Star / Fork / Issue 数量
                stars_text = article.select_one("a.Link--muted.d-inline-block.mr-3")
                forks_text = article.select("a.Link--muted.d-inline-block.mr-3")[1] if len(article.select("a.Link--muted.d-inline-block.mr-3")) > 1 else None
                
                stars = int(stars_text.text.strip().replace(",", "")) if stars_text else 0
                forks = int(forks_text.text.strip().replace(",", "")) if forks_text else 0
                issues = 0 # Trending 页面通常不直接显示 Issue 数量，可置 0 或通过 API 补充

                parsed_data.append({
                    "project": Project(full_name=full_name, description=description, language=language),
                    "metrics": ProjectMetrics(
                        full_name=full_name,
                        period_type=period,
                        rank=rank,
                        stars=stars,
                        forks=forks,
                        issues=issues
                    )
                })
            except Exception as e:
                print(f"[解析错误] 解析第 {rank} 个项目时出错: {e}")
                continue

        return parsed_data