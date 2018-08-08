import json
from pathlib import Path
import os

class rJ():

    def __init__(self, fileName=str):
        self.aFileName = fileName
        self.aFilterData = None
        self.aFile = ''

        if fileName !='' :
           self.createFromFile(fileName)
        

    def createFromFile(self, fileName): 
        try:
            self.aFileName = fileName
            self.aFile = Path(fileName)
            self.aFilterData =json.loads(self.aFile.read_text())
        except Exception as a:
            print(a)
        return self

    def createFromStr(self, jsonData={}):
        try:
            self.aFilterData = json.loads(jsonData)
        except Exception as a:
            print(a)
        return self 

    def createFromObject(self, obj:object):
        return self.createFromStr(json.dumps(obj))

    def isFileNotSet(self):
        return self.aFile is None

    def read(self): 
        return self.aFilterData

    def readPretty(self):
        return json.dumps( self.read(), indent=4, sort_keys=True)

    def save(self):
        try:
            data = self.readPretty()
            Path(self.aFileName).write_text(data)
            self.__init__(self.aFileName)
        except :
            pass

    def delete(self):
        if  self.aFileName != input('Type \'%s\' to delete permanently : '%(self.aFileName)):
            print('Canceled')
            return

        os.remove(self.aFileName)

