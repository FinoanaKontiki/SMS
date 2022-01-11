import json
class authentification:
    def __init__(self, accountID, token):
        self.accountID = accountID
        self.token = token
        self.headers = {'X-CM-PRODUCTTOKEN': token}
        self.pathInitApi_V1_message = "https://api.cm.com/messages/v1/accounts/"
        self.pathInitApi_V2_message = "https://api.cm.com/messages/v2/accounts/"
        self.pathInitApi_V2_addressbook = "https://api.cm.com/addressbook/v2/accounts/"
        self.checkRequest = lambda request : json.loads(request.text) if request.status_code == 200 or request.status_code == 201  else {"etat": "error ", "etat_description": str(request.status_code)} 
        
        
    def replaceCharMultiple(self, string,tupleChar):
        for cr in tupleChar:
                string = string.replace(*cr)
        return string