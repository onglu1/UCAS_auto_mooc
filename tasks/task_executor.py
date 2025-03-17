import logging
from abc import ABC, abstractmethod

class TaskExecutor(ABC):
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    @abstractmethod
    def execute(self, task_info):
        """
        执行任务的抽象方法
        """
        pass

    def switch_to_default(self):
        """
        切换回主文档
        """
        self.driver.switch_to.default_content() 