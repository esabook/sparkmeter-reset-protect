from azure.storage import CloudStorageAccount
from azure.storage.blob import BlockBlobService, PublicAccess, AppendBlobService

from pathlib import Path
from utils.setting import setting as s
import json, csv, datetime, os, pyodbc, datetime




    
class log():
    def __init__(self, meterInfo):
        self.MeterInfo = meterInfo
        self.fileName = ''

    def progress_callback_w(self, current, total):

        if current == total:
            try:
                os.remove(self.fileName)
            except:
                pass

    def saveLogToCSV(self, siteName, logdate):
        '''
        return filename
        '''
        
        fileName = '%s_reset-log_%s.csv' % (siteName, logdate)
        self.fileName = fileName.replace(":","-")
        
        header = []
        for key in self.MeterInfo.keys():
            header.append(key)
        
        mode = 'a' if Path(self.fileName).exists() else 'w'
        with open(self.fileName, mode , newline='') as mFile:
        	out = csv.DictWriter(mFile, dialect='excel', fieldnames=header, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        	if mode=='w':
        		out.writeheader()
        	out.writerow(self.MeterInfo)
        return self.fileName

    def saveCsvLogToBlob(self, fileName):

        to_location_path = fileName

        account_name = s().Data["blob"]["account_name"] 
        account_key = s().Data["blob"]["account_key"]
        container_name = s().Data["blob"]["container"]

        cloud_account = CloudStorageAccount( account_name = account_name, account_key = account_key )
    
        append_blob_service = cloud_account.create_append_blob_service()
        append_blob_service.create_container(container_name)
        append_blob_service.set_container_acl( container_name, public_access = PublicAccess.Container )

        if append_blob_service.exists(container_name, self.fileName):
            append_blob_service.append_blob_from_path(container_name, self.fileName, self.fileName, progress_callback = self.progress_callback_w)
        else:
            cloud_account.create_block_blob_service().create_blob_from_path(container_name, self.fileName, to_location_path, progress_callback = self.progress_callback_w)    
   

    def saveCSVtoSQLDB(self, siteName):
        cnxn = pyodbc.connect(s().Data['mssql'])
        cursor = cnxn.cursor()
        query = '''
                        Insert into SPARKMETER_RESET_PROTECT_LOG 
                        (
                            [address]
                            ,[current_avg]
                            ,[current_max]
                            ,[current_min]
                            ,[energy]
                            ,[frequency]
                            ,[ground_name]
                            ,[ground_serial]
                            ,[heartbeat_end]
                            ,[serial]
                            ,[state]
                            ,[true_power_inst]
                            ,[uptime]
                            ,[user_power_limit]
                            ,[voltage_avg]
                            ,[voltage_max]
                            ,[voltage_min]
                            ,[access_user]
                            ,[reset_datetime_utc])
                        values(
                            '%s',
                            %s, 
                            %s,
                            %s,
                            
                            %s,
                            %s,
                            '%s',
                            '%s',

                            '%s',
                            '%s',
                            '%s',
                            %s,

                            %s,
                            %s,
                            %s,
                            %s,
                            
                            %s,
                            '%s',
                            '%s0'
                            
                            
                        )
                       ''' % (
                            self.MeterInfo["address"],
                            self.MeterInfo["current_avg"],
                            self.MeterInfo["current_max"],
                            self.MeterInfo["current_min"],

                            self.MeterInfo["energy"],
                            self.MeterInfo["frequency"],
                            self.MeterInfo["ground_name"],
                            self.MeterInfo["ground_serial"],

                            self.MeterInfo["heartbeat_end"],
                            self.MeterInfo["serial"],
                            self.MeterInfo["state"],
                            self.MeterInfo["true_power_inst"],

                            self.MeterInfo["uptime"],
                            self.MeterInfo["user_power_limit"],
                            self.MeterInfo["voltage_avg"],
                            self.MeterInfo["voltage_max"],

                            self.MeterInfo["voltage_min"],
                	        s().Data['program_name'],
                	        datetime.datetime.utcnow().isoformat()
                           )
        cursor.execute(query)

        cursor.commit()

