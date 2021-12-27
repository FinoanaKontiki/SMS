class departement:
    def __init__(self):
        fileContent = open('C:\\PROJECT\\DOC\\zipcode.txt', 'r')
        with open('C:\\PROJECT\\DOC\\zipcode.txt', 'r') as fic:
            temp = fic.read()
        self.departementList = eval(temp)
        # print(type(data))
        # self.departementList =[code.split(', ') for code in fileContent.readlines()] 
        
    def range(self, dataRange):
        result = []
        for code in dataRange:
            interval = int(code['fin']) - int(code['debut'])
            for i in range(interval):
                valComp = str(int(code['debut']) + i)
                rangeToCompare = valComp if len(valComp) >= 2 else "0"+valComp
                result.append([depart for depart in self.departementList if depart.startswith(rangeToCompare)])
        return result