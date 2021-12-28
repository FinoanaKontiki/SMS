
import requests
import json
import re
from sms.sources.message.authentification import authentification

class campagne(authentification):
    def findUrlInBodySMS(self, data):
        result = []
        for value in data:
           urlSearch = re.search("(?<=\[\[url:)(.*)(?=\]])",value['body'])
           value['url'] = urlSearch.group(0) if urlSearch is not None else ''
           result.append(value)
        return result
                
    def getListCampage(self, skip=0, take=20, isArchived=False):
        result  = []
        url = "https://api.cm.com/messages/v1/accounts/"+self.accountID+"/messages?includePreview=true&isArchived="+str(isArchived).lower()+"&skip="+str(skip)+"&take="+str(take)
        try:
            req = requests.get(url,headers={'X-CM-PRODUCTTOKEN': self.token})
            if req.status_code == 200:
                result = self.findUrlInBodySMS(json.loads(req.text))
            else:
                result = {"status": "error "+ str(req.status_code)} 
        except Exception as e:
            result = {"status": "error "+ e}
        return result