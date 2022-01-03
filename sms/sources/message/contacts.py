import requests
import json
from sms.authentification import authentification

class contacts(authentification):
    
    def addSenders(self, senderName, isFavorite=True):
        url = self.pathInitApi_V1+self.accountID+"/senders"
        data = {
            "isFavorite" : isFavorite,
            "name" : senderName,
            "senders" : {
                "string" : "string"
            }
        }
        try:
            req = requests.get(url,headers=self.headers, json=data)
            result = self.checkRequest(req)
        except Exception as e:
            result = {"status": "error "+ str(e)}
        return result
    
    def addGroup(self, nameGroup):
        url = self.pathInitApi_V2+self.accountID+"/groups"
        data = {"name": nameGroup}
        try:
            req = requests.post(url,headers=self.headers, json=data)
            result = self.checkRequest(req)
        except Exception as e:
            result = {"status": "error "+ str(e)}
        return result
    
    def addContactInGroup(self,dataContacts):
        url = self.pathInitApi_V2+self.accountID+"/groups/"+dataContacts["groupId"]+"/contacts"
        data = {
            "firstName": dataContacts["firstName"],
            "insertion": dataContacts["insertion"],
            "lastName": dataContacts["lastName"],
            "email": dataContacts["email"],
            "phoneNumber": dataContacts["phoneNumber"],
            "groupId": dataContacts["groupId"],
            "customValues": [
                        {
                        "fieldId": dataContacts["fieldId"],
                        "value": dataContacts["value"]
                        }
                ]
            }
        try:
            req = requests.post(url,headers=self.headers, json=data)
            result = self.checkRequest(req)
        except Exception as e:
            result = {"status": "error "+ str(e)}
        return result
    
    def listGroup(self):
        pass