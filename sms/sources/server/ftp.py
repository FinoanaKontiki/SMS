from ftplib import FTP
import pandas as pd
class ftp:
    def __init__(self,login,pwd,host):
        self.login = login
        self.pwd = pwd
        self.host = host
        self.__server = ""
    
    def connectToServer(self):
        try:
            self.__server = FTP(host=self.host,user=self.login,passwd=self.pwd)
        except Exception as e:
            print (e)
            
    def createBackUpFile(self,folderName):
        pass
    