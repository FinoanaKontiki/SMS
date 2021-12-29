class authentification:
    def __init__(self, accountID, token):
        self.accountID = accountID
        self.token = token
        self.headers = {'X-CM-PRODUCTTOKEN': token}
        