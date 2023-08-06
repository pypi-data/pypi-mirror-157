from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from pyallied.web.webWaits import customwebDriverwait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



class DragAndDrop(customwebDriverwait):
    # drag and drop
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        '''
        drag_and_drop(source, target)¶
        Holds down the left mouse button on the source element,
        then moves to the target element and releases the mouse button.
        Args:	
        source: The element to mouse down.
        target: The element to mouse up
        '''
    def dragAndDrop(self, sourcexpath, destinationxpath):
        try:
            SourceelElementPresense=super().WaitFor_PresenseOf_Element_Located(sourcexpath)
            SourceelElementVisibility=super().WaitFor_VisibilityOf_Element_Located(sourcexpath)
            DestinationElementPresense=super().WaitFor_PresenseOf_Element_Located(destinationxpath)
            DestinationElementVisibility=super().WaitFor_VisibilityOf_Element_Located(destinationxpath)
            if(SourceelElementPresense & DestinationElementPresense ):
                if(SourceelElementVisibility & DestinationElementVisibility):
                    sourceElement = self.driver.find_element(By.XPATH, sourcexpath)
                    destination = self.driver.find_element(By.XPATH, destinationxpath)
                    action_chains = ActionChains(self.driver)
                    action_chains.drag_and_drop(sourceElement, destination).perform()
        except Exception as error:
            raise error            
        '''
        drag_and_drop_by_offset(source, xoffset, yoffset)¶
        Holds down the left mouse button on the source element,
        then moves to the target offset and releases the mouse button.
        Args:	
        source: The element to mouse down.
        xoffset: X offset to move to.
        yoffset: Y offset to move to.
        '''
    def dragAndDropByOffset(self, sourcexpath, xoffset, yoffset):
        try:
            SourceelElementPresense=super().WaitFor_PresenseOf_Element_Located(sourcexpath)
            SourceelElementVisibility=super().WaitFor_VisibilityOf_Element_Located(sourcexpath)
            if(SourceelElementPresense):
                if(SourceelElementVisibility):
                    sourceElement = self.driver.find_element(By.XPATH, sourcexpath)

                    action_chains = ActionChains(self.driver)
                    action_chains.drag_and_drop_by_offset(
                        sourceElement, xoffset, yoffset).perform()
        except Exception as error:
            raise error                