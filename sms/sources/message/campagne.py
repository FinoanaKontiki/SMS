
import requests
import json
import re
from sms.sources.message.authentification import authentification
from datetime import datetime
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
        url = "https://api.cm.com/messages/v1/accounts/"+self.accountID+"/messages?includePreview=true&isArchived="+str(isArchived).lower()+"&skip="+str(skip)+"&take="+str(take)
        try:
            req = requests.get(url,headers=self.headers)
            result = self.findUrlInBodySMS(json.loads(req.text)) if req.status_code == 200 else {"status": "error "+ str(req.status_code)}
        except Exception as e:
            result = {"status": "error "+ str(e)}
        return result
    
    def getCampagne (self, idCampagne):
        url = "https://api.cm.com/messages/v1/accounts/"+self.accountID+"/messages/"+idCampagne
        try:
            req = requests.get(url,headers=self.headers)
            result = json.loads(req.text) if req.status_code == 200 else {"status": "error "+ str(req.status_code)}
        except Exception as e:
            result = {"status": "error "+ str(e)}
            
        return result
    
    def duplicateCampagne (self, idOldCapagne):
        dataOld = self.getCampagne(idOldCapagne)
        current = str(datetime.now())
        dataDuplicate = {
            "analytics": dataOld['analytics'],
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
        url = "https://api.cm.com/messages/v1/accounts/"+self.accountID+"/messages"
        try:
            req = requests.post(url, headers=self.headers, json=dataDuplicate)
            result = json.loads(req.text) if req.status_code == 200 or req.status_code == 201  else {"status": "error "+ str(req.status_code)}
        except Exception as e:
            result = {"status": "error "+ str(e)}
        return result