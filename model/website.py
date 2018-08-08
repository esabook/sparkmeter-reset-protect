from robobrowser import RoboBrowser
from controller.meterController import meterController
from controller.loginController import login

class sparkWebsite():
    
    def __init__(self, url=None, email=None, password=None):
        'Sparkmeter Website'
        #super(sparkWebsite, self).__init__(base_url=url,email=email, password=password)

        self.LOGIN_iNFO  = login(base_url=url,username=email, password=password)
        self.METER      = meterController(self.LOGIN_iNFO)

    
        

    
