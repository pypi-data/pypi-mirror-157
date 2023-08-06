from importlib.metadata import version
import subprocess
import requests
import os

name_package_os = "ticsummary_domain"
name_package_pypi = "neofti_ticsummary_domain"
currentVersion = version(name_package_pypi)
needUpdate = False
url = f"https://pypi.org/pypi/{name_package_pypi}/json"

def startApp():
    print("Start app")
    subprocess.run(["python", "-m", name_package_os])

def update():
    print("Updating...")
    subprocess.run(["python", "-m", "pip","install","--upgrade",name_package_pypi])

def __messageBoxClickedUpdate__():
    update()
    startApp()

def checkUpdate():
    r = requests.get(url)
    data = r.json()
    listVersions = data["releases"].keys()
    file_path = os.path.realpath(__file__).rsplit(os.sep,1)[0]

    splitCurrentVersion = currentVersion.split('.')
    valueCurrentVersion = int(splitCurrentVersion[0])*100 + int(splitCurrentVersion[1])*10 + int(splitCurrentVersion[2])
    lastValueVersion = 0 
    for pypiVersion in listVersions:
        splitPypiVersion = pypiVersion.split('.')
        valuePypiVersion = int(splitPypiVersion[0])*100 + int(splitPypiVersion[1])*10 + int(splitPypiVersion[2]) 
        if lastValueVersion < valuePypiVersion:
            lastValueVersion = valuePypiVersion
            lastVersion = pypiVersion
    needUpdate = lastValueVersion <= valueCurrentVersion
    if needUpdate:
        print("need Update")
        from PyQt6.QtWidgets import QMessageBox,QApplication
        import sys

        comment = data["releases"][lastVersion][0]['comment_text']
        app = QApplication(sys.argv)
        messageBox = QMessageBox()#title="Exit new version. Update?",text=comment)
        messageBox.setWindowTitle("New version available. Update?")
        messageBox.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        messageBox.accepted.connect(__messageBoxClickedUpdate__)
        messageBox.rejected.connect(lambda:startApp())
        if comment=="":
            messageBox.setText("Empty comment")
        else:
            messageBox.setText(comment)
        messageBox.show()
        sys.exit(app.exec())
    else:
        startApp()

if __name__ == "__main__":
    checkUpdate()
    #update()
    #startApp()
