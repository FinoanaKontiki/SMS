import pandas as pd
import urllib.request
from pandas.core.algorithms import mode

from sms.authentification import authentification

class files(authentification):
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
      
    def appendContentsInFile(self, dataToAppend, fileToAdd):
        try:
            dataToAppend.to_csv(fileToAdd, sep=',', mode='a', index =False, header=False)
        except Exception as e:
            print(e)
            
    def filterFile(self, contentFileFrame):
        print(contentFileFrame)    
        
    def downloadFiles(self, idCampagne, fileType):
        url = "https://api.cm.com/messages/v1/accounts/"+self.accountID+"/messages/"+idCampagne+"/export?status="+fileType
        pathSaveFile = "C:\\PROJECT\\DOC\\CM\\Download\\"+idCampagne+"_"+fileType+".csv"
        try:
            confOpen = urllib.request.build_opener()
            confOpen.addheaders=[('X-CM-PRODUCTTOKEN',self.token)]
            urllib.request.install_opener(confOpen)
            req=urllib.request.urlretrieve(url,pathSaveFile)
            print(req)
        except Exception as e:
            print(e)
        