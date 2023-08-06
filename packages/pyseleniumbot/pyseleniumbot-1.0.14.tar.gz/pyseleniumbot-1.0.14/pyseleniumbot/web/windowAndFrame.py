from select import select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from pyseleniumbot.web.webWaits import customwebDriverwait

class frameAndWindow(customwebDriverwait):

    def __init__(self, browser):
        #self.browser = browser
        super().__init__(browser)
        self.browser=browser

    # switch to window
    # ex: <a href="somewhere.html" target="windowName">Click here to open a new window</a>

    def switchToWindowUsingName(self, windowName):
        try:
            self.browser.switch_to_window(windowName)
        except Exception as error:
            raise error
    def switchtoWindowUsingHandle(self, windowNumber):
        try:
            current_window = self.browser.current_window_handle
            ListOfHandles = self.browser.window_handles
            if(current_window != ListOfHandles[windowNumber]):
                self.browser.switch_to.window(ListOfHandles[windowNumber])
        except Exception as error:
            raise error                
    # frame switch, It’s possible to access subframes by separating the path with a dot,
    # and you can specify the frame by its index too. That is: driver.switch_to_frame("frameName.0.child")
    # would go to the frame named “child” of the first subframe of the frame called “frameName”. All frames are evaluated as if from *top*.

    def swithToFrame(self, xpath):
        try:
            super().WaitFor_frame_to_be_available_and_switch_to_it(xpath)
        except Exception as error:
            raise error        
    # Once we are done with working on frames, we will have to come back to the parent
    # frame which can be done using:

    def swithToParentFrame(self):
        try:
            self.browser.switch_to_default_content()
        except Exception as error:
            raise error            
    # navigating
