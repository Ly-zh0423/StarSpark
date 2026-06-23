# services/scheduler.py
import time
import random
import logging
import schedule
from datetime import datetime
from config import AppConfig
from services.github_service import GitHubService

logger = logging.getLogger(__name__)

class TaskScheduler:
    """使用 schedule 库的定时任务调度器"""
    
    def __init__(self, config: AppConfig):
        """初始化调度器"""
        self.config = config
        self.service = GitHubService(config)
        self.last_run_date = None
        self.runned = False
        self.setup_schedule()
        
        logger.info("📅 每日定时调度器已初始化")
        logger.info(f"⏰ 执行时间窗口: {config.scheduler.start_hour:02d}:{config.scheduler.start_minute:02d} - "
                    f"{config.scheduler.end_hour:02d}:{config.scheduler.end_minute:02d}")
        logger.info("🎲 每天在此时间窗口内随机选择一个时间点执行一次")
    
    def clear_schedule(self):
        """清除定时任务"""
        schedule.clear()

    def check_and_reset_daily_status(self):
        """检查是否是新的一天，如果是则重置状态并重新安排任务"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        if self.last_run_date != current_date:
            logger.info(f"📆 检测到新的一天 ({current_date})，重置任务状态")
            self.last_run_date = current_date
            self.runned = False
            self.setup_schedule()

    def setup_schedule(self):
        """设置定时任务 - 每天在配置的时间窗口内随机时间执行"""
        self.clear_schedule()
        self.runned = False

        start_h = self.config.scheduler.start_hour
        start_m = self.config.scheduler.start_minute
        end_h = self.config.scheduler.end_hour
        end_m = self.config.scheduler.end_minute

        # 在时间窗口内随机选择一个时间点
        if start_h == end_h:
            # 如果开始和结束在同一个小时
            hour = start_h
            minute = random.randint(start_m, end_m)
        else:
            # 跨小时的情况
            hour = random.randint(start_h, end_h)
            if hour == start_h:
                minute = random.randint(start_m, 59)
            elif hour == end_h:
                minute = random.randint(0, end_m)
            else:
                minute = random.randint(0, 59)
        
        logger.info(f"🎲 今日执行时间已设定: {hour:02d}:{minute:02d}")
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self.execute_task)
    
    def execute_task(self):
        """执行核心业务任务"""
        if self.runned: 
            return

        logger.info(f"🕐 定时任务开始执行 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            # 调用核心业务服务
            self.service.run_crawl_and_save()
            logger.info("✅ 任务执行完成")
            self.runned = True
        except Exception as e:
            logger.error(f"❌ 任务执行异常: {str(e)}", exc_info=True)
        logger.info("=" * 60)
        
    
    def run_scheduler(self):
        """运行调度器主循环"""
        logger.info("📅 每日定时调度器已启动")
        logger.info(f"🔄 检查频率: 每 {self.config.scheduler.check_interval} 秒检查一次")
        logger.info("按 Ctrl+C 停止程序\n")
        
        try:
            while True:
                # 检查是否是新的一天并重置状态
                self.check_and_reset_daily_status()
                
                # 检查是否有计划的任务需要运行
                schedule.run_pending()
                
                # 按照配置的频率休眠
                time.sleep(self.config.scheduler.check_interval)
                
        except KeyboardInterrupt:
            logger.info("\n👋 定时调度器已停止")