from select import select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome import service
from pyseleniumbot.web.webWaits import customwebDriverwait
class browserAlerts(customwebDriverwait):

    def __init__(self, browser):
        super().__init__(browser)
        self.browser = browser



    #alerts
    # Use this class to interact with alert prompts. 
    # It contains methods for dismissing, accepting, inputting, and getting text from alert prompts.   
    def acceptAlert(self):
        try:
            alertPresence= super().WaitForAlert_is_present()
            if(alertPresence):
                Alert(self.browser).accept()
        except Exception as error:
            raise error                
    def dismissAlert(self):
        try:
            alertPresence= super().WaitForAlert_is_present()
            if(alertPresence):
                Alert(self.browser).dismiss() 
        except Exception as error:
            raise error                
    def getAlertText(self):
        try:
            alertPresence= super().WaitForAlert_is_present()
            if(alertPresence):
                alertText=Alert(self.browser).text
                return alertText
        except Exception as error:
            raise error                
    def sendKeystoAlert(self,keysToSend):
        try:
            alertPresence= super().WaitForAlert_is_present()
            name_prompt = Alert(self.browser)
            name_prompt.send_keys(keysToSend)
        except Exception as error:
            raise error            
    # Special Keys
    #The Keys implementation.
    ''' yet to complete'''
    #Touch Actions
    ''' yet to complete'''






