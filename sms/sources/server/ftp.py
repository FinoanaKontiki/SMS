import ftplib
from genericpath import isfile
from pathlib import Path
import pysftp
import os

from datetime import datetime
class ftp():
    def __init__(self,user,pwd,host):
        self.user = user
        self.pwd = pwd
        self.host = host
        self._server = ""
        self.docFiles = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))+"\\tmp\\"
        self.sftpPath = "/ftp_down/SMS/"
    
    def connectToServer(self):
        try:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            self._server = pysftp.Connection(host=self.host,username=self.user,password=self.pwd, cnopts=cnopts)
            # self._server.cwd('/var/www/vhosts/')
            directory_structure = self._server.listdir_attr()

            # Print data
            for attr in directory_structure:
                print(attr.filename)
                
            result = {"status": "connected"}
        except Exception as e:
            result = {"status": "error "+ str(e)}
        return result
    
    def createBackLogServerFile(self, localFolderName,fileTypeInSftp):
        try:
            sftpPath = os.path.join(self.sftpPath,fileTypeInSftp)
            locaPath = os.path.join(self.docFiles,"backupFTP\\"+localFolderName)
            print(sftpPath,'sftpPath-----------')
            print(locaPath,'locaPath-----------')
            self._server.get_d(remotedir=sftpPath,localdir=locaPath, preserve_mtime= True)
            self._server.cwd(sftpPath)
            listFileInDoc = self._server.listdir()
            for file in listFileInDoc:
                pathLocalFileBackUp = Path(locaPath+"\\"+file)
                print(isfile(pathLocalFileBackUp))
                if isfile(pathLocalFileBackUp):
                    self._server.remove(remotefile=sftpPath+"/"+file)
                    status = True
                else:
                    status = False
                    print("Error le fichier backUp n'as pas été créer")
                    
            self._server.close()
        except Exception as e:
            print(e)
            status = False
            self._server.close()
            
        return status
        
    def uploadToSFTP(self, sftpFolderName, fileTypeInSftp):
        try:
            fileName = str(datetime.now().strftime("%Y%m%d"))+"_"+sftpFolderName+"_SMS.csv"
            sftpPath = self.sftpPath+"/"+fileTypeInSftp+"/"+fileName
            localFilePath = self.docFiles+"\\FTPFiles\\"+fileName
            self._server.put(localpath=localFilePath,remotepath=sftpPath)
            isUploaded = self._server.exists(sftpPath)
            print(isUploaded,' is upload------------')
            self._server.close()
        except Exception as e:
            print(e)
            self._server.close()
        
                    