from selenium import webdriver

class chrome(object):
    def __init__(self):
        pass
    
    def driver (self):
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--start-maximized')
        driver_location = "C:\\PROJECT\\Driver\\chromedriver.exe"
        driver = webdriver.Chrome(executable_path=driver_location, options=chrome_options)
        driver.set_window_position(0, 0)
        driver.set_window_size(2000, 2000)
        return driver
    
      
        