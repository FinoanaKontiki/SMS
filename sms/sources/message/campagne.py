
import requests
import json
import re

from requests.api import request
from sms.authentification import authentification
from datetime import datetime
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
        url = self.pathInitApi_V1+self.accountID+"/messages?includePreview=true&isArchived="+str(isArchived).lower()+"&skip="+str(skip)+"&take="+str(take)
        try:
            req = requests.get(url,headers=self.headers)
            result = self.findUrlInBodySMS(json.loads(req.text)) if req.status_code == 200 else {"etat": "error ", "etat_description": str(req.status_code)}
            if "etat" not in result:
                result = {"etat":"success", "value": result}
        except Exception as e:
            result = {"status": "error "+ str(e)}
        return result
    
    def getCampagne (self, idCampagne):
        url = self.pathInitApi_V1+self.accountID+"/messages/"+idCampagne
        try:
            req = requests.get(url,headers=self.headers)
            result = self.checkRequest(req)
            if "etat" not in result:
                result = {"etat":"success", "value": result}
        except Exception as e:
            result = {"status": "error "+ str(e)}
            
        return result
    
    def duplicateCampagne (self, idOldCapagne):
        dataOld = self.getCampagne(idOldCapagne)
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
        url = self.pathInitApi_V1+self.accountID+"/messages"
        try:
            req = requests.post(url, headers=self.headers, json=dataDuplicate)
            result = self.checkRequest(req)
            if "etat" not in result:
                result["etat"] = "success"
        except Exception as e:
            result = {"status": "error "+ str(e)}
        return result
    
    def createDraft(self, senderName, idGroup, bodySms, nameCampagne,ignoreUnsubscribes=False,channels="SMS"):
        url =  self.pathInitApi_V1+self.accountID+"/messages"
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
        print(dataCampagne["status"], '------------------------')
        if dataCampagne["status"] != "scheduled":
            urlPreview = self.pathInitApi_V1+self.accountID+"/messages/preview"
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
                dataCampagne["preview"] = preview_data
                dataCampagne["scheduledAtUtc"] = scheduledAtUtc
                dataCampagne["status"] = "scheduled"
                url_planning  = self.pathInitApi_V1+self.accountID+"/messages/"+dataCampagne["id"]+"?versioned=true"
                try:
                    print('ato 2')
                    print(dataCampagne,'-----------')
                    print(url_planning,'-----------')
                    planning_req = requests.put(url_planning, headers= self.headers, json= dataCampagne)
                    print(planning_req)
                    result = self.checkRequest(planning_req)
                    if "etat" not in result:
                        result["etat"] = "success"
                except Exception as e:
                    print('ato 2 error')
                    result = {"etat": "error ", "etat_description": str(e)}
        else:
            result = {"etat": "error ", "etat_description":"cette campagne à déja été planifier"}
                
        return result
        