import logging
import traceback
import json
from auth.login_manager import LoginManager
from page_selectors.page_selector import PageSelector
from tasks.pdf_executor import PDFExecutor
from tasks.video_executor import VideoExecutor
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mooc.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 从config.json文件中加载配置
with open('config.json', 'r', encoding='utf-8') as config_file:
    config_data = json.load(config_file)

class MoocAutomation:
    def __init__(self):
        # 配置选项
        self.config = {
            "skip_finished": True,  # 是否跳过已完成的任务
            "skip_pdf": False,  # 是否跳过PDF任务
            "skip_video": False,  # 是否跳过视频任务
        }
        self.login_manager = LoginManager()
        self.driver = self.login_manager.get_driver()
        self.wait = self.login_manager.wait
        self.page_selector = PageSelector(self.driver, self.wait)
        self.pdf_executor = PDFExecutor(self.driver, self.wait)
        self.video_executor = VideoExecutor(self.driver, self.wait)

    def run(self, username=None, password=None, course_url=None):
        try:
            # 从配置文件中获取参数
            if username is None:
                username = config_data.get('username')
            if password is None:
                password = config_data.get('password')
            if course_url is None:
                course_url = config_data.get('course_url')

            # 登录
            self.login_manager.login(username, password)

            # 打开课程页面
            if course_url is None:
                course_url = config_data.get('course_url')
            self.page_selector.open_course_page(course_url)

            # 初始化未完成章节列表
            if not self.page_selector.initialize_unfinished_chapters():
                logging.info("没有找到任何未完成的章节")
                return

            while True:
                # 尝试点击下一个未完成的章节
                if not self.page_selector.click_next_unfinished_chapter():
                    logging.info("所有章节已处理完毕")
                    break

                # 等待页面加载
                self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "prev_title_pos"))
                )

                # 查找所有任务
                tasks = self.page_selector.find_all_tasks()

                # 执行任务
                for task in tasks:
                    # 如果配置为跳过已完成任务，且当前任务已完成，则跳过
                    if self.config["skip_finished"] and task["is_finished"]:
                        logging.info(f"跳过已完成的任务: {task.get('title', '未知任务')}")
                        continue
                    if self.config["skip_pdf"] and task["type"] == "pdf":
                        logging.info(f"跳过PDF任务: {task.get('title', '未知任务')}")
                        continue
                    if self.config["skip_video"] and task["type"] == "video":
                        logging.info(f"跳过视频任务: {task.get('title', '未知任务')}")
                        continue

                    if task["type"] == "pdf":
                        self.pdf_executor.execute(task)
                    elif task["type"] == "video":
                        self.video_executor.execute(task)

                # 返回课程页面
                self.page_selector.open_course_page(course_url)

        except Exception as e:
            logging.error(f"程序运行出错: {str(e)}")
            logging.debug(traceback.format_exc())
        finally:
            input("按回车键退出...")
            self.login_manager.close()

def main():
    logging.info("程序开始运行...")
    automation = MoocAutomation()
    automation.run()
    logging.info("程序结束运行")

if __name__ == "__main__":
    main() 