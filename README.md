# StarSpark ✨

🚀 **StarSpark** 是一个 GitHub Trending 热门项目爬取与管理工具，支持自动抓取 GitHub 热门仓库数据、中文翻译、本地持久化存储、可选的项目源码包下载以及**每日定时自动执行**。

## ✨ 功能特性

- 🔍 **GitHub Trending 爬取**：支持爬取 `daily`、`weekly`、`monthly` 三种时间维度的热门榜单
- 🌐 **自动中文翻译**：自动将项目描述翻译为简体中文，方便中文用户阅读
- 💾 **SQLite 本地持久化**：将项目信息与指标快照存储到本地 SQLite 数据库，支持历史数据追踪
- 📊 **历史指标快照**：每次爬取均记录 Star、Fork、Issue 等指标，便于趋势分析与统计绘图
- 📦 **可选 ZIP 下载**：支持通过镜像加速下载项目源码包，已下载文件自动跳过
- ⏰ **定时自动执行**：支持配置每日执行时间窗口，自动随机选择时间点执行任务
- ⚙️ **YAML 配置驱动**：所有参数通过 `config.yaml` 灵活配置

## 📁 项目结构

```
StarSpark/
├── main.py                      # 程序入口
├── config.py                    # 配置加载模块（dataclass 映射）
├── config.yaml                  # 配置文件
├── models.py                    # 数据模型（Project / ProjectMetrics）
├── crawlers/
│   └── github_api.py            # GitHub Trending 页面爬虫
├── database/
│   ├── manager.py               # SQLite 连接管理器（上下文管理器）
│   └── repositories.py          # 数据持久化仓库层（CRUD）
├── services/
│   ├── github_service.py        # 核心业务服务（编排爬取/翻译/存储/下载）
│   └── scheduler.py             # 定时任务调度器（每日自动执行）
└── utils/
    └── translate.py             # 在线翻译工具
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- pip 包管理器

### 安装依赖

```bash
pip install requests bs4 pyyaml schedule
```

### 配置

编辑项目根目录下的 `config.yaml` 文件：

```yaml
# 数据库配置
database:
  path: "star_spark.db"       # SQLite 数据库文件路径

# 爬虫配置
crawler:
  periods:                     # 爬取周期类型，支持: daily, weekly, monthly
    - daily
    - weekly
    - monthly
  request_delay: 2.0           # 请求延迟（秒），防止被 GitHub 封禁

# 下载配置
download:
  auto_download: false         # 是否自动下载项目 zip 包
  mirror_url: "https://gh.xmly.dev"  # GitHub 下载镜像地址
  save_dir: "./downloads"      # zip 包本地保存目录

# 调度器配置
scheduler:
  start_hour: 20               # 执行时间窗口开始（24小时制）
  start_minute: 0
  end_hour: 22                 # 执行时间窗口结束（24小时制）
  end_minute: 30
  check_interval: 60           # 调度器检查频率（秒）
```

### 运行

```bash
python main.py
```

程序将依次执行：
1. 加载 `config.yaml` 配置文件
2. 初始化 SQLite 数据库与表结构
3. 启动定时调度器，在配置的时间窗口内随机选择时间点执行
4. 按配置的周期类型逐一爬取 GitHub Trending 榜单
5. 自动翻译项目描述为中文
6. 将项目信息与指标快照写入数据库
7. 若开启 `auto_download`，则通过镜像下载项目 ZIP 包

**提示**：程序会持续运行并在每天自动执行，按 `Ctrl+C` 停止。

## 🗄️ 数据库结构

### `projects` 表 — 项目基础信息

| 字段 | 类型 | 说明 |
|------|------|------|
| `full_name` | TEXT (PK) | 项目全名，如 `facebook/react` |
| `description` | TEXT | 原始英文描述 |
| `language` | TEXT | 主要编程语言 |
| `translated_desc` | TEXT | 翻译后的中文简介 |

### `project_metrics` 表 — 项目指标快照

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INTEGER (PK) | 自增主键 |
| `full_name` | TEXT (FK) | 关联项目全名 |
| `period_type` | TEXT | 榜单类型（daily / weekly / monthly） |
| `rank` | INTEGER | 当前排名 |
| `stars` | INTEGER | Star 数量 |
| `forks` | INTEGER | Fork 数量 |
| `issues` | INTEGER | Issue 数量 |
| `crawled_at` | TEXT | 爬取时间（本地时间） |

**索引优化**：`project_metrics` 表已为 `(full_name, period_type, crawled_at)` 建立复合索引，加速历史数据查询。

## 🔧 模块说明

| 模块 | 说明 |
|------|------|
| [`config.py`](config.py) | 使用 `dataclass` 将 YAML 配置映射为强类型对象，支持类型检查与默认值 |
| [`models.py`](models.py) | 定义 `Project` 和 `ProjectMetrics` 数据模型 |
| [`crawlers/github_api.py`](crawlers/github_api.py) | 基于 BeautifulSoup 的 GitHub Trending 页面解析器，内置请求延迟与容错机制 |
| [`database/manager.py`](database/manager.py) | SQLite 连接管理器，使用上下文管理器自动处理事务提交与回滚 |
| [`database/repositories.py`](database/repositories.py) | 数据仓库层，提供项目信息 UPSERT、指标插入、历史查询等操作 |
| [`services/github_service.py`](services/github_service.py) | 核心业务编排层，串联爬取 → 翻译 → 存储 → 下载完整流程 |
| [`services/scheduler.py`](services/scheduler.py) | 定时任务调度器，支持每日时间窗口内随机执行，自动日期切换与状态重置 |
| [`utils/translate.py`](utils/translate.py) | 调用在线翻译 API 将英文描述翻译为简体中文 |

## 📌 注意事项

- 请合理设置 `request_delay`，避免请求频率过高被 GitHub 限制访问
- GitHub Trending 页面的 HTML 结构可能随官方更新而变化，届时需调整 [`crawlers/github_api.py`](crawlers/github_api.py) 中的 CSS 选择器
- 翻译功能依赖外部翻译 API，网络不稳定时可能返回空翻译结果，不影响主流程
- 定时调度器会在每天配置的时间窗口内随机选择一个时间点执行，确保程序持续运行
- SQLite 数据库文件会随着爬取逐渐增大，建议定期备份或清理历史数据

## 📊 数据查询示例

项目提供了 `get_project_history()` 方法，可方便地获取某个项目的历史指标数据，用于统计绘图：

```python
from database.manager import DatabaseManager
from database.repositories import ProjectRepository

db_manager = DatabaseManager("star_spark.db")
repo = ProjectRepository(db_manager)

# 获取某个项目的所有历史数据
history = repo.get_project_history("facebook/react")

# 获取某个项目在特定周期下的历史数据
daily_history = repo.get_project_history("facebook/react", period_type="daily")
```

## 📄 License

MIT License
