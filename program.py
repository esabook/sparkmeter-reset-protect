from model.website import sparkWebsite
from utils.log import log
from utils.setting import setting as s
from utils.telegram_bot import telegram_bot as tb

import datetime, time, os

currentWebsiteSession = sparkWebsite()

def do_resetprotect(arg):
		'''
		non verbose to reset protect of single meter serial on current login session,

		'''
		retries = True
		while retries:
			try:
				br =  currentWebsiteSession.METER.resetMeter(arg)
				retries = False
                
				return br._states != -1
			except Exception as e:
				print(e)
                
				return False
					
def do_findingProtectedMeterAndReset(profile):
    #1 flag for current base url from setting
    print('\n' + profile['baseurl']+'\t:')

    
    files = os.listdir()
    for fl in files:
        if fl.endswith(".csv"):
            os.remove(fl)
   
       
    #2 get meter status, failure retry count
    retriesCount = s().Data['retry_count_strategy']

    while retriesCount > 0:
        try:
             #3 loging in
            currentWebsiteSession   = sparkWebsite(profile['baseurl'], profile['username'], profile['password'])
            meterStates             = currentWebsiteSession.METER.getReadLatestState()['readings']

            state       = 'state'
            sn          = 'serial'
            addr        = 'address'
            iii         = 0

            telegramMessage = []
            # finding meter
            for meterstate in meterStates:

                #filter by protect and totalizer SN
                if str(meterstate[state]).lower() == "protect" and str(meterstate['serial']).find('SM100E')<0:
                	iii += 1
                	gb = meterstate['ground_name']
                    
                	print('%s Reset for SN: %-25s ADDR: %-50s on GB: %-50s ' %
                	      (iii, meterstate[sn], meterstate[addr], gb))

                    # do reset
                	if do_resetprotect(meterstate[sn]):
                          currentLog = log(meterstate)
                          fn = currentLog.saveLogToCSV(gb,  datetime.datetime.utcnow())
                          telegramMessage.append('\n%s\t %s\t %s\t %s' % (meterstate[sn], meterstate['ground_name'], meterstate[addr], meterstate['heartbeat_end'] ))
                          currentLog.saveCSVtoSQLDB(gb)
                          currentLog.saveCsvLogToBlob(fn)

            if len(telegramMessage) > 0:
                messg = '%s (%s meter/s)\n %s' % ( profile['baseurl'], len(telegramMessage), str('\n').join(telegramMessage) )
                tb().sendMessageToAllRegisteredChannel(messg)
                telegramMessage.clear()
            
            retriesCount            = 0
        except Exception as e :
            print(e)
            retriesCount           -= 1

   


            







if __name__ == "__main__":

    # Read setting
    sparkCloudCredentials = s().Data['credentials']

    start_time  = datetime.datetime.now()
    runs        = True

    # while runs:
        # delay
        # while datetime.datetime.now() < start_time:
            # time.sleep(15)

    for profile in sparkCloudCredentials:
		#0 skip disabled config
        if profile.get('disabled', False):
        	    continue

        do_findingProtectedMeterAndReset(profile)
        
        
        
        # start_time = datetime.datetime.now() + datetime.timedelta( seconds = s().Data['delayed_thread_seconds'] )
        # print("Sleep until %s" % (start_time) )

		
				   
