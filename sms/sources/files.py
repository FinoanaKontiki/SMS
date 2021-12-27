import pandas as pd
from pandas.core.algorithms import mode

class files:
    def __init__(self):
        pass
    
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
        