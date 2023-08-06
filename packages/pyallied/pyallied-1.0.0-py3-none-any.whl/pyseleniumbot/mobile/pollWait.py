import polling2, time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException

class pollWait:
    def __init__(self,browser):
          self.browser=browser
    def with_findElements_byXpath(self,xpath):
        try:
            polling2.poll(lambda: self.browser.find_elements(AppiumBy.XPATH, xpath),ignore_exceptions=(NoSuchElementException,), step=5, timeout=30)
        except Exception:
            return Exception
    def with_findElement_byXpath(self,xpath):
        try:
            polling2.poll(lambda: self.browser.find_element(AppiumBy.XPATH, xpath),ignore_exceptions=(NoSuchElementException,), step=5, timeout=30)
        except Exception:
            return Exception
           