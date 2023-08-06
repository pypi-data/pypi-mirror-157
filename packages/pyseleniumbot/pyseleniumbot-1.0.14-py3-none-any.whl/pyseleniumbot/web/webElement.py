from select import select
from xml.dom.minidom import Element
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from pyseleniumbot.web.webWaits import customwebDriverwait
from selenium.webdriver.remote.webdriver import WebDriver
import cv2
import numpy as np
import easyocr
import matplotlib.pyplot as plt

class common(customwebDriverwait):

    def __init__(self, browser):
        super().__init__(browser)
        self.browser = browser

    def findElementsBy(self, xpath):
        # self.browser.presence_of_all_elements_located(xpath)
        # self.browser.visibility_of_element_located(xpath)
        return self.browser.find_elements(By.XPATH, xpath)

    def findElementBy(self, xpath):
        try:
            self.browser.presence_of_element_located(xpath)
            self.browser.visibility_of_element_located(xpath)
            if(self.browser.presence_of_element_located(xpath)) :
                self.browser.find_element(By.XPATH, xpath)
        except Exception as error:
            raise error        

    def click(self, xpath):
        try:
            elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
            elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresense):
                if(elementVisible):
                    self.browser.find_element(By.XPATH, xpath).click()
        except Exception as error:
            raise error            

    def clear(self, xpath):
        try:
            elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
            elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresense):
                if(elementVisible):
                    self.browser.find_element(By.XPATH, xpath).clear()  
        except Exception as error:
            raise error              
    
    
    def isClickable(self, xpath, index=None):
        # self.browser.visibility_of_element_located(xpath)
        try:
            return WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((xpath)))
        except Exception as error:
            raise error    
    
    '''
    Simulates typing into the element.

    Args:	
    value - A string for typing, or setting form fields. For setting file inputs, this could be a local file path.
    Use this to send simple key events or to fill out form fields:
    form_textfield = driver.find_element(By.NAME, 'username')
                    form_textfield.send_keys("admin")
    This can also be used to set file inputs.

    file_input = driver.find_element(By.NAME, 'profilePic')
    file_input.send_keys("path/to/profilepic.gif")
    # Generally it's better to wrap the file path in one of the methods
    # in os.path to return the actual path to support cross OS testing.
    # file_input.send_keys(os.path.abspath("path/to/profilepic.gif"))
    '''

    def fillField(self, xpath, text):
        try:
            elementPresence = super().WaitFor_PresenseOf_Element_Located(xpath)
            elementVisibility = super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresence):
                if(elementVisibility):
                    self.browser.find_element(By.XPATH, xpath).send_keys(text)
        except Exception as error:
            raise error

    def navigateto(self, urlstring):
        try:
            self.browser.get(urlstring)
        except Exception as error:
            raise error
    '''
        Gets the given attribute or property of the element.

        This method will first try to return the value of a property with the given name. If a property with that name doesn’t exist, it returns the value of the attribute with the same name. If there’s no attribute with that name, None is returned.

        Values which are considered truthy, that is equals “true” or “false”, are returned as booleans. All other non-None values are returned as strings. For attributes or properties which do not exist, None is returned.

        To obtain the exact value of the attribute or property, use get_dom_attribute() or get_property() methods respectively.

        Args:	
        name - Name of the attribute/property to retrieve.
        Example:

        # Check if the "active" CSS class is applied to an element.
        is_active = "active" in target_element.get_attribute("class")
    '''
    def getAttribute(self, xpath,AttributeName):
        try:
            elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
            elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresense):
                if(elementVisible):
                    return self.browser.find_element(By.XPATH, xpath).get_attribute(AttributeName)
        except Exception as error:
            raise error                  
    
    '''
        Gets the given attribute of the element. Unlike get_attribute(), this method only returns 
        attributes declared in the element’s HTML markup.

        Args:	
        name - Name of the attribute to retrieve.
        Usage:	
        text_length = target_element.get_dom_attribute("class")
    '''
    def getDomAttribute(self, xpath,AttributeName):
        try:
            elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
            elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresense):
                if(elementVisible):
                    return self.browser.find_element(By.XPATH, xpath).get_dom_attribute(AttributeName) 
        except Exception as error:
            raise error


    '''
        Gets the given property of the element.

        Args:	
        name - Name of the property to retrieve.
        Usage:	
        text_length = target_element.get_property("text_length")
    '''
    def getProperty(self, xpath,PropertyName):
        try:
            elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
            elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresense):
                if(elementVisible):
                    return self.browser.find_element(By.XPATH, xpath).get_property(PropertyName)
        except Exception as error:
            raise error             
    '''
        Whether the element is visible to a user.
    '''
    def isElementDisplayed(self, xpath):
        try:
            elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
            elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresense):
                if(elementVisible):
                    return self.browser.find_element(By.XPATH, xpath).is_displayed()
        except Exception as error:
            raise error             
    '''
        Returns whether the element is enabled.
    '''
    def isElementEnabled(self, xpath):
        try:
            elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
            elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresense):
                if(elementVisible):
                    return self.browser.find_element(By.XPATH, xpath).is_enabled()  
        except Exception as error:
            raise error
    '''
        Returns whether the element is selected.

        Can be used to check if a checkbox or radio button is selected.
    '''
    def isElementSelected(self, xpath):
        try:
            elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
            elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresense):
                if(elementVisible):
                    return self.browser.find_element(By.XPATH, xpath).is_selected() 
        except Exception as error:
            raise error
    '''
        Saves a screenshot of the current element to a PNG image file. Returns
        False if there is any IOError, else returns True. Use full paths in your filename.
    '''
    def currentElementScreenshot(self, xpath,screenShotSavingPath):
        try:
            elementPresense = super().WaitFor_PresenseOf_Element_Located(xpath)
            elementVisible = super().WaitFor_VisibilityOf_Element_Located(xpath)
            if(elementPresense):
                if(elementVisible):
                    return self.browser.find_element(By.XPATH, xpath).screenshot(screenShotSavingPath)
        except Exception as error:
            raise error            
    # action class

    def actionClick(self, xpath):
        try:
            actions = ActionChains(self.browser)
            
            if(super().WaitFor_PresenseOf_Element_Located(xpath)):
                element = self.browser.find_element(By.XPATH, xpath)
                actions.move_to_element(element).click(element)
                actions.perform()
        except Exception as error:
            raise  error    

    def actionClickandHold(self, xpath=None):
        try:
            actions = ActionChains(self.browser)
            if(xpath != None):
                element = self.browser.find_element(By.XPATH, xpath)
            else:
                element = None
            if(element != None):
                actions.click_and_hold(element)
                actions.perform()
            else:
                actions.click_and_hold()
                actions.perform()
        except Exception as error:
            raise error        

    def moveToElement(self, xpath):
        try:
            actions = ActionChains(self.browser)
            element = self.browser.find_element(By.XPATH, xpath)
            actions.move_to_element(element).perform()
        except Exception as error:
            raise error    

    def moveToElementWithOffset(self, xpath, xoffset, yoffset):
        try:
            actions = ActionChains(self.browser)
            element = self.browser.find_element(By.XPATH, xpath)
            actions.move_to_element_with_offset(element, xoffset, yoffset)
            actions.perform()
        except Exception as error:
            raise error    
    def moveByOffsett(self, xoffset, yoffset):
        try:
            actions = ActionChains(self.browser)
            actions.move_by_offset(xoffset, yoffset)
            actions.perform()
        except Exception as error:
            raise error    
    def actionRelease(self, xpath=None):
        try:
            actions = ActionChains(self.browser)
            if(xpath != None):
                element = self.browser.find_element(By.XPATH, xpath)
            else:
                element = None
            if(element != None):
                actions.release(element)
                actions.perform()

            else:
                actions.release()
                actions.perform()
        except Exception as error:
            raise error        
    

    def keyDown(self, ModifierKey, key, xpath=None):
        try:
            actions = ActionChains(self.browser)
            if(xpath != None):
                element = self.browser.find_element(By.XPATH, xpath)
            else:
                element = None
            if(element != None):
                actions.key_down(ModifierKey, element).send_keys(key)
                actions.perform()
            else:
                actions.key_down(ModifierKey).send_keys(key)
                actions.perform()
        except Exception as error:
            raise error


    def keyUp(self, ModifierKey, key, xpath=None):
        try:
            actions = ActionChains(self.browser)
            if(xpath != None):
                element = self.browser.find_element(By.XPATH, xpath)
            else:
                element = None
            if(element != None):
                actions.key_up(ModifierKey, element).perform()
                
            else:
                actions.key_up(ModifierKey).perform()
        except Exception as error:
            raise error        

    def double_click(self, xpath: None):
        try:
            actions = ActionChains(self.browser)
            if(xpath != None):
                element = self.browser.find_element(By.XPATH, xpath)
            else:
                element = None
            if(element != None):
                actions.double_click(element)
                actions.perform()
            else:
                actions.double_click()
                actions.perform()
        except Exception as error:
            raise error        

    def righttClick(self, xpath=None):
        try:
            actions = ActionChains(self.browser)
            if(xpath != None):
                element = self.browser.find_element(By.XPATH, xpath)
            else:
                element = None
            if(element != None):
                actions.context_click(element)
                actions.perform()
            else:
                actions.context_click()
                actions.perform() 
        except Exception as error:
            raise error               

    def resetActions(self):
        try:
            actions = ActionChains(self.browser)
            actions.reset_actions()
            actions.perform()
        except Exception as error:
            raise error            

    def sendKeys(self, *keys_to_send):
        try:
            actions = ActionChains(self.browser)
            actions.send_keys(keys_to_send)
            actions.perform()
        except Exception as error:
            raise error            

    def sendKeysToElement(self, xpath, *keys_to_send):
        try:
            actions = ActionChains(self.browser)
            element = super().WaitFor_PresenseOf_Element_Located(xpath)
            actions.send_keys_to_element(element, keys_to_send)
            actions.perform()
        except Exception as error:
            raise error    
        '''
        Gets the full document screenshot of the current window as a base64 encoded string
        which is useful in embedded images in HTML.

        Usage:	
        driver.get_full_page_screenshot_as_base64()
        '''
    def get_screenshot_ofcurrentActive_page_in_base64(self):
        try:
            return self.browser.get_full_page_screenshot_as_base64()
        except Exception as error:
            raise error    

        '''
        Saves a full document screenshot of the current window to a PNG image file. Returns
        False if there is any IOError, else returns True. Use full paths in your filename.
        Args:	
        filename: The full path you wish to save your screenshot to. This should end with a .png extension.
        Usage:	
        driver.get_full_page_screenshot_as_file('/Screenshots/foo.png')
        '''
    def get_screenshot_ofcurrentActive_page_asFile(self,filename:str):
        try:
            return self.browser.get_full_page_screenshot_as_file(filename) 
        except Exception as error:
            raise error       
        '''get_full_page_screenshot_as_png() → str
        Gets the full document screenshot of the current window as a binary data.

        Usage:	
        driver.get_full_page_screenshot_as_png()
        '''
    def get_screenshot_ofcurrentActive_page_asPNG(self):
        try:
            return self.browser.get_full_page_screenshot_as_png()
        except Exception as error:
            raise error    

        ''' 
        Saves a screenshot of the current window to a PNG image file. Returns
        False if there is any IOError, else returns True. Use full paths in your filename.
        Args:	
        filename: The full path you wish to save your screenshot to. This should end with a .png extension.
        Usage:	
        driver.save_screenshot('/Screenshots/foo.png')
        '''
    def screenshot_save_full_page_screenshot(self,filename):
        try:
            return self.browser.save_screenshot(filename)
        except Exception as error:
            raise error    

    '''
    returns the embedded text in the image.
    It returns a list of detected text, with each text element containing three types of information. 
    Which are: the text, its bounding box vertices, and the confidence level of the text detection
    '''    
    def get_embeddedText_from_image(self,path:str):
        try:
            reader= easyocr.Reader(['en'])
            return reader.readtext(path)
        except Exception as error:
            raise error        
    