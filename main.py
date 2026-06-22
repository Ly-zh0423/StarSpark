# main.py
import sys
from config import load_config
from services.github_service import GitHubService

def main():
    print("🚀 StarSpark 正在启动...")
    
    try:
        # 加载配置文件
        config = load_config("config.yaml")
        # 初始化核心业务服务
        service = GitHubService(config)
        # 执行爬取、存储与下载任务
        service.run_crawl_and_save()
        
        print("\n🎉 所有任务执行完毕！")
        
    except FileNotFoundError as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 运行期间发生未知错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()