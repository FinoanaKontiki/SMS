from select import select
from flask import Flask,jsonify,request
from .sources.server.ftp import ftp
from .sources.server.files import files
from .sources.server.ftp import ftp
from .sources.departement import departement
from .sources.message.campagne import campagne
from .sources.message.contacts import contacts
from .sources.capture.image import image
from sms.color import colors
app = Flask(__name__)

# Config options - Make sure you created a 'config.py' file.
app.config.from_object('config')
# To get one variable, tape app.config['MY_VARIABLE']

camp = campagne("34f7db5c-48ac-42c2-8f5e-da39e4e28bbe","36864ae2-4ff5-422b-af69-f5cafaaa413a")

@app.route('/connectServer')
def connectServer():
        server = ftp("kr@clubdesreduc.eu","_1"'%'"o{=nEmbPA'","160.153.244.152")
        server.connectToServer()
        return jsonify({'message': 'conected'})

@app.route('/formatFiles')
def formatFiles():
        fichier = files()
        dataToAdd = fichier.formatFile("C:\\PROJECT\\DOC\\HEMEA-2021-04.csv","delivered")
        # dataToAdd = fichier.formatFile("C:\\PROJECT\\DOC\\test\\HEMEA-2021-04-append.csv","all")
        fichier.appendContentsInFile(dataToAdd, "C:\\PROJECT\\DOC\\test\\HEMEA-2021-04-append.csv")
        return jsonify({'message': 'ok'})

@app.route('/findDepartement')
def findDepartement():
        dep = departement()
        dataRange = [{'debut':'01','fin':'06'},{'debut':'65','fin':'90'}]
        range = dep.range(dataRange)
        # print(range)
        return jsonify(range)

@app.route('/listeCampagne')
def listeCampagne():
        liste = camp.getListCampage(take=100)
        # print(type(eval(result)))
        allId = [data['id'] for data in liste['value']]
        # return jsonify(result)
        return jsonify(allId)
        return jsonify(liste)

@app.route('/getCampagne')
def getCampagne():
        liste = camp.getCampagne(idCampagne="05dce27b-9451-4697-a3a5-ef42c588fd81")
        return jsonify(liste)

@app.route('/getCountCampagne')
def getCountCampagne():
        liste = camp.getCountCampagne()
        return jsonify(liste)

@app.route('/sendMessageTest')
def sendMessageTest():
        liste = camp.sendMessageTest(idCamp="a9878be0-70e5-49ab-9bb2-5a9472b74ad4",phoneTosend="00447716885606")
        return jsonify(liste)

@app.route('/duplicateCampagne')
def duplicateCampagne():
        liste = camp.duplicateCampagne(idOldCapagne="a9878be0-70e5-49ab-9bb2-5a9472b74ad4")
        return jsonify(liste)

@app.route('/createDraftCampagne')
def createDraftCampagne():
        body = "Campagne TEST, cliquez ici : [[https://www.cm.com/app/docs/en/api/messages/v1/index/#advanced_features]]"
        liste = camp.createDraft(senderName="Verisure TEST send name", idGroup="52956a3d-28f3-4b7e-a9a0-2131394b551b",bodySms=body, nameCampagne="TEST verisure PLANIFICATION 30/12/2021 - 3")
        return jsonify(liste)

@app.route('/updateCampagne')
def updateCampagne():
        data = {
                "body": "Campagne TEST UPDATE SHEDULED,cliquez ici : [[https://www.cm.com/app/docs/en/api/messages/v1/index/#advanced_features]]",
                "channels": ["SMS"],
                "ignoreUnsubscribes": False,
                "isArchived": False,
                "isStatsComplete": False,
                "name": "TEST UPDATE SHEDULED",
                "recipients": [
                        {
                        "group": "52956a3d-28f3-4b7e-a9a0-2131394b551b"
                        }
                ],
                "scheduledAtUtc": "2023-01-04T08:31:11.3630934Z",
                "senders": [
                        "verisure"
                ],
                "status": "scheduled",
            }
        liste = camp.updateCampagne("320bebc9-7944-4552-bb70-d0cdc5046f7e", data)
        return jsonify(liste)

@app.route('/planifierCampagne')
def planifierCampagne():
        result = camp.planifierCampagne(idCampagne="320bebc9-7944-4552-bb70-d0cdc5046f7e", scheduledAtUtc="2022-12-29T13:24:58.2109794Z")
        return jsonify(result)

@app.route('/setSenders')
def setSenders():
        cont = contacts("34f7db5c-48ac-42c2-8f5e-da39e4e28bbe","36864ae2-4ff5-422b-af69-f5cafaaa413a")
        result =cont.addSenders("test senders",False)
        return jsonify(result)

@app.route('/createGroupe')
def createGroupe():
        cont = contacts("34f7db5c-48ac-42c2-8f5e-da39e4e28bbe","36864ae2-4ff5-422b-af69-f5cafaaa413a")
        result = cont.addGroup(nameGroup="groupe 1 test")
        return jsonify(result)

@app.route('/listGroup')
def listGroup():
        cont = contacts("34f7db5c-48ac-42c2-8f5e-da39e4e28bbe","36864ae2-4ff5-422b-af69-f5cafaaa413a")
        result = cont.listGroup(take=50)
        # print(type(eval(result)))
        allId = [data['id'] for data in result['value']]
        # return jsonify(result)
        return jsonify(allId)

@app.route('/ajouterContact_group')
def addGroupContact():
        cont = contacts("34f7db5c-48ac-42c2-8f5e-da39e4e28bbe","36864ae2-4ff5-422b-af69-f5cafaaa413a")
        contactsIbfo = {
                        "firstName": "Fy",
                        "insertion": "van",
                        "lastName": "Kontiki",
                        "email": "finoana.kontiki.dev@gmail.com",
                        "phoneNumber": "+33757130251",
                        "groupId": "52956a3d-28f3-4b7e-a9a0-2131394b551b",
                        "fieldId": 6,
                        "value": "Test Company"
                        }
        result = cont.addContactInGroup(nameGroup="groupe 1 test")
        return jsonify(result)

#type file converted, delivered, undelivered, 
@app.route('/downloadFile')
def downloadFile():
        down = files("34f7db5c-48ac-42c2-8f5e-da39e4e28bbe","36864ae2-4ff5-422b-af69-f5cafaaa413a")
        # download = down.downloadFiles("2c5979c7-2199-4ed6-812c-9d17cdc698e1",fileType="undelivered")
        download = down.downloadFiles("2c5979c7-2199-4ed6-812c-9d17cdc698e1",fileType="optedOut")
        return jsonify(download)

@app.route('/filter')
def filter():
        file = files("34f7db5c-48ac-42c2-8f5e-da39e4e28bbe","36864ae2-4ff5-422b-af69-f5cafaaa413a")
        path = "C:\\PROJECT\\SMS\\sms\\tmp\\converted\\a26aa25e-e86e-4189-a930-2124a85809ad_20211221T114030347922Z_converted.csv"
        dataFile = {"etat": "success", "pathFile":path, "idStats": "02", "fileType": "converted"}
        resultFilter = file.filterFile(dataFile)
        pathAppend = "C:\\PROJECT\\SMS\\sms\\tmp\\Append\\TEST.csv"
        add = file.appendContentsInFile(dataToAppend=resultFilter, fileType="converted")
        # return jsonify(result.to_json(orient='records')[1:-1].replace('},{', '} {'))
        return jsonify({"capture":"ok"})





#######################
@app.route('/lunch_DWH_maj', methods=['GET'])
def lunch():
        file = files(accountID=app.config['ACCOUNTID'],token=app.config['TOKEN'])
        serv = ftp(host=app.config['HOST'],user=app.config['USER'], pwd=app.config['PASS'])
        # listeCampagne = request.json["list"]
        listSent = camp.allCampgneByDATE()
        listSplit = file.splitCampagneIDLIst(listSent,5)
        try:
                for listeCampagne in listSplit:
                        file.executThread(listeCampagne)
                ##MAJ DWH FILES
                server_tatus = serv.connectToServer()
                if server_tatus['status'] == "connected": 
                        serv.testEx()
                        result = jsonify({'etat': 'success', 'description': "process finished"})
                else:
                        result = jsonify(server_tatus)
        except Exception as e:
                print(e)
                result = {'etat':'error'}
        
        serv._server.close()
        print(f"{colors.BOLD}{result}{colors.ENDC}")
        return jsonify(result)
     
##CAPTURE HTML TO IMG
@app.route('/capture')
def capture():
        origins = image()
        # origins.capture("C:\\PROJECT\DOC\\capture\\Kit_defiscmini_uneproposition_16072021.html")
        # origins.capture("C:\\PROJECT\DOC\\capture\\homme.html")
        origins.capture("C:\\PROJECT\DOC\\capture\\Kit_Captur_Kontiki_Design_LADVP.html")
        return jsonify({"capture":"ok"})        

###########################server#########################################
@app.route('/connectDWH')
def connectDWH():
        serv = ftp(host=app.config['HOST'],user=app.config['USER'], pwd=app.config['PASS'])
        server_tatus = serv.connectToServer()
        if server_tatus['status'] == "connected": 
                serv.testEx()
        return jsonify(server_tatus)

@app.route('/filterlisteCampagne')
def filterListCamp():
        camp.allCampgneByDATE()
        return jsonify({"capture":"ok"})

if __name__ == "__main__":
        app.run()
