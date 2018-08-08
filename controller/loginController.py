from robobrowser import RoboBrowser

class login():

    BROWSER     = RoboBrowser()
    USERNAME       = ''
    PASSWORD    = ''
    URL         = ''
    TOKEN       = ''
    API_ENDPOINT= ''
    def __init__(self, base_url=None, username=None, password=None):
        '''
        
        Login to sparkmeter website
        
        '''

        if base_url is not None and username is not None and password is not None:
           self.login(base_url, username, password)


    def isOnLogin(self):
        '''
        
        Return true if current login session available
        
        '''
        if self.BROWSER._cursor == -1: return False
        return '/login' not in self.BROWSER.url

    def reLogin(self):
        '''
        
        Relogin again to sparkmeter if current session is outdate/timeout
        
        '''
        self.login(self.URL, self.USERNAME, self.PASSWORD)
        
    def login(self,  base_url, username, password):
        '''
        
        Login action to `base_url` with given `username` and `password`
        
        '''
        try:
            self.BROWSER = RoboBrowser(parser='lxml') 
            self.USERNAME = username
            self.PASSWORD = password
            self.URL = base_url

		    #1
            self.BROWSER.open(base_url)

    	    #2
            form = self.BROWSER.get_form(action='/login')
            form['email'].value = username
            form['password'].value = password
            self.BROWSER.submit_form(form)
        except Exception as e:
            print(e)
        
  
        return self