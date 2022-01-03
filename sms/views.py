from flask import Flask,jsonify
from .sources.server.ftp import ftp
from .sources.server.files import files
from .sources.departement import departement
from .sources.message.campagne import campagne
from .sources.message.contacts import contacts
from .sources.capture.image import image

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
        liste = camp.getListCampage()
        return jsonify(liste)

@app.route('/getCampagne')
def getCampagne():
        liste = camp.getCampagne(idCampagne="86a18358-c5aa-4e78-859f-2044e4216c00")
        return jsonify(liste)

@app.route('/duplicateCampagne')
def duplicateCampagne():
        liste = camp.duplicateCampagne(idOldCapagne="8c030812-3806-494d-a601-aba341c0021b")
        return jsonify(liste)

@app.route('/createDraftCampagne')
def createDraftCampagne():
        body = "Campagne TEST, cliquez ici : [[https://www.cm.com/app/docs/en/api/messages/v1/index/#advanced_features]]"
        liste = camp.createDraft(senderName="Verisure TEST send name", idGroup="52956a3d-28f3-4b7e-a9a0-2131394b551b",bodySms=body, nameCampagne="TEST verisure PLANIFICATION 30/12/2021 - 3")
        return jsonify(liste)

@app.route('/planifierCampagne')
def planifierCampagne():
        result = camp.planifierCampagne(idCampagne="86a18358-c5aa-4e78-859f-2044e4216c00", scheduledAtUtc="2022-12-29T13:24:58.2109794Z")
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

@app.route('/downloadFile')
def downloadFile():
        down = files("34f7db5c-48ac-42c2-8f5e-da39e4e28bbe","36864ae2-4ff5-422b-af69-f5cafaaa413a")
        download = down.downloadFiles("a26aa25e-e86e-4189-a930-2124a85809ad",fileType="undelivered")
        return jsonify({'message': 'ok'})

##CAPTURE HTML TO IMG
@app.route('/capture')
def capture():
        origins = image()
        # origins.capture("C:\\PROJECT\DOC\\capture\\Kit_defiscmini_uneproposition_16072021.html")
        # origins.capture("C:\\PROJECT\DOC\\capture\\homme.html")
        origins.capture("C:\\PROJECT\DOC\\capture\\Kit_Captur_Kontiki_Design_LADVP.html")
        return jsonify({"capture":"ok"})        
        
if __name__ == "__main__":
        app.run()
