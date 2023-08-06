from pyallied.web.webWaits import customwebDriverwait
class DropDownActions(customwebDriverwait):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
    def Uninstall_addon(self,identifier):
        if(self.driver.capabilities['browser_name']=="firefox"):
            self.driver.uninstall_addon(identifier)
        else:
            raise "add option is allowed only on firefox"
    '''
    Installs Firefox addon.

    Returns identifier of installed addon. This identifier can later be used to uninstall addon.

    Parameters:	
    path – Absolute path to the addon that will be installed.

    Usage:	
    driver.install_addon('/path/to/firebug.xpi')
    '''
    def Install_addon(self,path, temporary=False):
        if(self.driver.capabilities['browser_name']=="firefox"):
            self.driver.install_addon(path)
        else:
            raise "install addon is allowed only on firefox"
    
    def Set_context(self,context):
        if(self.driver.capabilities['browser_name']=="firefox"):
            self.driver.set_context(context)
        else:
            raise "set context is allowed only on firefox"
    def Get_firefox_profile(self,context):
        if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.firefox_profile
        else:
            raise "get firefox profile is allowed only on firefox"
    '''def is_headless(self):
        if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.headless
        else:
            raise "is headless? is allowed only on firefox" '''
    def Add_extension(self,extension='webdriver.xpi'):
        if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.firefox_profile.add_extension(extension)
        else:
            raise "Add_extension is allowed only on firefox" 
    '''sets the preference that we want in the profile.'''        
    def Set_preference(self,key, value):
        if(self.driver.capabilities['browser_name']=="firefox"):
            self.driver.firefox_profile.set_preference(key, value)
        else:
            raise "Set_preference is allowed only on firefox"
    '''sets the preference that we want in the profile.'''        
    def get_default_capabilities(self):
        if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.firefox_profile.default_capabilities
        else:
            raise "get_default_capabilities is allowed only on firefox"
    def Update_capabilities(self):
        if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.firefox_profile.update_preferences()
        else:
            raise "get_default_capabilities is allowed only on firefox"                          
    def get_binary_instance(self):
        if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.binary()
        else:
            raise "binary is allowed only on firefox"   
    def Set_accept_untrusted_certs(self):
        if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.firefox_profile.accept_untrusted_certs
        else:
            raise "accept_untrusted_certs is allowed only on firefox"
    def Set_assume_untrusted_cert_issuer(self):
        if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.firefox_profile.assume_untrusted_cert_issuer
        else:
            raise "assume_untrusted_cert_issuer is allowed only on firefox"
    def Get_encoded_Profile(self):
        if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.firefox_profile.encoded
        else:
            raise "Get_encoded_Profile is allowed only on firefox"
    def Get_Profile_path(self):
        if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.firefox_profile.path
        else:
            raise "path is allowed only on firefox"
    def Get_Profile_DEFAULT_PREFERENCES(self):
        if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.firefox_profile.DEFAULT_PREFERENCES 
        else:
            raise "DEFAULT_PREFERENCES  is allowed only on firefox"
    def Get_Profile_ANONYMOUS_PROFILE_NAME(self):
        if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.firefox_profile.ANONYMOUS_PROFILE_NAME 
        else:
            raise "ANONYMOUS_PROFILE_NAME is allowed only on firefox"
    def Get_Profile_port(self):
        if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.firefox_profile.port 
        else:
            raise "get port is allowed only on firefox" 
    def Add_command_line_options(self,*args):
        if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.binary.add_command_line_options(*args) 
        else:
            raise "add_command_line_options is allowed only on firefox"
    def kill_Binary_instance(self,*args):
        if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.binary.kill() 
        else:
            raise "kill_Binary_instance is allowed only on firefox"
    def Launch_browser(self,profile, timeout=30):
        if(self.driver.capabilities['browser_name']=="firefox"):
           return self.driver.binary.launch_browser(profile, timeout=30) 
        else:
            raise "Launch_browser is allowed only on firefox"                                                                                                                                                                                                                 