import pandas as pd
import urllib.request
import os
import threading
import socket
import numpy as np
import asyncio

from urllib.error import ContentTooShortError
from datetime import datetime
from pathlib import Path
from pandas.core.algorithms import mode
from pandas.core.frame import DataFrame
from sms.authentification import authentification
from sms.sources.message.campagne import campagne
from sms.color import colors

class files(authentification):
    def __init__(self, accountID, token):
        super().__init__(accountID, token)
        self.directory = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.docFiles = self.directory+"//tmp//"
        
    ##Fonctionlity Util 
    def writeToLog(self, logName, data):
        pathLog =  self.docFiles+"LOG//"+logName+"_"+data['etat']+".txt"
        with open(pathLog,"a") as f:
            f.write(str(data)+",\n")
            
    def formDate(self,date):
        dateSplit = date.split('-')
        if dateSplit[0] != '' and len(date) == 16:
            try:
                dateShoot = dateSplit[2].split(' ')[0]+"/"+dateSplit[1]+"/"+dateSplit[0]
            except Exception as e:
                print("-----------error")
                print(e)
            hour = date.split(' ')[1]
            result = dateShoot+" "+hour
        else:
            result = ''
        return result

    def splitCampagneIDLIst(self, listCampagne, nbrPart):
        lenContet = int(len(listCampagne)/nbrPart)
        comptID=0
        allData = []
        data = []
        for camp in listCampagne:
            data.append(camp)
            if comptID == lenContet:
                allData.append(data)
                comptID=0
                data = []
            comptID += 1
        if len(data) >0:
                allData.append(data)
        return allData

    ############################################            
    def formatFile(self, pathFile, type):
        fileContentFrame = pd.read_csv(pathFile, sep=',', on_bad_lines='skip')
        if type == 'delivered':
            # fileContentFrame['phone'] = ["+33"+str(number) for number in fileContentFrame['phone'] if str(number).startswith("33") != True]
            for i,number in enumerate(fileContentFrame['phone']): 
                if str(number).startswith("33") != True:
                    fileContentFrame.at[i,'phone'] = "+33"+str(number)
             
        elif type == 'all':
            self.filterFileToAppend(fileContentFrame)
            
        print(fileContentFrame['phone'])
        return fileContentFrame
    
    def appendContentsInFile(self, dataToAppend, fileType):
        try:
            fileName = str(datetime.now().strftime("%Y%m%d"))+"_"+fileType+"_SMS.csv"
            newFTPfile = self.docFiles+"FTPFiles//"+fileName
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
                pathFolderFile = "tmp//"+fileType+"//"+idCampagne+"_"+dateShoot+"_"+fileType+".csv"
                pathSaveFile = os.path.join(self.directory,pathFolderFile)
                url = self.pathInitApi_V1_message+self.accountID+"/messages/"+idCampagne+"/export?status="+fileType if fileType != "optedOut" else self.pathInitApi_V2_addressbook+self.accountID+"/optout/export?campaignId="+idCampagne
                pathSaveFile = os.path.join(self.directory,pathFolderFile)
                socket.setdefaulttimeout(60)
                try:
                    confOpen = urllib.request.build_opener()
                    confOpen.addheaders=[('X-CM-PRODUCTTOKEN',self.token)]
                    urllib.request.install_opener(confOpen)
                    urllib.request.urlretrieve(url,pathSaveFile)    
                except (socket.timeout, ContentTooShortError) as e:
                    trying = 1
                    while trying <= 5:
                        try:
                            urllib.request.urlretrieve(url, pathSaveFile)
                            break
                        except (socket.timeout, ContentTooShortError) as e:
                            print(f"{colors.FAIL} {idCampagne} timeout download --- try again {trying}{colors.ENDC}")
                            self.writeToLog("Downoad_function",{"etat": "error ", "etat_description": str(e)})
                            trying += 1
                    if trying > 5:
                        result = {"etat": "error ", "etat_description": "file not downloaded id = "+ idCampagne}
                        print(f"{colors.FAIL} {idCampagne} ERROR download file id = {idCampagne}{colors.ENDC}")

                    print(f"{colors.FAIL} {idCampagne} ERROR download --- try again {trying}{colors.ENDC}")
                    self.writeToLog("Downoad_function",{"etat": "error ", "etat_description": str(e)})
                checkFile = Path(pathSaveFile)
                if checkFile.is_file():
                    # idStats = currentCamp['value']['name'].split('-')[2]
                    idStats = 2
                    print(f"{colors.OKCYAN} {idCampagne} ---  downloaded ---- {fileType}{colors.ENDC}")
                    result = {"etat": "success", "pathFile":pathSaveFile, "idStats": idStats, "fileType": fileType}
                else:
                    result = {"etat": "error ", "etat_description": "file not created"}
                    print(f"{colors.FAIL} {idCampagne} ERROR Download--- in downloadFiles{colors.ENDC}")
            else:
                print(f"{colors.FAIL} {idCampagne} --- Status {currentCamp['value']['status']}{colors.ENDC}")
                result = {"etat": "error ", "etat_description": "status "+ currentCamp['value']['status']}
        else:
            result = {"etat": "error ", "etat_description": "campagne not found"}
            print(f"{colors.FAIL} {idCampagne} campagne not found--- in downloadFiles{colors.ENDC}")
            
        return result
    
    def filterFileToAppend(self, dataInfoCreatedFile , dataExist = pd.DataFrame()):
        try:
            fileContentFrame = pd.read_csv(dataInfoCreatedFile['pathFile'], sep=',', na_filter=False, on_bad_lines='skip', skip_blank_lines= True) if len(dataExist) < 1  else dataExist
            if fileContentFrame.empty == False:
                dataKonticrea = {"idStats":"04", "tag_campagne":"test", "code_pays":"fr"}
                fileContentFrame.loc[:,'idStats'] = dataKonticrea['idStats']
                fileContentFrame.loc[:,'tag_campagne'] = dataKonticrea['tag_campagne']
                fileContentFrame.loc[:,'code_pays'] = dataKonticrea['code_pays']
                if dataInfoCreatedFile['fileType'] == "optedOut":
                    data  = {
                        "date_shoot" : fileContentFrame['DateUtc'].apply(lambda date: self.formDate(str(date))),
                        "mobile" : fileContentFrame['OptOutValue'],
                        "idStats" : fileContentFrame['idStats'],
                        "tag_campagne" : fileContentFrame['tag_campagne'],
                        "code_pays" : fileContentFrame['code_pays'],
                    }

                elif dataInfoCreatedFile['fileType'] == "optedOutUndelivered":
                    data  = {
                        "date_shoot" : fileContentFrame['Processed UTC'],
                        "mobile" : fileContentFrame['Recipient'],
                        "idStats" : fileContentFrame['idStats'],
                        "tag_campagne" : fileContentFrame['tag_campagne'],
                        "code_pays" : fileContentFrame['code_pays'],
                    }

                elif dataInfoCreatedFile['fileType'] == "undelivered":
                    all_with_date = fileContentFrame[fileContentFrame["Status"] == "Failed"]
                    all_with_date.reset_index(drop=True, inplace= True)
                    date_to_optout = all_with_date["Processed UTC"].iloc[0]
                    true_date = lambda date,date_to: self.formDate(str(date)) if date != '' else self.formDate(str(date_to))
                    fileContentFrame['Processed UTC'] = np.vectorize(true_date)(fileContentFrame['Processed UTC'],date_to_optout)
                    data_undeliver = fileContentFrame[fileContentFrame['Status'] == "Failed"]
                    data  = {
                        "date_shoot" : data_undeliver['Processed UTC'],
                        "mobile" : data_undeliver['Recipient'],
                        "idStats" : data_undeliver['idStats'],
                        "tag_campagne" : data_undeliver['tag_campagne'],
                        "code_pays" : data_undeliver['code_pays'],
                    }
                    dataOpted = fileContentFrame[fileContentFrame['Status']=='OptedOut']
                    if len(dataOpted) > 1:
                        dataInfoCreatedFile = {"pathFile":"async","fileType": "optedOutUndelivered"}
                        asyncio.run(self.updateOptOutByUndelivered(dataInfoCreatedFile=dataInfoCreatedFile, data=dataOpted))
                        next
                else:
                    data={
                        "date_shoot" : fileContentFrame['Processed UTC'].apply(lambda date: self.formDate(str(date))),
                        "mobile" : fileContentFrame['Recipient'],
                        "idStats" : fileContentFrame['idStats'],
                        "tag_campagne" : fileContentFrame['tag_campagne'],
                        "code_pays" : fileContentFrame['code_pays'],
                    }
                    
                resultFrame = pd.DataFrame(data)
                # print(withstatus)
                # print(resultFrame)
                result = resultFrame[resultFrame['date_shoot']!='']
                return result
            else:
                os.remove(dataInfoCreatedFile['pathFile'])
                print(f"{colors.FAIL} ERROR: ---file Empty  PATH: {dataInfoCreatedFile['pathFile']} {colors.ENDC}")
                return {'etat':'ERROR'}
        except Exception as e:
            print(f"{colors.FAIL} ERROR: {str(e)}  PATH: {dataInfoCreatedFile['pathFile']} {colors.ENDC}")
            self.writeToLog("filterFile_function",{"etat": "error ", "etat_description": str(e)})
            return {'etat':'ERROR'}

    async def updateOptOutByUndelivered(self, dataInfoCreatedFile, data):
        print('async-------------------------------------')
        data_append = self.filterFileToAppend(dataInfoCreatedFile=dataInfoCreatedFile, dataExist= data)
        if isinstance(data_append,DataFrame,):
            self.appendContentsInFile(data_append, 'optedOut')

    def launchDWHUpdate(self, campagneList,fileType):
        for idCamp in campagneList:
            infoCurrentCamp =  self.downloadFiles(idCamp,fileType)
            if "etat" in  infoCurrentCamp and infoCurrentCamp["etat"] == "success":
                dataToAppend = self.filterFileToAppend(infoCurrentCamp)
                if isinstance(dataToAppend,DataFrame):
                    appendResult = self.appendContentsInFile(dataToAppend,fileType)
                    appendResult['idCampagne'] = idCamp 
                    self.writeToLog(fileType,appendResult)
                    if appendResult['etat'] == 'success':
                        print(f"{colors.OKCYAN} File download ID: {idCamp} -------------- {fileType}{colors.ENDC}")
                        os.remove(infoCurrentCamp['pathFile'])
                    else:
                        print(f"{colors.FAIL} {idCamp} error--------Fies not removed--- {fileType}{colors.ENDC}")
                        print(appendResult)
    
    def executThread(self,listeCampagne):
        result = {"etat": "success"}
        try:
            print(listeCampagne)
            undelivered  =threading.Thread(target=self.launchDWHUpdate,args=(listeCampagne,"undelivered"))
            converted=threading.Thread(target=self.launchDWHUpdate,args=(listeCampagne,"converted"))
            optedOut=threading.Thread(target=self.launchDWHUpdate,args=(listeCampagne,"optedOut"))
            delivered=threading.Thread(target=self.launchDWHUpdate,args=(listeCampagne,"delivered"))
            theadList = [undelivered,converted,optedOut,delivered]
            # theadList = [optedOut]
            [t.start() for t in theadList]
            [t.join() for t in theadList]
            print(f"{colors.OKGREEN}--- All process executed ---{colors.ENDC}")
            return result
        except Exception as e:
            print(f"{colors.FAIL} ERROR--{str(e)} {colors.ENDC}")
            return {"etat": "error ", "etat_description": str(e)}