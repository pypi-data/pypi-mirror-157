from typing import Dict
from selenium.webdriver.common.utils import is_url_connectable
from selenium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.protocols.webdriver.can_execute_scripts import CanExecuteScripts
import polling2
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotVisibleException


class mobAppium:
    def __init__(self, browser):
        self.browser = browser
        '''
        Returns information about whether a remote end is in a state in which it can create new sessions 
        and can additionally include arbitrary meta information that is specific to the implementation.
        usage: selenium.webdriver.common.utils.is_url_connectable(port)


        '''

    def get_Remote_Driver_Status(self, port):
        self.browser.is_url_connectable(port)

        '''
        Execute a variety of native, mobile commands that aren't associated with a specific endpoint

        Syntax is execute("mobile: <commandName>", <JSON serializable argument>)
        
        useage: self.driver.execute_script("mobile: scroll", {'direction': 'down'})


        '''

    def execute_Mobile_Command(self, Mobilecommand: str, parameters: Dict[str, any]):
        self.browser.execute_script(Mobilecommand, parameters)
        '''
        The server should attempt to create a session that most closely matches the desired and required capabilities.

        JSONWP Spec Required capabilities have higher priority than desired 
        capabilities and must be set for the session to be created
        W3C Spec capabilities.alwaysMatch must be set for session to be created; 
        capabilities.firstMatch must match at least one (the first one to match will be used)

        useage:
        desired_caps = {
            'platformName': 'Android',
            'platformVersion': '7.0',
            'deviceName': 'Android Emulator',
            'automationName': 'UiAutomator2',
            'app': PATH('/path/to/app')
            }
        self.driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desired_caps)

        '''

    def create_NewSession(self, hostAddress: str, desired_caps: Dict[str, str]):
        self.browser = webdriver.Remote(hostAddress, desired_caps)
        '''
        end the session
        '''

    def end_Session(self):
        self.browser.quit()
        ''' Returns dict of capabilities '''

    def get_Session_Capabilities(self):
        desired_caps = self.browser.session
        ''' 
        Navigate backwards in the browser history, if possible (Web context only)

        '''

    def go_Back(self):
        self.browser.back()
        '''
        Take a screenshot of the current viewport/window/page
        Takes a screenshot of the viewport in a native context (iOS, Android) and 
        takes a screenshot of the window in web context

        Note that some platforms may have settings that prevent screenshots from being taken, 
        for security reason. One such feature is the Android FLAG_SECURE layout parameter


        '''

    def take_screenshot(self):
        screenshotBase64 = self.browser.get_screenshot_as_base64()
        return screenshotBase64

        '''
        Get the current application hierarchy XML (app) or page source (web)
        In a web context, the source returns the source HTML of the current window. 
        In a native context (iOS, Android, etc...) it will return the application hierarchy XML.

        This method is useful for inspecting your application hierarchy and using that to write selectors

        (NOTE: iOS and Android don't have standard ways of defining their application source, 
        so on calls to 'Get Page Source' Appium traverses the app hierarchy and creates an XML document. 
        Thus, getting the source can often be an expensive and time-consuming operation)


        '''

    def get_PageSource(self):
        source = self.browser.page_source
        return source
        '''
        Configure the amount of time that a particular type of operation can execute for before they are aborted


        '''

    def set_PageLoad_Timeout(self, timeout: int):
        self.browser.set_page_load_timeout(timeout)

        '''Set the amount of time, in milliseconds, that asynchronous scripts executed by execute async are 
        permitted to run before they are aborted (Web context only)
        
        '''

    def set_scriptLoad_Timeout(self, timeout: int):
        self.browser.set_script_timeout(timeout)
        '''
        Set the amount of time the driver should wait when searching for elements
        '''

    def set_Implicit_Wait_Timeout(self, timeout: int):
        self.browser.implicitly_wait(5)  # waits 5 seconds
        '''
        Inject a snippet of JavaScript into the page for execution in the context of the currently 
        selected frame (Web context only)
        
        Args:	
        script: The JavaScript to execute.
        *args: Any applicable arguments for your JavaScript.
        Usage:	
        script = "var callback = arguments[arguments.length - 1]; " \
                "window.setTimeout(function(){ callback('timeout') }, 3000);"
        driver.execute_async_script(script
        '''

    def execute_Async_Script(self, script: str, *args):
        self.browser.execute_async_script(script)

        '''
        execute_script(script, *args)¶
        Synchronously Executes JavaScript in the current window/frame.

        Args:	
        script: The JavaScript to execute.
        *args: Any applicable arguments for your JavaScript.
        Usage:	
        driver.execute_script('return document.title;')
        '''

    def execute_Script(self, script: str, *args):
        self.browser.execute_script(script)
        '''
        Get the current device/browser orientation
        '''

    def get_Orientation(self):
        orientation = self.driver.orientation
        return orientation
        '''
        Set the current device/browser orientation
        '''

    def set_Orientation(self, orientation: str):
        self.browser.orientation = orientation

        '''
        Get the current geo location
        '''

    def get_geoLocation(self):
        location = self.browser.location()
        return location

    def find_elementBy(self, locatorType, locator):
        locatorType=locatorType
        locator=locator        
        return mobAppium.__with_findElement(self,locatorType, locator)

    def find_elementBy(self, locatorType: str, locator: any):
        locatorType=locatorType
        locator=locator
        print (mobAppium.__with_findElements(self,locatorType, locator))
        return mobAppium.__with_findElements(self,locatorType, locator)

    def __with_findElements(self, locatorType, locator):

        if locatorType == "XPATH":
            try:
                elements = polling2.poll(lambda: self.browser.find_elements(AppiumBy.XPATH, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return elements
            except Exception:
                return Exception
        if locatorType == "ANDROID_UIAUTOMATOR":
            try:
                elements = polling2.poll(lambda: self.browser.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return elements
            except Exception:
                return Exception
        if locatorType == "ANDROID_VIEWTAG":
            try:
                elements = polling2.poll(lambda: self.browser.find_elements(AppiumBy.ANDROID_VIEWTAG, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return elements
            except Exception:
                return Exception
        if locatorType == "ANDROID_DATA_MATCHER":
            try:
                elements = polling2.poll(lambda: self.browser.find_elements(AppiumBy.ANDROID_DATA_MATCHER, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return elements
            except Exception:
                return Exception
        if locatorType == "ANDROID_VIEW_MATCHER":
            try:
                elements = polling2.poll(lambda: self.browser.find_elements(AppiumBy.ANDROID_VIEW_MATCHER, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=5, timeout=30)
                return elements
            except Exception:
                return Exception
        if locatorType == "ACCESSIBILITY_ID":
            try:
                elements = polling2.poll(lambda: self.browser.find_elements(AppiumBy.ACCESSIBILITY_ID, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return elements
            except Exception:
                return Exception
        if locatorType == "IMAGE":
            try:
                elements = polling2.poll(lambda: self.browser.find_elements(AppiumBy.IMAGE, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return elements
            except Exception:
                return Exception

    def __with_findElement(self, locatorType, locator):

        if locatorType == "XPATH":
            try:
                element = polling2.poll(lambda: self.browser.find_element(AppiumBy.XPATH, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                
                return element
            except Exception:
                #print(Exception,'--------------------')
                return Exception
        if locatorType == "ANDROID_UIAUTOMATOR":
            try:
                element = polling2.poll(lambda: self.browser.find_element(AppiumBy.ANDROID_UIAUTOMATOR, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return element
            except Exception:
                return Exception
        if locatorType == "ANDROID_VIEWTAG":
            try:
                element = polling2.poll(lambda: self.browser.find_element(AppiumBy.ANDROID_VIEWTAG, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return element
            except Exception:
                return Exception
        if locatorType == "ANDROID_DATA_MATCHER":
            try:
                element = polling2.poll(lambda: self.browser.find_element(AppiumBy.ANDROID_DATA_MATCHER, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return element
            except Exception:
                return Exception
        if locatorType == "ANDROID_VIEW_MATCHER":
            try:
                element = polling2.poll(lambda: self.browser.find_element(AppiumBy.ANDROID_VIEW_MATCHER, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=5, timeout=30)
                return element
            except Exception:
                return Exception
        if locatorType == "ACCESSIBILITY_ID":
            try:
                element = polling2.poll(lambda: self.browser.find_element(AppiumBy.ACCESSIBILITY_ID, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return element
            except Exception:
                return Exception
        if locatorType == "IMAGE":
            try:
                element = polling2.poll(lambda: self.browser.find_element(AppiumBy.IMAGE, locator), ignore_exceptions=(
                    ElementNotVisibleException, NoSuchElementException, StaleElementReferenceException), step=0.5, timeout=30)
                return element
            except Exception:
                return Exception
