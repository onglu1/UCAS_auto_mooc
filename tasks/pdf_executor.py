import logging
import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .task_executor import TaskExecutor

class PDFExecutor(TaskExecutor):
    def execute(self, task_info):
        """
        执行PDF阅读任务
        """
        logging.info("开始阅读PDF...")
        try:
            # 1. 先切换到主iframe,使用id定位
            logging.debug("切换到主iframe")
            main_iframe = self.wait.until(
                EC.presence_of_element_located((By.ID, "iframe"))
            )
            self.driver.switch_to.frame(main_iframe)
            
            # 2. 等待并切换到PDF iframe
            logging.debug(f"等待PDF iframe加载,xpath={task_info['xpath']}")
            pdf_iframe = self.wait.until(
                EC.presence_of_element_located((By.XPATH, task_info["xpath"]))
            )
            logging.debug("PDF iframe已找到,准备切换")
            self.driver.switch_to.frame(pdf_iframe)
            
            # 3. 等待并切换到panView iframe
            logging.debug("等待panView iframe加载")
            pan_view_iframe = self.wait.until(
                EC.presence_of_element_located((By.ID, "panView"))
            )
            logging.debug("panView iframe已找到,准备切换")
            self.driver.switch_to.frame(pan_view_iframe)
            
            # 4. 添加更长的等待时间
            logging.debug("等待PDF内容加载...") 
            time.sleep(5)
            
            # 5. 检查fileBox是否存在,添加显式等待
            logging.debug("查找fileBox元素")
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "fileBox"))
                )
            except Exception as e:
                logging.error(f"未找到fileBox元素:{str(e)}")
                return
                
            images = self.driver.find_elements(By.CSS_SELECTOR, ".fileBox img")
            if not images:
                logging.warning("未找到PDF图片")
                return
                
            logging.info(f"找到 {len(images)} 张PDF图片，将直接阅读最后一张")
            
            # 只处理最后一张图片
            try:
                last_img = images[-1]
                self.driver.execute_script("arguments[0].scrollIntoView(true);", last_img)
                time.sleep(1)
                
                img_height = self.driver.execute_script("return arguments[0].offsetHeight;", last_img)
                current_scroll = self.driver.execute_script("return window.pageYOffset;")
                
                scroll_step = 100
                for scroll_pos in range(current_scroll, current_scroll + img_height, scroll_step):
                    self.driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
                    time.sleep(0.2)
                
                logging.info("已阅读最后一张图片")
                print("已完成最后一张图片阅读")
            except Exception as e:
                logging.error(f"滚动阅读最后一张图片时出错: {str(e)}")
            
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
            
            logging.info("PDF阅读完成!")
            
        except Exception as e:
            logging.error(f"阅读PDF时出错: {str(e)}")
            logging.debug(traceback.format_exc())
            raise
        finally:
            try:
                # 依次切换回各层frame
                self.driver.switch_to.parent_frame()  # 从panView切回pdf iframe
                self.driver.switch_to.parent_frame()  # 从pdf iframe切回main iframe
                self.driver.switch_to.default_content()  # 最后切回默认内容
            except Exception as e:
                logging.error(f"切换回默认frame时出错: {str(e)}") 