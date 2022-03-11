import queue
import threading
import pysftp
import os
import platform

from sms.color import colors 
from datetime import datetime
from genericpath import isfile
from pathlib import Path
from os import listdir
class ftp():
    def __init__(self,user,pwd,host):
        self.user = user
        self.pwd = pwd
        self.host = host
        self._server = ""
        self.pathByOs = "\\" if platform.system() == "Windows" else "//"
        self.docFiles = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))+self.pathByOs+"tmp"+self.pathByOs
        self.sftpPath = self.pathByOs+"ftp_down"+self.pathByOs+"SMS"+self.pathByOs
    
    def connectToServer(self):
        try:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            self._server = pysftp.Connection(host=self.host,username=self.user,password=self.pwd, cnopts=cnopts)                
            result = {"status": "connected"}
            print(f"{colors.OKGREEN} -----Connected to server successfuly-------{colors.ENDC}")
        except Exception as e:
            print(f"{colors.FAIL} connection to server refused{colors.ENDC}")
            result = {"status": "error "+ str(e)}
        return result
    
    def createBackLogServerFile(self, localFolderName,fileTypeInSftp):
        status = True
        try:
            print(f"{colors.WARNING}{fileTypeInSftp} Create backUp----{colors.ENDC}")
            sftpPath = os.path.join(self.sftpPath,fileTypeInSftp)
            locaPath = os.path.join(self.docFiles,"backupFTP"+self.pathByOs+localFolderName)
            self._server.cwd(sftpPath)
            listFileInDoc = self._server.listdir()
            fileInLocalBackUp = listdir(locaPath)
            list_serve_doc = self._server.listdir(remotepath=sftpPath)
            for serv_file in list_serve_doc:
                if serv_file not in fileInLocalBackUp:
                    print("LOCALE ---------------")
                    print(serv_file)
                    self._server.get_d(remotedir=sftpPath,localdir=locaPath, preserve_mtime= True)
            print(listFileInDoc)
            print(fileInLocalBackUp)
            for file in listFileInDoc:
                pathLocalFileBackUp = Path(locaPath+self.pathByOs+file)
                if isfile(pathLocalFileBackUp):
                    print(f"{colors.OKGREEN} BACK up {fileTypeInSftp} created {colors.ENDC}")
                    # self._server.remove(remotefile=sftpPath+self.pathByOs+file)
                else:
                    status = False
                    print(f"{colors.FAIL} ERROR create {fileTypeInSftp} backUp file {colors.ENDC}")
            print(f"{colors.OKGREEN}{fileTypeInSftp} backUp fineshed----{colors.ENDC}")       
            # self._server.close()
        except Exception as e:
            print(f"{colors.FAIL} ERROR file ={fileTypeInSftp}  Error={str(e)}{colors.ENDC}")
            status = False
            # self._server.close()
            
        return status
        
    def uploadToSFTP(self, localFolderName, fileTypeInSftp):
        try:
            print(f"{colors.WARNING}{fileTypeInSftp} Start upload----{colors.ENDC}")
            fileName = str(datetime.now().strftime("%Y%m%d"))+"_"+localFolderName+"_SMS.csv"
            # fileName = "20220305_"+localFolderName+"_SMS.csv"
            sftpPath = self.sftpPath+self.pathByOs+fileTypeInSftp+self.pathByOs+fileName
            localFilePath = self.docFiles+self.pathByOs+"FTPFiles"+self.pathByOs+fileName
            self._server.put(localpath=localFilePath,remotepath=sftpPath)
            if self._server.exists(sftpPath):
                os.remove(localFilePath)
                print(f"{colors.OKGREEN}{fileTypeInSftp} ---Uploaded----{colors.ENDC}")
            else:
                print(f"{colors.FAIL} file {fileTypeInSftp} not uploaded path local: {localFilePath} {colors.ENDC}")
        except Exception as e:
            print(f"{colors.FAIL} ERROR uploading {fileTypeInSftp} file {str(e)}{colors.ENDC}")

    def proccessUpload(self, localFolderName,fileTypeInSftp):
        print(f"{colors.WARNING}{fileTypeInSftp} Start process----{colors.ENDC}")
        backCreate = self.createBackLogServerFile(localFolderName,fileTypeInSftp)
        if backCreate:
            self.uploadToSFTP(localFolderName,fileTypeInSftp)
        

    def lunchUploadTread(self):
        try:
            upClicked = threading.Thread(target=self.proccessUpload, args=("converted","Clicked"))          
            upHardbounce = threading.Thread(target=self.proccessUpload, args=("undelivered","Hardbounce"))          
            upCSent = threading.Thread(target=self.proccessUpload, args=("delivered","Sent"))          
            upUnsub = threading.Thread(target=self.proccessUpload, args=("optedOut","Unsub"))
            treadList = [upClicked, upHardbounce, upCSent, upUnsub]
            [th.start() for th in treadList]
            [th.join() for th in treadList]
            print(f"{colors.OKGREEN}-----------Upload process fineshed-----------{colors.ENDC}")
            self._server.close()
        except Exception as e:
            print(f"{colors.FAIL}-----ERROR on thread execution {str(e)}{colors.ENDC}")
            self._server.close()

    def testEx(self):
        argUpload = [("converted","Clicked"),("undelivered","Hardbounce"),("delivered","Sent"),("optedOut","Unsub")]
        for arg in argUpload:
            try:
                self.proccessUpload(arg[0],arg[1])
            except Exception as e:
                print(f"{colors.FAIL}-----ERROR on thread execution {str(e)}{colors.ENDC}")
                pass
        # self._server.close()

              

        
                    