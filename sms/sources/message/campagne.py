
import requests
import json
import re

from requests.api import request
from sms.authentification import authentification
from datetime import datetime
from dateutil import parser
from uuid import uuid4
class campagne(authentification):
    def __init__(self, accountID, token):
        super().__init__(accountID, token)
        
    def findUrlInBodySMS(self, data):
        result = []
        for value in data:
           urlSearch = re.search("(?<=\[\[url:)(.*)(?=\]])",value['body'])
           value['url'] = urlSearch.group(0) if urlSearch is not None else ''
           result.append(value)
        return result
                
    def getListCampage(self, skip=0, take=20, isArchived=False):
        url = self.pathInitApi_V1_message+self.accountID+"/messages?includePreview=true&isArchived="+str(isArchived).lower()+"&skip="+str(skip)+"&take="+str(take)
        try:
            req = requests.get(url,headers=self.headers)
            result = self.findUrlInBodySMS(json.loads(req.text)) if req.status_code == 200 else {"etat": "error ", "etat_description": str(req.status_code)}
            if "etat" not in result:
                result = {"etat":"success", "value": result}
        except Exception as e:
            result = {"status": "error "+ str(e)}
        return result

    def getListCampageSent(self, skip=0, take=20, isArchived=False):
        url = self.pathInitApi_V1_message+self.accountID+"/messages?status=sent&status=cancelled&status=failed&includePreview=true&isArchived="+str(isArchived).lower()+"&skip="+str(skip)+"&take="+str(take)
        try:
            req = requests.get(url,headers=self.headers)
            result = self.findUrlInBodySMS(json.loads(req.text)) if req.status_code == 200 else {"etat": "error ", "etat_description": str(req.status_code)}
            if "etat" not in result:
                result = {"etat":"success", "value": result}
        except Exception as e:
            result = {"status": "error "+ str(e)}
        return result
    
    def getCampagne (self, idCampagne):
        url = self.pathInitApi_V1_message+self.accountID+"/messages/"+idCampagne
        try:
            req = requests.get(url,headers=self.headers)
            result = self.checkRequest(req)
            if "etat" not in result:
                result = {"etat":"success", "value": result}
        except Exception as e:
            result = {"status": "error "+ str(e)}
            
        return result
    
    def duplicateCampagne (self, idOldCapagne):
        dataOldAll = self.getCampagne(idOldCapagne)
        dataOld = dataOldAll['value']
        print(dataOld)
        current = str(datetime.now())
        dataDuplicate = {
            "analytics": dataOld['analytics'] if 'analytics' in dataOld else "" ,
            "body": dataOld['body'],
            "channels": dataOld['channels'],
            "createdAtUtc": current,
            "createdBy": self.accountID,
            "id": dataOld['id'],
            "ignoreUnsubscribes": dataOld['ignoreUnsubscribes'],
            "isArchived": dataOld["isArchived"],
            "isStatsComplete": dataOld["isStatsComplete"],
            "modifiedAtUtc": current,
            "name": dataOld["name"] + " - Duplicated",
            "recipients": dataOld["recipients"],
            "scheduledAtUtc": None,
            "senders": dataOld["senders"],
            "status": "draft",
            "updatedAtUtc": current,
        }
        url = self.pathInitApi_V1_message+self.accountID+"/messages"
        try:
            req = requests.post(url, headers=self.headers, json=dataDuplicate)
            result = self.checkRequest(req)
            if "etat" not in result:
                result["etat"] = "success"
        except Exception as e:
            result = {"etat": "error ", "etat_description": str(e)}
        return result
    
    def createDraft(self, senderName, idGroup, bodySms, nameCampagne,ignoreUnsubscribes=False,channels="SMS"):
        url =  self.pathInitApi_V1_message+self.accountID+"/messages"
        smsContents = {
            "senders": [senderName],
            "recipients": [
                {
                "group": idGroup
                }
            ],
            "body": bodySms,
            "channels": [channels],
            "ignoreUnsubscribes": ignoreUnsubscribes,
            "name": nameCampagne,
            "status": "draft"
            }
        try:
            req = requests.post(url,headers=self.headers, json=smsContents)
            result = self.checkRequest(req)
            if "etat" not in result:
                result["token"] = str(uuid4())
                result["etat"] = "success"
        except Exception as e:
            result = {"etat": "error ", "etat_description": str(e)}
        return result
    
    def planifierCampagne(self, idCampagne, scheduledAtUtc):
        dataCampagne = self.getCampagne(idCampagne)
        if dataCampagne["value"]["status"] != "scheduled":
            urlPreview = self.pathInitApi_V1_message+self.accountID+"/messages/preview"
            preview_data = {}
            try:
                print('ato 1')
                preview_req = requests.post(urlPreview, headers=self.headers, json=dataCampagne)
                preview_data = self.checkRequest(preview_req)
            except Exception as e:
                print('ato 1 error')
                result = {"etat": "error ", "etat_description": str(e)}
                
            if bool(preview_data) == True:
                print('ato 2 debut')
                dataCampagne["value"]["preview"] = preview_data
                dataCampagne["value"]["scheduledAtUtc"] = scheduledAtUtc
                dataCampagne["value"]["status"] = "scheduled"
                url_planning  = self.pathInitApi_V1_message+self.accountID+"/messages/"+dataCampagne["value"]["id"]+"?versioned=true"
                print(dataCampagne)
                try:
                    print('ato 2')
                    print(dataCampagne,'-----------')
                    print(url_planning,'-----------')
                    planning_req = requests.put(url_planning, headers= self.headers, json= dataCampagne['value'])
                    print(planning_req)
                    result = self.checkRequest(planning_req)
                    if "etat" not in result:
                        result["etat"] = "success"
                except Exception as e:
                    print('ato 2 error')
                    result = {"etat": "error ", "etat_description": str(e)}
        else:
            result = {"etat": "error ", "etat_description":"this campaign has already been planned"}
                
        return result
    
    
    def updateCampagne(self, idCampagne, dataNew):
        url = self.pathInitApi_V1_message+self.accountID+"/messages/"+idCampagne
        print(url)
        current = str(datetime.now())
        try:
            dataToAdd = {
                "body": dataNew['body'] if "body" in dataNew else "",
                "channels": dataNew['channels'] if "body" in dataNew else "",
                "createdAtUtc": current,
                "createdBy": self.accountID,
                "id": idCampagne,
                "ignoreUnsubscribes": dataNew['ignoreUnsubscribes'] if "body" in dataNew else "",
                "isArchived": dataNew["isArchived"] if "body" in dataNew else "",
                "isStatsComplete": dataNew["isStatsComplete"] if "body" in dataNew else "",
                "modifiedAtUtc": current,
                "name": dataNew["name"],
                "recipients": dataNew["recipients"],
                "scheduledAtUtc": dataNew["scheduledAtUtc"] if "scheduledAtUtc" in dataNew else None,
                "senders": dataNew["senders"],
                "status": dataNew["status"],
                "updatedAtUtc": current,
            }
            print(dataToAdd)
            req = requests.put(url=url,headers=self.headers,json=dataToAdd)
            result = self.checkRequest(req)
            if "etat" not in result:
                result["etat"] = "success"
        except Exception as e:
            result = {"etat": "error ", "etat_description": str(e)}
        return result
    
    def getCountCampagne(self):
        url = self.pathInitApi_V1_message+self.accountID+"/messages/count"
        try:
            req = requests.get(url,headers=self.headers)
            result = self.checkRequest(req)
            if "etat" not in result:
                result = {"etat":"success", "value": result}
        except Exception as e:
            result = {"status": "error "+ str(e)}
            
        return result
    
    def sendMessageTest(self, idCamp, phoneTosend):
        currentCamp = self.getCampagne(idCamp)
        url =  self.pathInitApi_V1_message+self.accountID+"/messages/test"
        print(url)
        if currentCamp['etat'] == "success":
            testRecipe = [
                {
                    "msisdn": phoneTosend,
                    "data": {
                    "1": "John",
                    "2": "van",
                    "3": "Doe",
                    "4": "+31627100000",
                    "5": "john.doe@example.com"
                    }
                }       
            ]
            data = {"message": currentCamp['value'], "testRecipients":testRecipe}
            try:
                req = requests.post(url,headers=self.headers, json=data)
                result = self.checkRequest(req)
                if "etat" not in result:
                    result = {"etat":"success", "value": result}
            except Exception as e:
                result = {"status": "error "+ str(e)}
            
        return result    
    
    def allCampgneByDATE(self, nbrJourToGet=31):
        acount = self.getCountCampagne()
        print(acount)
        allCamp = self.getListCampageSent(take=acount['value']['sent'])
        print(len(allCamp['value']))
        list_camp_id = []
        for camp in allCamp['value']:
            if camp['status'] == "sent" and "Verisure" in camp['name']:
            # if camp['status'] == "sent":
                date_creation = parser.parse(camp['scheduledAtUtc'])
                day_betwen = datetime.now().date() - date_creation.date()
                if day_betwen.days <= nbrJourToGet:
                    list_camp_id.append(camp['id'])
        print(len(list_camp_id))
        return list_camp_id 

    def getBase(self):
        acount = self.getCountCampagne()
        allCamp = self.getListCampageSent(take=acount['value']['sent'])
        data = []
        for d in allCamp['value']:
            try:
                idStats = d['name'].split('-')[2]
                data.append(idStats)
            except IndexError:
                print(d['name'],'-------ERROR')
                pass
        print(len(data),"---------avant")
        data = list(dict.fromkeys(data))
        print(len(data),"---------Apres")
        return data