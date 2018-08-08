from .loginController import login

from enum import Enum

import json
import http.client, urllib
from bs4 import BeautifulSoup

class meterState(Enum):
    off= 0
    on = 1
    auto=2


class meterController():

    def __init__(self, loginSession: login):
        'Initializer with RoboBrowser object, to scapping meters from available login session'
        self.LOGIN_iNFO = loginSession
        self.BROWSER = loginSession.BROWSER
        self.METER_JSONCOLLECTION = {'meters':[]}
        self.METER_FILTER = {}
        self.MAIN_uRL = None

    def read(self):
        'Read current `METER_JSONCOLLECTION`'
        return self.METER_JSONCOLLECTION
    def getReadLatestState(self):
        '''
        read latest reading meter state

        '''
        br = self.BROWSER
        self.MAIN_uRL = br.url if self.MAIN_uRL is None else self.MAIN_uRL
        if  br._cursor == -1 : return self
        grab_latest_state_url = br.url+"/readings/latest.json" 
        br.open(grab_latest_state_url)
        content = json.loads(br.response.text)

        return content

    def getAllMeterInfo(self):
        'Get all available meters on sparkmeter server, return object of myself'
        # 1 
        br = self.BROWSER
        if  br._cursor == -1 : return self

        self.MAIN_uRL = br.url+"/meter/" if self.MAIN_uRL is None else self.MAIN_uRL
        grab_meter_url = self.MAIN_uRL + 'meters.json?meter_type=customer'

        # 2 
        print(grab_meter_url)
        br.open(grab_meter_url)
        content = json.loads(br.response.text)

        # 3
        content['main_url'] = self.MAIN_uRL

        self.METER_JSONCOLLECTION = content
        return self

    def getDetailOfAllMeterlInfo(self, **kwargs):
        meters = self.METER_JSONCOLLECTION
        tempDetailInfo = []

        for meter in meters['meters']:
            param = {**{'address_coords':'address-coords', 'customer_code':'customer-code'},**kwargs}
            detailInfo = self.getGrabDetailedMeterInfoByScrapping(meter['meter_serial'], **param)
            meter = {**meter, **detailInfo}
            tempDetailInfo.append(meter)
        
        meters["meters"] = tempDetailInfo
        self.METER_JSONCOLLECTION = meters
        return self

    #TODO: need optimizing
    def getGrabDetailedMeterInfoByScrapping(self, meterserial, **kwargs):
        returnBrowser = self.BROWSER
        if  returnBrowser._cursor == -1 : return returnBrowser
        
        mainUrl=self.read()['main_url']
        set_meter_url = mainUrl + meterserial
        returnBrowser.open(set_meter_url)
		
        bs = BeautifulSoup(returnBrowser.response.text, 'lxml')
        returnDict = {}
        for arg in kwargs:
            returnDict[arg] = bs.find('dd', id=kwargs[arg]).text

        return returnDict

    def getMeterDetailInfo(self, meterserial):
        'Get all available meters on sparkmeter server, return object of myself'
        # 1 
        br = self.BROWSER
        if  br._cursor == -1 : return self

        self.MAIN_uRL = br.url if self.MAIN_uRL is None else self.MAIN_uRL
        grab_meter_url = self.MAIN_uRL + meterserial +'/jsondata'
    
        # 2 
        br.open(grab_meter_url)
        content = json.loads(br.response.text)
        return content['meter']
        
    def getMeterInfo(self,  filterJson=None, useFilter: bool=False):
        'Return `getAllMeterInfo()` but selected meters is based on filter'
        self.getAllMeterInfo()
        meters = self.METER_JSONCOLLECTION
        tempFilteredMeter=[]

        #4
        if not useFilter or filterJson is None or len(filterJson)==0:
            self.METER_JSONCOLLECTION = meters
        else:
            for meter in meters['meters']:
                if self.__compareMeterWithFilter(meter, filterJson):
                    tempFilteredMeter.append(meter)
           
            meters['meters']=tempFilteredMeter
            self.METER_JSONCOLLECTION = meters
        
        return self

    def changeAllMeterCredit(self, amountTarget:float, currentMaximumAmount:float):
        '''
        
        Change credit for all meters on current `METER_JSONCOLLECTION` to `amountTarget` and `currentMaximumAmount` filter.
        You can selects meter target with `getMeterInfo` and set filter 
        
        '''
        
        meterInfo = self.METER_JSONCOLLECTION
        if not hasattr(meterInfo,"__getitem__") : return
            
        # 1 iterate all available meter
        for meter in meterInfo['meters']:
            credit = meter['meter_credit_value']
            serial = meter['meter_serial']		
			
            if credit < currentMaximumAmount and credit < amountTarget :
			
				# 2  set meter credit
                print('Meter: %-45s from %-30s => add %-20s ' % (serial, credit, abs(amountTarget-credit)),end = "")			
                try:
                    br = self.changeMeterCredit(serial, abs( amountTarget - credit)) 
                except Exception as e:
                    print(e)
                print('http response: %s' % (br.response.status_code))
				
            else:
                print('Meter: %-45s from  %-56s PASS' % (serial, credit))

    def reverse(self, trxIdArray):
        br = self.BROWSER
        self.MAIN_uRL = br.url if self.MAIN_uRL is None else self.MAIN_uRL
        url = self.MAIN_uRL+'transaction/'+trxIdArray+'/reverse'
        print(url)
        try:
            br.open(url)
        except Exception as e:
            print(e)
    def changeAllMeterState(self, newMeterState:str):
        '''
        
        Change meter state for all meters on current `METER_JSONCOLLECTION` to `newMeterState`.
        You can selects meter target with `getMeterInfo` and set filter 
        
        '''
        
        meterInfo = self.METER_JSONCOLLECTION
        if not hasattr(meterInfo,"__getitem__") : return
            
        # 1 iterate all available meter
        for meter in meterInfo['meters']:
            retries = True
            while retries:
                try:
                    currentState = meter['meter_state']
                    serial = meter['meter_serial']		

                    # 2  set meter state
                    print('Meter: %-45s from %-30s => to %-20s ' % (serial, currentState, newMeterState), end = "")			

                    br = self.changeMeterState(serial, newMeterState) 
                    print('http response: %s' % (br.response.status_code))
                    retries  = False
                except Exception as e:
                    print(e)
        
    def changeAllMeterTariff(self, TarifID:str):
        '''Change meter state for all meters on current `METER_JSONCOLLECTION` to `newMeterState`.
        You can selects meter target with `getMeterInfo` and set filter '''
        
        meterInfo = self.METER_JSONCOLLECTION
        if not hasattr(meterInfo,"__getitem__") : return
            
        # 1 iterate all available meter
        for meter in meterInfo['meters']:
            retries = True
            while retries:
                try:
                    currentTariff = meter['tariff_name']
                    serial = meter['meter_serial']		
            
                    # 2  set meter credit
                    print('Meter: %-45s from %-30s => to %-20s ' % (serial, currentTariff, TarifID), end = "")			

                    br = self.changeMeterTarif(serial, TarifID) 
                    print('http response: %s' % (br.response.status_code))
                except Exception as e:
                    print(e)
            
				
        

    def changeMeterCredit(self, meter_serial:str, amount:float):
        'Change `amount` meter credit to `meter_serial` (as meter), return RoboBrowser object after sending request'
        br = self.BROWSER
        if  br._cursor == -1 : return br
        
        mainUrl=self.read()['main_url']
        set_meter_url = mainUrl + meter_serial +'/transaction'
        br.open(set_meter_url)
		
        form = br.get_form(id='transaction_form')
        # form['vendor'].value = form['vendor'].options[0].value,				#first customer id, semi-hardcoded

       				                
        # for p in form['account'].options:
        #     if 'kur' in br.find(value=p).string:
        #         form['account'].value = p
        
        form['acct_type'].value = 'credit'
        form['source'].value = form['source'].options[2]	
        form['amount'].value = amount
        
        br.submit_form(form)
        return br

    def changeMeterState(self, meter_serial:str, relayState:str):
        br = self.BROWSER
        if  br._cursor == -1 : return br
        
        mainUrl=self.read()['main_url']
        url = mainUrl + meter_serial +'/set-state'
        #bodyParams = urllib.parse.urlencode({'state': relayState})

        response =br.session.post(url,None, json={'state': relayState})
        br._update_state(response)

        return br
    
    def changeMeterTarif(self, meter_serial:str, tarif:str):
        returnBrowser = self.BROWSER
        if  returnBrowser._cursor == -1 : return returnBrowser
        
        mainUrl=self.read()['main_url']
        set_meter_url = mainUrl + meter_serial +'/edit'
        returnBrowser.open(set_meter_url)
		
        form = returnBrowser.get_form(class_='form form-horizontal')
        if tarif in form['tariff'].options :
            form['tariff'].value = tarif
            returnBrowser.submit_form(form)

        
        return returnBrowser

    def editMeterInfo(self, meterserial:str, **kwargs):
        
        #mapp = ["address-street1", "address-street2", "address-city","address-state", "address-postalcode", "address-country", "address-coords", "customer-name", "customer-code"]
       
        returnBrowser = self.BROWSER
        if  returnBrowser._cursor == -1 : return returnBrowser
        
        mainUrl=self.read()['main_url']
        set_meter_url = mainUrl + meterserial +'/edit'
        returnBrowser.open(set_meter_url)
		
        form = returnBrowser.get_form(class_='form form-horizontal')
        for key, value in kwargs.items():
            #TODO: add support optionz
            try:
                if str(key) == 'tariff_name':
                    key = 'tariff'
                    for p in form[str(key)].options:
                        if returnBrowser.find(value=p).string == value:
                            value = p
                if str(key) == 'meter_state':
                    key = 'state'
                    value = str(value)
                    
                form[str(key)].value = value
            except:
                pass
        
        returnBrowser.submit_form(form)
        return returnBrowser
    
    def resetMeter(self, meter_serial):
        br = self.BROWSER
        if  br._cursor == -1 : return br
        
        mainUrl=self.MAIN_uRL if self.MAIN_uRL is not None else br.url
        url = mainUrl + "/meter/" + meter_serial +'/reset-meter'

        br.open(url)

        return br














    def __compareMeterWithFilter(self, meterInfo, filterJson:json):
        '''Return true if given `meterInfo` is matches of `filterJson`'''		
        condition = True

        try:
            for met in filterJson.keys():
               
                try:
                    op =  met.split('_?') if '_?' in met else [met,None]
                    if op[0] not in meterInfo: continue

                    mval = meterInfo[op[0]]
                    fval = filterJson[met]
                    try:
                        mval = mval.lower()
                        fval = fval.lower()
                    except:
                        pass

                    condition = self.__compare(mval, op[1], fval) and condition
                except :
                    pass
        except:
            pass
		
        return condition

    def __compare(self,left, operator, right):
        'comparator method to compare given value of `left` and `right` by string of `operator`. Return true/false'

        if	operator == '<'  : return left <    right
        if	operator == '<=' : return left <=   right
        if	operator == '> ' : return left >    right
        if	operator == '>=' : return left >=   right
        if	operator == '!=' : return left !=   right	
        if	operator == '==' : return left ==   right	
        if	operator == '%-' : return left in  right	
        if	operator == '-%' : return right in left
        if	operator == '%!' : return left not in  right	
        if	operator == '!%' : return right not in left
        return right == left
