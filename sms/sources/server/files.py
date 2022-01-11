import pandas as pd
import urllib.request
import os
import time
import json
import threading

from datetime import datetime
from pathlib import Path
from pandas.core.algorithms import mode
from sms.authentification import authentification
from sms.sources.message.campagne import campagne

class files(authentification):
    def __init__(self, accountID, token):
        super().__init__(accountID, token)
        self.directory = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.docFiles = self.directory+"\\tmp\\"
        
    ##Fonctionlity Util 
    def writeToLog(self, logName, data):
        pathLog =  self.docFiles+"LOG\\"+logName+"_"+data['etat']+".txt"
        print(pathLog)
        with open(pathLog,"a") as f:
            f.write(str(data)+";")
            
    def formDate(self,date):
        dateSplit = date.split('-')
        if dateSplit[0] != '':
            dateShoot = dateSplit[2].split(' ')[0]+"/"+dateSplit[1]+"/"+dateSplit[0]
            hour = date.split(' ')[1]
            result = dateShoot+" "+hour
        else:
            result = ''
        return result        
    ############################################            
    def formatFile(self, pathFile, type):
        fileContentFrame = pd.read_csv(pathFile, sep=',', on_bad_lines='skip')
        if type == 'delivered':
            # fileContentFrame['phone'] = ["+33"+str(number) for number in fileContentFrame['phone'] if str(number).startswith("33") != True]
            for i,number in enumerate(fileContentFrame['phone']): 
                if str(number).startswith("33") != True:
                    fileContentFrame.at[i,'phone'] = "+33"+str(number)
             
        elif type == 'all':
            self.filterFile(fileContentFrame)
            
        print(fileContentFrame['phone'])
        return fileContentFrame
    
    def appendContentsInFile(self, dataToAppend, fileType):
        try:
            fileName = str(datetime.now().strftime("%Y%m%d"))+"_"+fileType+"_SMS.csv"
            newFTPfile = self.docFiles+"FTPFiles\\"+fileName
            dataToAppend.to_csv(newFTPfile, sep=',', mode='a', index =False, header=False)
            result = {"etat": "success", "date": str(datetime.now())}
        except Exception as e:
            result = {"etat": "error ", "etat_description": str(e), "date": str(datetime.now())}
            
        return result
        
    def downloadFiles(self, idCampagne, fileType):
        smsCampagne = campagne(self.accountID,self.token)
        currentCamp = smsCampagne.getCampagne(idCampagne)
        if "etat" in currentCamp and currentCamp["etat"] == "success":
            if currentCamp['value']['status'] == "sent":
                dateShoot = currentCamp['value']['scheduledAtUtc']
                dateShoot = self.replaceCharMultiple(currentCamp['value']['scheduledAtUtc'],((":",""),(".",""),("-","")))
                pathFolderFile = "tmp\\"+fileType+"\\"+idCampagne+"_"+dateShoot+"_"+fileType+".csv"
                pathSaveFile = os.path.join(self.directory,pathFolderFile)
                url = self.pathInitApi_V1_message+self.accountID+"/messages/"+idCampagne+"/export?status="+fileType if fileType != "optedOut" else self.pathInitApi_V2_addressbook+self.accountID+"/optout/export?campaignId="+idCampagne
                print(url)
                pathSaveFile = os.path.join(self.directory,pathFolderFile)
                try:
                    confOpen = urllib.request.build_opener()
                    confOpen.addheaders=[('X-CM-PRODUCTTOKEN',self.token)]
                    urllib.request.install_opener(confOpen)
                    urllib.request.urlretrieve(url,pathSaveFile)
                    checkFile = Path(pathSaveFile)
                    if checkFile.is_file():
                        idStats = currentCamp['value']['name'].split('-')[2]
                        result = {"etat": "success", "pathFile":pathSaveFile, "idStats": idStats, "fileType": fileType}
                    else:
                        result = {"etat": "error ", "etat_description": "file not created"}
                        
                except Exception as e:
                    result = {"etat": "error ", "etat_description": str(e)}
            else:
                result = {"etat": "error ", "etat_description": "status "+ currentCamp['value']['status']}
        else:
            result = {"etat": "error ", "etat_description": "campagne not found"}
            
        return result
    
    def filterFile(self, dataInfoCreatedFile):
        fileContentFrame = pd.read_csv(dataInfoCreatedFile['pathFile'], sep=',', na_filter=False)
        dataKonticrea = {"idStats":"04", "tag_campagne":"test", "code_pays":"fr"}
        fileContentFrame['idStats'] = dataKonticrea['idStats']
        fileContentFrame['tag_campagne'] = dataKonticrea['tag_campagne']
        fileContentFrame['code_pays'] = dataKonticrea['code_pays']

        if dataInfoCreatedFile['fileType'] == "optedOut":
            data  = {
                "date_shoot" : fileContentFrame['DateUtc'].apply(lambda date: self.formDate(str(date))),
                "mobile" : fileContentFrame['OptOutValue'],
                "idStats" : fileContentFrame['idStats'],
                "tag_campagne" : fileContentFrame['tag_campagne'],
                "code_pays" : fileContentFrame['code_pays'],
            }
        # elif dataInfoCreatedFile['fileType'] == "undelivered":
        #    pass
        else:
            data={
                "date_shoot" : fileContentFrame['Processed UTC'].apply(lambda date: self.formDate(str(date))),
                "mobile" : fileContentFrame['Recipient'],
                "idStats" : fileContentFrame['idStats'],
                "tag_campagne" : fileContentFrame['tag_campagne'],
                "code_pays" : fileContentFrame['code_pays'],
            }
            
        resultFrame = pd.DataFrame(data)
        # withstatus = fileContentFrame[fileContentFrame["Status"] == "Failed"]
        # print(withstatus.at[1,"Processed UTC"])
        # print(withstatus)
        # print(resultFrame[resultFrame['date_shoot']==''])
        return resultFrame
    
    def launchDWHUpdate(self, campagneList,fileType):
        for idCamp in campagneList:
            infoCurrentCamp =  self.downloadFiles(idCamp,fileType)
            if "etat" in  infoCurrentCamp and infoCurrentCamp["etat"] == "success":
                dataToAppend = self.filterFile(infoCurrentCamp)
                appendResult = self.appendContentsInFile(dataToAppend,fileType)
                appendResult['idCampagne'] = idCamp 
                self.writeToLog(fileType,appendResult)
                if appendResult['etat'] == 'success':
                    print("remove----",str(infoCurrentCamp['pathFile']))
                    os.remove(infoCurrentCamp['pathFile'])
    
    def executThread(self,listeCampagne):
        result = {"etat": "success"}
        try:
            undelivered  =threading.Thread(target=self.launchDWHUpdate,args=(listeCampagne,"undelivered"))
            converted=threading.Thread(target=self.launchDWHUpdate,args=(listeCampagne,"converted"))
            optedOut=threading.Thread(target=self.launchDWHUpdate,args=(listeCampagne,"optedOut"))
            delivered=threading.Thread(target=self.launchDWHUpdate,args=(listeCampagne,"delivered"))
            theadList = [undelivered,converted,optedOut,delivered]
            [t.start() for t in theadList]
            [t.join() for t in theadList]
        except Exception as e:
            result = {"etat": "error ", "etat_description": str(e)}
        return result