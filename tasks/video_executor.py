import logging
import time
import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from .task_executor import TaskExecutor

class VideoExecutor(TaskExecutor):
    def execute(self, task_info):
        """
        执行视频播放任务
        """
        logging.info("开始播放视频...")
        try:
            # 1. 切换到主iframe
            logging.debug("切换到主iframe")
            main_iframe = self.wait.until(
                EC.presence_of_element_located((By.ID, "iframe"))
            )
            self.driver.switch_to.frame(main_iframe)
            
            # 2. 切换到视频iframe
            logging.debug("切换到视频iframe...")
            video_iframe = self.wait.until(
                EC.presence_of_element_located((By.XPATH, task_info["xpath"]))
            )
            self.driver.switch_to.frame(video_iframe)
            
            # 3. 点击播放按钮
            logging.debug("点击播放按钮...")
            play_button = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "vjs-big-play-button"))
            )
            play_button.click()
            
            # 4. 等待视频元素加载
            logging.debug("等待视频元素加载...")
            video_element = self.wait.until(
                EC.presence_of_element_located((By.ID, "video_html5_api"))
            )
            
            # 5. 尝试静音视频
            logging.debug("尝试静音视频...")
            mute_button = self.driver.find_element(By.CLASS_NAME, "vjs-mute-control")
            if "vjs-vol-3" in mute_button.get_attribute("class"):
                # 使用 JavaScript 执行点击操作
                self.driver.execute_script("arguments[0].click();", mute_button)
                
            # 6. 获取视频时长并等待播放完成
            duration = self.wait.until(lambda d: d.execute_script(
                "return document.getElementById('video_html5_api').duration"
            ))
            
            logging.info(f"视频总时长: {duration:.1f}秒")
            
            current_time = 0
            while current_time < duration:
                current_time = self.driver.execute_script(
                    "return document.getElementById('video_html5_api').currentTime"
                )
                time.sleep(1)
                if int(current_time) % 10 == 0:
                    logging.info(f"视频播放进度: {current_time:.1f}/{duration:.1f}秒")
                print(f"当前播放进度: {current_time:.1f}/{duration:.1f}秒", end='\r')
                
            logging.info("视频播放完成!")
            
        except Exception as e:
            logging.error(f"播放视频时出错: {str(e)}")
            logging.debug(traceback.format_exc())
            raise
        finally:
            try:
                # 依次切换回各层frame
                self.driver.switch_to.parent_frame()  # 从video iframe切回main iframe
                self.driver.switch_to.default_content()  # 最后切回默认内容
            except Exception as e:
                logging.error(f"切换回默认frame时出错: {str(e)}") 