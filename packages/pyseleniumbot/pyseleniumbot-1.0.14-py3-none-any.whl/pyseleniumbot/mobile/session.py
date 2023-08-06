from tkinter import COMMAND
from typing import Union
from click import command
from pyseleniumbot.mobile.pollWait import pollWait
from appium import webdriver 
from appium.webdriver.applicationstate import ApplicationState
from appium.webdriver.extensions.device_time import DeviceTime
from appium.webdriver.extensions.location import Location
from appium.webdriver.extensions.settings import Settings
from appium.protocols.webdriver.can_execute_commands import CanExecuteCommands
from appium.webdriver.applicationstate import ApplicationState
from appium.webdriver.mobilecommand import MobileCommand
from appium.webdriver.appium_connection import AppiumConnection
from selenium.webdriver.remote.switch_to import SwitchTo
class session(pollWait,Location,Settings,CanExecuteCommands,AppiumConnection,MobileCommand,ApplicationState):
    
    def __init__(self, browser):
        super().__init__(browser)
        self.browser = browser
    def page_source(self):
        self.html=self.browser.page_source
        #print(html)
        return self.html
    def is_ServiceRunning(self):
        return self.browser.AppiumConnection.get_timeout()
    def get_Logs(self,type):
        return self.browser.get_log(type)
    def get_WindowRect(self):
        return self.browser.get_window_rect()
    def get_DesiredCaps(self):
        return self.browser.session
    def goBack(self):
        return self.browser.back()
    def take_Screenshot(self):
        screenshotBase64 = self.browser.get_screenshot_as_base64()
        return screenshotBase64
    def get_Orientation(self):
        return self.browser.orientation    
    def set_Orientation(self,orientation):
        self.browser.orientation = str(orientation)
    def get_GeoLocation(self):
        return self.browser.location

        #locationData=Location.location
        #return locationData
    def set_GeoLocation(self, latitude: Union[float, str], longitude: Union[float, str], altitude: Union[float, str] = None, speed: Union[float, str] = None, satellites: Union[float, str] = None):       
        self.browser.set_location(latitude, longitude, altitude)
    def get_Events(self):
        return self.browser.get_events()
    def get_AppStrings(self):
        return self.browser.app_strings()
    def get_DeviceTime(self):
        return self.browser.get_device_time()
    def get_Settings(self):
        return self.browser.get_settings()    
    def get_AvailableIMEengines(self):
        return self.browser.available_ime_engines
    def is_AppInstalled(self):
        return self.browser.is_app_installed()
    def get_battery_info(self):
        return self.browser.battery_info
    def switch_Context(self):
        self.browser.switch_to.context('WEBVIEW_1')
    def get_Contexts(self):
        return self.browser.contexts
        

    

            


         

