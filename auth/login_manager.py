import pickle
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginManager:
    def __init__(self):
        logging.info("初始化浏览器...")
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 20)
        logging.info("浏览器初始化完成")
        
    def save_cookies(self, cookies, file_name='cookies.pkl'):
        with open(file_name, 'wb') as f:
            pickle.dump(cookies, f)
    
    def load_cookies(self, file_name='cookies.pkl'):
        if os.path.exists(file_name):
            with open(file_name, 'rb') as f:
                return pickle.load(f)
        return None

    def login(self, username=None, password=None):
        cookies = self.load_cookies()
        if cookies:
            logging.info("发现已保存的cookies，尝试使用cookies登录...")
            self.driver.get('https://mooc.ucas.edu.cn/')
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    logging.warning(f"添加cookie时出错: {str(e)}")
            
            self.driver.refresh()
            
            try:
                time.sleep(5)
                login_buttons = self.driver.find_elements(By.XPATH, '/html/body/div[1]/div[1]/div/a')
                if not login_buttons:
                    logging.info("使用cookies登录成功！")
                    return
                else:
                    logging.info("cookies已过期，需要重新登录...")
            except Exception as e:
                logging.warning(f"检查登录状态时出错: {str(e)}")

        logging.info("开始使用账号密码登录...")
        if username is None:
            username = input("请输入账号：")
        if password is None:
            password = input("请输入密码：")

        self.driver.get('https://mooc.ucas.edu.cn/')
        
        login_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div/a'))
        )
        login_button.click()
        
        username_input = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/section/div[2]/div/div[1]/div/div[1]/div/form[2]/div[1]/div/div/div[1]/input'))
        )
        password_input = self.driver.find_element(By.XPATH, '/html/body/div/section/div[2]/div/div[1]/div/div[1]/div/form[2]/div[1]/div/div/div[2]/input')
        
        username_input.send_keys(username)
        password_input.send_keys(password)
        
        submit_button = self.driver.find_element(By.XPATH, '/html/body/div/section/div[2]/div/div[1]/div/div[1]/div/form[2]/div[3]/div/div/button')
        submit_button.click()
        
        time.sleep(5)
        
        cookies = self.driver.get_cookies()
        self.save_cookies(cookies)
        logging.info("登录成功，Cookies已保存")

    def get_driver(self):
        return self.driver

    def close(self):
        logging.info("关闭浏览器...")
        self.driver.quit()
        logging.info("浏览器已关闭") 