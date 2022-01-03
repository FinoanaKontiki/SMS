from .chrome import chrome
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
import imgkit
import time

class image():
    def __init__(self):
        self.driver = chrome().driver()
        self.wait = ui.WebDriverWait(self.driver, timeout=10000)
        
    def capture(self, source):
        self.driver.get(source)
        self.wait.until(EC.presence_of_all_elements_located((By.XPATH,"/html/body")))
        time.sleep(2)
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        # element = soup.find('div',attrs={'class':'kdev'})
        element = soup.find('body')
        config = imgkit.config(wkhtmltoimage="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltoimage.exe")
        options = {'format': 'png', 'width': '640'}
        imgkit.from_string(str(element), "C:\\PROJECT\\DOC\\capture\\kdev.png", config=config, options=options)
        # imgkit.from_file(source, "C:\\PROJECT\\DOC\\capture\\and.png", options=options, config=config)
        
        # img= self.driver.find_element_by_xpath("/html/body").screenshot_as_png
        # with open("C:\\PROJECT\\DOC\\capture\\test2.png", "wb") as file:
        #     file.write(img)
        # img= self.driver.find_element("xpath",'//*[@id="templateUpperBody"]/table/tbody/tr/td/table[1]/tbody/tr[2]/td')
        
        
        # height = self.driver.execute_script('return document.body.parentNode.scrollHeight')
        # time.sleep(1)
        # print(height,'--------------')
        # total_height = int(height)+500
        # self.driver.set_window_size(1920, total_height)
        # self.driver.save_screenshot("C:\\PROJECT\\DOC\\capture\\tsotra.png")
        
        