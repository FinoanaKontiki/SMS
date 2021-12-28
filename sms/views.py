from flask import Flask,jsonify
from .sources.server.ftp import ftp
from .sources.files import files
from .sources.departement import departement
from .sources.message.authentification import authentification
from .sources.message.campagne import campagne

app = Flask(__name__)

# Config options - Make sure you created a 'config.py' file.
app.config.from_object('config')
# To get one variable, tape app.config['MY_VARIABLE']

camp = campagne("34f7db5c-48ac-42c2-8f5e-da39e4e28bbe","36864ae2-4ff5-422b-af69-f5cafaaa413a")

@app.route('/')
def index():
        return "Hello world !"

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
        
if __name__ == "__main__":
        app.run()
