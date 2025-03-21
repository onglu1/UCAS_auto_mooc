import logging
import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class PageSelector:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        self.unfinished_chapters = []
        self.current_chapter_index = 0

    def find_all_tasks(self):
        """
        查找页面中所有任务点
        """
        logging.info("开始查找所有任务点...")
        try:
            logging.debug("切换到主iframe")
            self.driver.switch_to.frame("iframe")
            
            logging.debug("等待任务点加载...")
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "ans-job-icon"))
            )
            
            tasks = self.driver.find_elements(By.CLASS_NAME, "ans-job-icon")
            logging.info(f"找到 {len(tasks)} 个任务点")
            all_tasks = []
            
            pdf_index = 0
            video_index = 0

            for i, task in enumerate(tasks, 1):
                try:
                    parent = task.find_element(By.XPATH, "./..")
                    class_name = parent.get_attribute("class")
                    is_finished = "ans-job-finished" in class_name
                    
                    iframe = parent.find_element(By.TAG_NAME, "iframe")
                    iframe_class = iframe.get_attribute("class")
                    
                    task_type = "unknown"
                    task_xpath = ""
                    if "insertdoc-online-pdf" in iframe_class:
                        task_type = "pdf"
                        pdf_index += 1
                        task_xpath = f"(//iframe[contains(@class, 'insertdoc-online-pdf')])[{pdf_index}]"
                    elif "ans-insertvideo-online" in iframe_class:
                        task_type = "video"
                        video_index += 1
                        task_xpath = f"(//iframe[contains(@class, 'ans-insertvideo-online')])[{video_index}]"
                    
                    task_info = {
                        "type": task_type,
                        "xpath": task_xpath,
                        "element": task,
                        "is_finished": is_finished,
                        "class_name": class_name,
                        "iframe_class": iframe_class,
                        "index": i
                    }
                    
                    try:
                        task_text = task.get_attribute("title") or parent.text
                        task_info["title"] = task_text
                    except:
                        task_info["title"] = "无法获取标题"
                    
                    all_tasks.append(task_info)
                    logging.info(f"任务点 {i}: 类型={task_type}, 已完成={is_finished}")
                    
                except Exception as e:
                    logging.error(f"处理任务点 {i} 时出错: {str(e)}")
                    logging.debug(traceback.format_exc())
            
            self._log_task_statistics(all_tasks)
            return all_tasks
            
        except Exception as e:
            logging.error(f"查找任务点时出错: {str(e)}")
            logging.debug(traceback.format_exc())
            raise
        finally:
            self.driver.switch_to.default_content()

    def _log_task_statistics(self, tasks):
        finished_count = len([t for t in tasks if t["is_finished"]])
        unfinished_count = len(tasks) - finished_count
        pdf_count = len([t for t in tasks if t["type"] == "pdf"])
        video_count = len([t for t in tasks if t["type"] == "video"])
        
        logging.info("任务点统计信息:")
        logging.info(f"- 已完成: {finished_count}")
        logging.info(f"- 未完成: {unfinished_count}")
        logging.info(f"- PDF任务: {pdf_count}")
        logging.info(f"- 视频任务: {video_count}")

    def find_unfinished_chapter(self):
        """
        查找包含待完成任务点的章节
        """
        logging.info("开始查找未完成的章节...")
        try:
            # 切换到章节列表的iframe
            logging.debug("切换到章节列表iframe")
            self.driver.switch_to.frame("frame_content-zj")
            
            # 等待章节列表加载
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "chapter_item"))
            )
            
            # 查找所有包含待完成任务点的章节
            chapters = self.driver.find_elements(By.CLASS_NAME, "chapter_item")
            for chapter in chapters:
                try:
                    # 如果没有onclick属性，是章节折叠，跳过
                    onclick = chapter.get_attribute("onclick")
                    if not onclick:
                        continue
                    # 如果任务不包含已完成任务点，则认为该章节未完成
                    task_points = chapter.find_elements(By.CLASS_NAME, "icon_yiwanc")
                    if not task_points: 
                        # 获取章节信息
                        title = chapter.get_attribute("title")
                        onclick = chapter.get_attribute("onclick")
                        logging.info(f"找到未完成章节: {title}")
                        return chapter
                except Exception as e:
                    logging.debug(f"处理章节时出错: {str(e)}")
                    continue
            
            logging.info("没有找到未完成的章节")
            return None
            
        except Exception as e:
            logging.error(f"查找未完成章节时出错: {str(e)}")
            return None
        finally:
            # 切换回默认内容
            self.driver.switch_to.default_content()

    def click_unfinished_chapter(self):
        """
        点击未完成的章节
        """
        chapter = self.find_unfinished_chapter()
        if chapter:
            try:
                # 重新切换到iframe，因为find_unfinished_chapter在返回前切换回了默认内容
                self.driver.switch_to.frame("frame_content-zj")
                chapter.click()
                logging.info("已点击未完成章节")
                # 切换回默认内容
                self.driver.switch_to.default_content()
                return True
            except Exception as e:
                logging.error(f"点击章节时出错: {str(e)}")
                # 确保切换回默认内容
                self.driver.switch_to.default_content()
                return False
        return False

    def open_course_page(self, url):
        """
        打开指定的课程页面
        """
        self.driver.get(url)
        logging.info("已打开课程页面")

    def get_all_unfinished_chapters(self):
        """
        获取所有未完成章节的列表
        """
        logging.info("开始获取所有未完成的章节...")
        unfinished_chapters = []
        try:
            self.driver.switch_to.frame("frame_content-zj")
            
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "chapter_item"))
            )
            
            chapters = self.driver.find_elements(By.CLASS_NAME, "chapter_item")
            for chapter in chapters:
                try:
                    onclick = chapter.get_attribute("onclick")
                    if not onclick:
                        continue
                    task_points = chapter.find_elements(By.CLASS_NAME, "icon_yiwanc")
                    if not task_points:
                        title = chapter.get_attribute("title")
                        unfinished_chapters.append({
                            'element': chapter,
                            'title': title,
                            'onclick': onclick
                        })
                        logging.info(f"添加未完成章节: {title}")
                except Exception as e:
                    logging.debug(f"处理章节时出错: {str(e)}")
                    continue
            
            logging.info(f"共找到 {len(unfinished_chapters)} 个未完成章节")
            return unfinished_chapters
            
        except Exception as e:
            logging.error(f"获取未完成章节列表时出错: {str(e)}")
            return []
        finally:
            self.driver.switch_to.default_content()

    def initialize_unfinished_chapters(self):
        """
        初始化未完成章节列表
        """
        self.unfinished_chapters = self.get_all_unfinished_chapters()
        self.current_chapter_index = 0
        return len(self.unfinished_chapters) > 0

    def click_next_unfinished_chapter(self):
        """
        点击下一个未完成的章节
        """
        if not self.unfinished_chapters:
            logging.info("没有未完成的章节")
            return False

        if self.current_chapter_index >= len(self.unfinished_chapters):
            logging.info("所有未完成章节都已尝试")
            return False

        try:
            chapter_info = self.unfinished_chapters[self.current_chapter_index]
            logging.info(f"尝试点击第 {self.current_chapter_index + 1} 个未完成章节: {chapter_info['title']}")
            
            # 切换到章节列表的iframe
            self.driver.switch_to.frame("frame_content-zj")
            
            # 等待章节列表加载
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "chapter_item"))
            )
            
            # 重新获取所有章节元素
            chapters = self.driver.find_elements(By.CLASS_NAME, "chapter_item")
            target_chapter = None
            
            # 通过标题和onclick属性匹配目标章节
            for chapter in chapters:
                try:
                    title = chapter.get_attribute("title")
                    onclick = chapter.get_attribute("onclick")
                    if title == chapter_info['title'] and onclick == chapter_info['onclick']:
                        target_chapter = chapter
                        break
                except Exception:
                    continue
            
            if target_chapter is None:
                logging.error(f"无法找到章节: {chapter_info['title']}")
                self.current_chapter_index += 1
                return self.click_next_unfinished_chapter()
            
            # 点击找到的章节
            target_chapter.click()
            self.current_chapter_index += 1
            logging.info(f"已点击章节: {chapter_info['title']}")
            return True
            
        except Exception as e:
            logging.error(f"点击章节时出错: {str(e)}")
            self.current_chapter_index += 1  # 跳过当前出错的章节
            return self.click_next_unfinished_chapter()  # 递归尝试下一个章节
        finally:
            self.driver.switch_to.default_content() 