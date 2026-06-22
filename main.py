# main.py
import sys
import logging
from config import load_config
from services.scheduler import TaskScheduler

# 配置基础日志格式
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 StarSpark 正在启动...")
    
    try:
        # 1. 加载配置文件
        config = load_config("config.yaml")
        
        # 2. 初始化并启动调度器
        scheduler = TaskScheduler(config)
        scheduler.run_scheduler()
        
    except FileNotFoundError as e:
        logger.error(f"❌ 启动失败: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 运行期间发生未知错误: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()