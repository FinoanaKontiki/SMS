from genericpath import isdir
import pandas as pd
# import urllib.request
import urllib
import os
import threading
import socket
import numpy as np
import asyncio
import requests
import json

from urllib.error import ContentTooShortError
from datetime import datetime
from pathlib import Path
from pandas.core.algorithms import mode
from pandas.core.frame import DataFrame
from sms.authentification import authentification
from sms.sources.message.campagne import campagne
from sms.color import colors
from clint.textui import progress, puts

class files(authentification):
    def __init__(self, accountID, token):
        super().__init__(accountID, token)
        self.directory = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.docFiles = self.directory+self.pathByOs+"tmp"+self.pathByOs
        self.user_id_Konticrea = 52
        self.apikey_Konticrea = "ohaQzT-OXQJaP-hZlVoU-CoMkhN-vK5UPZ"
        self.stats_apikey = "b48fac8d4d8bb8200896ca4c66ca0180"
        self.dataFile = pd.read_csv(self.docFiles+self.pathByOs+"tags"+self.pathByOs+"liste_id_tag.csv" ,sep=";", encoding="ISO-8859-1" , on_bad_lines='skip', skip_blank_lines= True)
        self.all_campagne_with_data_konticrea =  []
        self.camp_list_name = {}
        self.statsBaseList = self.setListBaseStats()
        
    ##Fonctionlity Util 
    def writeToLog(self, logName, data):
        pathLog =  self.docFiles+"LOG"+self.pathByOs+logName+"_"+data['etat']+".txt"
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
    ##
    def setListBaseStats(self):
        url = "https://stats.kontikimedia.com/publicapi/cmapi/getcmbases?userapikey=ed630f1f208bfcefe996218d331ed327"
        data = {"userapikey":"b48fac8d4d8bb8200896ca4c66ca0180"}
        result = {}
        try:
            request = requests.post(url,data=data)
            res = json.loads(request.text) if request.status_code == 200 or request.status_code == 201  else {"etat": "error ", "etat_description": str(request.status_code)}
            if "etat" not in res:
                result = res['bases'] 
        except Exception as e:
            print(f"{colors.FAIL} ERROR GET STATS DATABASE NAME !!!!!!!!!!!!!{colors.ENDC}")
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
            self.filterFileToAppend(fileContentFrame)
            
        print(fileContentFrame['phone'])
        return fileContentFrame
    
    def appendContentsInFile(self, dataToAppend, fileType, idCamp):
        try:
            fileName = str(datetime.now().strftime("%Y%m%d"))+"_"+fileType+"_SMS.csv"
            base_for_folder_name = self.getDatabaseStats(idCamp)
            base_folder_path = self.docFiles+"FTPFiles"+self.pathByOs+base_for_folder_name
            if isdir(base_folder_path):
                newFTPfile = self.docFiles+"FTPFiles"+self.pathByOs+base_for_folder_name+self.pathByOs+fileName
            else:
                try:
                    os.mkdir(base_folder_path)
                    newFTPfile = self.docFiles+"FTPFiles"+self.pathByOs+base_for_folder_name+self.pathByOs+fileName
                except FileExistsError:
                    pass
            print('*'*50)
            print('Camp= '+self.camp_list_name[idCamp])
            print('base folder name = '+base_for_folder_name)
            print(base_folder_path)
            print(newFTPfile)
            print('*'*50)
            dataToAppend.dropna(inplace = True)
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
                pathFolderFile = "tmp"+self.pathByOs+fileType+self.pathByOs+idCampagne+"_"+dateShoot+"_"+fileType+".csv"
                pathSaveFile = os.path.join(self.directory,pathFolderFile)
                url = self.pathInitApi_V1_message+self.accountID+"/messages/"+idCampagne+"/export?status="+fileType if fileType != "optedOut" else self.pathInitApi_V2_addressbook+self.accountID+"/optout/export?campaignId="+idCampagne
                pathSaveFile = os.path.join(self.directory,pathFolderFile)
                socket.setdefaulttimeout(60)
                try:
                    # confOpen = urllib.request.build_opener()
                    # confOpen.addheaders=[('X-CM-PRODUCTTOKEN',self.token)]
                    # urllib.request.install_opener(confOpen)
                    # urllib.request.urlretrieve(url,pathSaveFile)
                    self.downloadNew(url,pathSaveFile,fileType, idCampagne)  
                except (socket.timeout, ContentTooShortError) as e:
                    trying = 1
                    while trying <= 5:
                        try:
                            # urllib.request.urlretrieve(url, pathSaveFile)
                            self.downloadNew(url,pathSaveFile,fileType, idCampagne)
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
                    dataStats = self.getDataKonticrea(idCampagne)
                    # print(f"{colors.OKCYAN} {idCampagne} ---  downloaded ---- {fileType}{colors.ENDC}")
                    result = {"etat": "success", "idCampagne":idCampagne, "pathFile":pathSaveFile, "dataStats": dataStats, "fileType": fileType}
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
    
    def filterFileToAppend(self, dataInfoCreatedFile , idCamp,dataExist = pd.DataFrame()):
        try:
            fileContentFrame = pd.read_csv(dataInfoCreatedFile['pathFile'], sep=',', na_filter=False, on_bad_lines='skip', skip_blank_lines= True) if len(dataExist) < 1  else dataExist
            # fileContentFrame = pd.read_csv(dataInfoCreatedFile['pathFile'], sep=',', na_filter=False, skip_blank_lines= True, engine='python', error_bad_lines=False) if len(dataExist) < 1  else dataExist
            if fileContentFrame.empty == False:
                if len(dataInfoCreatedFile['dataStats']) > 0:
                    forData = dataInfoCreatedFile['dataStats']
                    dataKonticrea = {"idStats":forData['stats_id'],"tag_campagne":forData['tag'],"code_pays":forData['country'], "advertiser":forData['campaign']}
                else:
                    # tag = self.findTagCamp(dataInfoCreatedFile['idCampagne'])
                    tag = self.findTagAndAdvertiser(dataInfoCreatedFile['idCampagne'])
                    if bool(tag) != False:
                        dataKonticrea = {"idStats":tag['id_stats'] if tag['id_stats'] != '' else "00","tag_campagne":tag['tag'] if tag['tag'] != '' else 'None',"code_pays":"fr", "advertiser":tag['advertiser']}
                    else:
                        dataKonticrea = {"idStats":"00","tag_campagne":'None',"code_pays":"fr"}
                fileContentFrame.loc[:,'idStats'] = dataKonticrea['idStats']
                fileContentFrame.loc[:,'tag_campagne'] = dataKonticrea['tag_campagne']
                fileContentFrame.loc[:,'code_pays'] = dataKonticrea['code_pays']
                fileContentFrame.loc[:,'advertiser'] = dataKonticrea['advertiser']
                formatMobile = lambda mobile: str(mobile).replace('+', '')
                if dataInfoCreatedFile['fileType'] == "optedOut":
                    data  = {
                        "date_shoot" : fileContentFrame.loc[:,'DateUtc'].apply(lambda date: self.formDate(str(date))),
                        "mobile" : fileContentFrame.loc[:,'OptOutValue'].apply(formatMobile),
                        "idStats" : fileContentFrame.loc[:,'idStats'],
                        "tag_campagne" : fileContentFrame.loc[:,'tag_campagne'],
                        "code_pays" : fileContentFrame.loc[:,'code_pays'],
                        "advertiser" : fileContentFrame.loc[:,'advertiser'],
                    }

                elif dataInfoCreatedFile['fileType'] == "optedOutUndelivered":
                    data  = {
                        "date_shoot" : fileContentFrame.loc[:,'Processed UTC'],
                        "mobile" : fileContentFrame.loc[:,'Recipient'].apply(formatMobile),
                        "idStats" : fileContentFrame.loc[:,'idStats'],
                        "tag_campagne" : fileContentFrame.loc[:,'tag_campagne'],
                        "code_pays" : fileContentFrame.loc[:,'code_pays'],
                        "advertiser" : fileContentFrame.loc[:,'advertiser'],
                    }

                elif dataInfoCreatedFile['fileType'] == "undelivered":
                    # with open('dict.txt', "w") as f:
                    #     f.write(str(fileContentFrame.to_json()))
                    all_with_date = fileContentFrame[fileContentFrame["Status"] == "Failed"]
                    all_with_date.reset_index(drop=True, inplace= True)
                    # print(all_with_date['ErrorCode'])
                    date_to_optout = all_with_date["Processed UTC"].iloc[0]
                    true_date = lambda date,date_to: self.formDate(str(date)) if date != '' else self.formDate(str(date_to))
                    fileContentFrame['Processed UTC'] = np.vectorize(true_date)(fileContentFrame['Processed UTC'],date_to_optout)
                    data_undeliver = fileContentFrame[fileContentFrame['Status'] == "Failed"]
                    data  = {
                        "date_shoot" : data_undeliver.loc[:,'Processed UTC'],
                        "mobile" : data_undeliver.loc[:,'Recipient'].apply(formatMobile),
                        "idStats" : data_undeliver.loc[:,'idStats'].astype(int),
                        "tag_campagne" : data_undeliver.loc[:,'tag_campagne'],
                        "code_pays" : data_undeliver.loc[:,'code_pays'],
                        "error_code": data_undeliver.loc[:,'ErrorCode'],
                        "advertiser" : data_undeliver.loc[:,'advertiser'],
                    }
                    dataOpted = fileContentFrame[fileContentFrame['Status']=='OptedOut']
                    if len(dataOpted) > 1:
                        dataInfoCreatedFile = {"pathFile":"async","idCampagne":dataInfoCreatedFile['idCampagne'],"fileType": "optedOutUndelivered", "dataStats":dataInfoCreatedFile['dataStats']}
                        asyncio.run(self.updateOptOutByUndelivered(dataInfoCreatedFile=dataInfoCreatedFile, data=dataOpted, idCamp=idCamp))
                        next
                else:
                    data={
                        "date_shoot" : fileContentFrame.loc[:,'Processed UTC'].apply(lambda date: self.formDate(str(date))),
                        "mobile" : fileContentFrame.loc[:,'Recipient'].apply(formatMobile),
                        "idStats" : fileContentFrame.loc[:,'idStats'],
                        "tag_campagne" : fileContentFrame.loc[:,'tag_campagne'],
                        "code_pays" : fileContentFrame.loc[:,'code_pays'],
                        "advertiser" : fileContentFrame.loc[:,'advertiser'],
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
            self.writeToLog("filterFile_function",{"etat": "error ", "etat_description": str(e), "date": str(datetime.now()), "id": dataInfoCreatedFile['idCampagne']})
            return {'etat':'ERROR'}

    async def updateOptOutByUndelivered(self, dataInfoCreatedFile, data, idCamp):
        print('async-------------------------------------')
        data_append = self.filterFileToAppend(dataInfoCreatedFile=dataInfoCreatedFile, dataExist= data, idCamp=idCamp)
        if isinstance(data_append,DataFrame,):
            self.appendContentsInFile(data_append, 'optedOut',idCamp=idCamp)

    def launchDWHUpdate(self, campagneList,fileType):
        for idCamp in campagneList:
            infoCurrentCamp =  self.downloadFiles(idCamp,fileType)
            if "etat" in  infoCurrentCamp and infoCurrentCamp["etat"] == "success":
                dataToAppend = self.filterFileToAppend(infoCurrentCamp, idCamp=idCamp)
                if isinstance(dataToAppend,DataFrame):
                    appendResult = self.appendContentsInFile(dataToAppend,fileType,idCamp)
                    appendResult['idCampagne'] = idCamp 
                    self.writeToLog(fileType,appendResult)
                    if appendResult['etat'] == 'success':
                        # print(f"{colors.OKCYAN} File download ID: {idCamp} -------------- {fileType}{colors.ENDC}")
                        os.remove(infoCurrentCamp['pathFile'])
                    else:
                        print(f"{colors.FAIL} {idCamp} error--------Fies not removed--- {fileType}{colors.ENDC}")
                        print(appendResult)
    
    def executThread(self,listeCampagne):
        result = {"etat": "success"}
        try:
            print(listeCampagne)
            self.all_campagne_with_data_konticrea = self.getCampagneInfoKonticrea(listeCampagne)
            print(self.all_campagne_with_data_konticrea)
            undelivered  =threading.Thread(target=self.launchDWHUpdate,args=(listeCampagne,"undelivered"))
            converted=threading.Thread(target=self.launchDWHUpdate,args=(listeCampagne,"converted"))
            optedOut=threading.Thread(target=self.launchDWHUpdate,args=(listeCampagne,"optedOut"))
            delivered=threading.Thread(target=self.launchDWHUpdate,args=(listeCampagne,"delivered"))
            theadList = [undelivered,converted,optedOut,delivered]
            # theadList = [undelivered]
            [t.start() for t in theadList]
            [t.join() for t in theadList]
            print(f"{colors.OKGREEN}--- All process executed ---{colors.ENDC}")
            return result
            # else:
            #     print(f"{colors.FAIL} ERROR-- CAMPAGNE DATA KONTICREA EMPTY {colors.ENDC}")    
        except Exception as e:
            print(f"{colors.FAIL} ERROR--{str(e)} {colors.ENDC}")
            return {"etat": "error ", "etat_description": str(e)}

    def getCampagneInfoKonticrea(self,listIDCampagne):
        try:
            data = {
                "user_id": self.user_id_Konticrea,
                "apikey": self.apikey_Konticrea,
                "tool_id": listIDCampagne,
                "stats_apikey": self.stats_apikey
            }
            print(data)
            url = "http://vps-e1758d70.vps.ovh.net:5009/api/sms/export/getData"
            # url = "http://192.168.210.103:5009/api/sms/export/getData"
            req = requests.post(url,json=data)
            result = self.checkRequest(req)    
        except Exception as e:
            result = {"etat": "error "+ str(e)}
            print(f"{colors.FAIL} ERROR--{str(e)} {colors.ENDC}")

        print(result)
        return result

    def getDataKonticrea (self, idCamp):
        data = []
        if len(self.all_campagne_with_data_konticrea) != 0:
            for dataKonti in self.all_campagne_with_data_konticrea:
                if dataKonti['idCampagne'] == idCamp:
                    data = dataKonti
        else:
            print(f"{colors.WARNING} Data campagne Konticrea empty {colors.ENDC}")
        return data
    def downloadNew (self, url, pathToSave, fileType, idCampagne):
        try:
            r = requests.get(url, stream=True, headers={'X-CM-PRODUCTTOKEN': self.token})
            with open(pathToSave, "wb") as files:
                total_length = int(r.headers.get('content-length'))
                puts(f"{colors.OKGREEN}--- Donload: {idCampagne}  type: {fileType} ---{colors.ENDC}")
                for ch in progress.bar(r.iter_content(chunk_size = 1024), expected_size=(total_length/1024) + 1):
                    if ch:
                        files.write(ch)
        except Exception as e:
            print(f"{colors.FAIL} ERROR in download--{str(e)} {colors.ENDC}")

    def findTagCamp( self, IdCamp):
        dataFile =  self.dataFile.copy()
        rowSelectedFrame = dataFile[dataFile['id'] == IdCamp]
        rowSelectedFrame.reset_index(drop=True, inplace= True)
        data = {}
        if len(rowSelectedFrame) == 1:
            data = {
                "tag": rowSelectedFrame.loc[0,"Tag"],
                "id_stats": int(rowSelectedFrame.loc[0,"id_stats"])
            } 
        return data
    
    def findTagAndAdvertiser(self, idCamp):
        dataRes = {}
        camp_name = self.camp_list_name[idCamp]
        if bool(camp_name):
            if "verisure" in str(camp_name).lower():
                dataRes = {
                    "advertiser":"Verisure",
                    "tag": "alarms",
                    "id_stats": int(53)
                }
            elif "mon-centre-auditif.com" in str(camp_name).lower():
                dataRes = {
                    "advertiser":"mon-centre-auditif.com",
                    "tag": "Health",
                    "id_stats": int(14)
                }
        return dataRes
    
    def getDatabaseStats(self, idCamp):
        camp_name = self.camp_list_name[idCamp]
        res = ''
        for base in self.statsBaseList:
            if str(base['name']).lower() in camp_name.lower():
               res = base['name']
        if res == '':
            if 'PDCVLR' in camp_name or 'PDC VLR' in camp_name:
                res = 'PDCVLR'
        return res
