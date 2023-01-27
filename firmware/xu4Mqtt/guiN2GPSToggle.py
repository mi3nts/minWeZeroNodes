# # Import tkinter and webview libraries
# from tkinter import *
# import webview
  
# # # define an instance of tkinter
# tk = Tk()
  
# # #  size of the window where we show our website
# tk.geometry("800x450")

# # # Open website
# webview.create_window('MINTS', 'http://mdash.circ.utdallas.edu:3000/d/central_node_demo/central-node-demo?orgId=1&refresh=5s')
# webview.start()


# Import tkinter and webview libraries
import datetime
from mintsXU4 import mintsSensorReader as mSR
from mintsXU4 import mintsDefinitions as mD
import time
from collections import OrderedDict
from os import listdir
from os.path import isfile, join
from mintsXU4 import mintsLatest as mL
import os 
import nmap, socket
import yaml
import json


from PyQt5 import QtWidgets, QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QUrl
import sys

dataFolder          = mD.dataFolder
gpsPort             = mD.gpsPort
statusJsonFile      = mD.statusJsonFile
hostsFile           = mD.hostsFile
locationsFile       = mD.locationsFile
hostsDataFolder     = mD.hostsDataFolder
statusJsonFile      = mD.statusJsonFile
hostsStatusJsonFile = mD.hostsStatusJsonFile
gpsOnJsonFile       = mD.gpsOnJsonFile
gpsOffJsonFile      = mD.gpsOffJsonFile

hosts     = yaml.load(open(hostsFile),Loader=yaml.FullLoader)
locations = yaml.load(open(locationsFile),Loader=yaml.FullLoader)

repos        = locations['locations']['repos']
rawFolder    = locations['locations']['rawFolder']
latestFolder = locations['locations']['latestFolder']



class wearableWindow(QMainWindow):
    def __init__(self):
        super(wearableWindow, self).__init__()
        self.setStyleSheet("background-color: black;")
        self.setGeometry(0,1080-50,1920,50)
        self.setWindowTitle("MINTS Wearable EOD 001")
        self.connected = False
        self.prevConnected = False
        self.initUI()

    def initUI(self):

        # creating label for the UTD Logo 
        self.utdLogo = QLabel(self)
        self.utdLogo.setGeometry(QtCore.QRect(1920-95,5,40,40))
        self.utdLogo.setText("")
        self.utdLogo.setPixmap(QtGui.QPixmap('res/utd.png'))
        self.utdLogo.setScaledContents(True)
        self.utdLogo.setObjectName("UTD Logo")
        
        # creating label for the Mints Logo 
        self.mintsLogo = QLabel(self)
        self.mintsLogo.setGeometry(QtCore.QRect(1920-50,5,40,40))
        self.mintsLogo.setText("")
        self.mintsLogo.setPixmap(QtGui.QPixmap('res/mi3nts.png'))
        self.mintsLogo.setScaledContents(True)
        self.mintsLogo.setObjectName("Mints Logo")

        self.infoTextUTD = QtWidgets.QLabel(self)
        self.infoTextUTD.setGeometry(QtCore.QRect(1920-920,5,920-100,25))
        self.infoTextUTD.setText("The University of Texas at Dallas")
        self.infoTextUTD.setAlignment(QtCore.Qt.AlignRight)
        self.infoTextUTD.setStyleSheet("color: grey;") 
        
        self.infoTextMints = QtWidgets.QLabel(self)
        self.infoTextMints.setGeometry(QtCore.QRect(1920-920,27,920-100,25))
        self.infoTextMints.setText("Multi-Scale Integrated Interactive Intelligent Sensing & Simulation for Actionable Insights in Service of Society")
        self.infoTextMints.setAlignment(QtCore.Qt.AlignRight)
        self.infoTextMints.setStyleSheet("color: grey;") 
                
        # creating label for the Mints Logo 
        self.statusBar = QtWidgets.QLabel(self)
        self.statusBar.setGeometry(QtCore.QRect(100,0,1000-100,50))
        self.statusBar.setText("")
        self.statusBar.setFont(QFont('Courier', 14))        
        self.statusBar.setAlignment(QtCore.Qt.AlignLeft)
        self.statusBar.setAlignment(QtCore.Qt.AlignVCenter)
        self.statusBar.setStyleSheet("color: white;") 

        self.gpsButton = QtWidgets.QPushButton(self)
        self.gpsButton.setGeometry(QtCore.QRect(5,5,90,40))        
        self.gpsButton.setText("GPS")
        self.gpsButton.setFont(QFont('SansSerif', 12, QFont.Bold))
        self.gpsButton.setStyleSheet("color: white;") 
        self.gpsButton.clicked.connect(self.mainGPS)


    def mainGPS(self):
        hostFound,hostID,hostIP =  self.getHostMac()
        if self.connected and hostFound:
            self.gpsToggle(hostFound,hostID,hostIP)
        else:
            self.gpsCheck(hostFound,hostID,hostIP)

    
    def getHostMac(self):
        self.updateStatusBar("Looking for a host...")
        scanner = nmap.PortScanner()
        hostNodes = hosts['nodeIDs']
        for hostIn in hostNodes:
            ipAddress = hostIn['IP']    
            host = socket.gethostbyname(ipAddress)
            scanner.scan(host, '1', '-v')
            ipState = scanner[host].state()
            if ipState == "up":
                hostID = os.popen("ssh teamlary@"+ ipAddress+' "cat /sys/class/net/eth0/address"').read().replace(":","").replace("\n","")
                if hostID == hostIn['nodeID']:
                    self.updateStatusBar("Host " + hostID + " found @" + ipAddress)
                    return True, hostID,hostIn['IP'];
                else:
                    print("Host " + hostID + " found with incorrect IP:" + ipAddress)
                    return False, 0,0;
        
        self.updateStatusBar("No hosts found")
        self.gpsButton.setStyleSheet("border-color: white;"
                                             "color: white;") 
        time.sleep(1)
        self.updateStatusBar("")                                              
        return False, -1,0;

    def updateStatusBar(self,strIn):
        print(strIn)
        self.statusBar.setText(strIn)
        QApplication.processEvents() 
        time.sleep(1)

    def readLatestTime(self,hostID,sensorID):
        
        fileName = latestFolder + "/" + hostID+"_"+sensorID+".json"
        if os.path.isfile(fileName):
            try:    
                with open(fileName, 'r') as f:
                    data = json.load(f)
                return datetime.datetime.strptime(data['dateTime'],'%Y-%m-%d %H:%M:%S.%f')

            except Exception as e:
                print(e)
        else:
            return datetime.datetime.strptime("2022-10-04 22:40:40.204179",'%Y-%m-%d %H:%M:%S.%f')
    
    def writeLatestTime(self,hostID,sensorID,dateTime):
        fileName = latestFolder + "/" + hostID+"_"+sensorID+".json"
        mSR.directoryCheck2(fileName)
        sensorDictionary = OrderedDict([
                    ("dateTime"            ,str(dateTime))
                    ])
        with open(fileName, "w") as outfile:
            json.dump(sensorDictionary,outfile)


    def gpsCheck(self,hostFound,hostID,hostIP):
        if hostFound:
            print("Reading Current GPS Status")
            mSR.directoryCheck2(hostsStatusJsonFile)
            out = os.popen('rsync -avzrtu -e "ssh" teamlary@' +hostIP+":"+statusJsonFile+" "+ hostsStatusJsonFile).read()
            self.updateCurrentGPSStatus(hostID,True)
            self.connected = True
        else:
            self.connected = False





    def gpsToggle(self,hostFound,hostID,hostIP):
        if hostFound:
            mSR.directoryCheck2(hostsStatusJsonFile)
            out = os.popen('rsync -avzrtu -e "ssh" teamlary@' +hostIP+":"+statusJsonFile+" "+ hostsStatusJsonFile).read()

            dateTime = datetime.datetime.now() 
            if mSR.gpsStatus(hostsStatusJsonFile):
                self.updateStatusBar("GPS Currently Active, Turning GPS Off")
                out = os.popen("ssh teamlary@"+ hostIP+' "cd ' + repos + 'minWeNodes/firmware/xu4Mqtt && ./gpsHalt.sh"').read()

                time.sleep(0.1)
                out = os.popen('scp ' + gpsOffJsonFile + ' teamlary@' +hostIP+":"+statusJsonFile).read()

                time.sleep(0.1)
                out = os.popen("ssh teamlary@"+ hostIP+' "cd ' + repos + 'minWeNodes/firmware/xu4Mqtt && nohup ./gpsReRun.sh >/dev/null 2>&1 &"').read()
                
                sensorDictionary = OrderedDict([
                    ("dateTime"             ,str(dateTime)),
                    ("active"               ,0),
                    ("toggled"              ,1)
                    ])
                mSR.sensorFinisherWearable(dateTime,hostID,"GPSSTATUS001",sensorDictionary) 

            else:
    
                self.updateStatusBar("GPS Currently Inactive, Turning GPS On")
                out = os.popen("ssh teamlary@"+ hostIP+' "cd ' + repos + 'minWeNodes/firmware/xu4Mqtt && ./gpsHalt.sh"').read()
                time.sleep(0.1)

                out = os.popen('scp ' + gpsOnJsonFile + ' teamlary@' +hostIP+":"+statusJsonFile).read()
                time.sleep(0.1)

                out = os.popen("ssh teamlary@"+ hostIP+' "cd ' + repos + 'minWeNodes/firmware/xu4Mqtt &&  nohup ./gpsReRun.sh >/dev/null 2>&1 &"').read()

                sensorDictionary = OrderedDict([
                    ("dateTime"             ,str(dateTime)),
                    ("active"               ,1),
                    ("toggled"              ,1)
                    ])
                mSR.sensorFinisherWearable(dateTime,hostID,"GPSSTATUS001",sensorDictionary) 


            out = os.popen('rsync -avzrtu -e "ssh" teamlary@' +hostIP+":"+statusJsonFile+" "+ hostsStatusJsonFile).read()
            print("Current GPS Status:", mSR.gpsStatus(hostsStatusJsonFile))
            self.updateCurrentGPSStatus(hostID,False)
        else:
            time.sleep(1)    

    def updateCurrentGPSStatus(self,hostID,justChecking):
        dateTime = datetime.datetime.now() 
        if(mSR.gpsStatus(hostsStatusJsonFile)):
            if justChecking:
                sensorDictionary = OrderedDict([
                    ("dateTime"             ,str(dateTime)),
                    ("active"               ,1),
                    ("toggled"              ,0)
                    ])
                mSR.sensorFinisherWearable(dateTime,hostID,"GPSSTATUS001",sensorDictionary) 

            self.gpsButton.setStyleSheet("border :1px solid ;"
                                                "border-bottom-color : green;"
                                                "color: white;")
            QApplication.processEvents() 
            self.updateStatusBar("GPS ON")       
            self.updateStatusBar(" ")
        else:
            if  justChecking:
                sensorDictionary = OrderedDict([
                    ("dateTime"             ,str(dateTime)),
                    ("active"               ,0),
                    ("toggled"              ,0)
                    ])
                mSR.sensorFinisherWearable(dateTime,hostID,"GPSSTATUS001",sensorDictionary) 

            self.gpsButton.setStyleSheet("border :1px solid ;"
                                                "border-bottom-color : red;"
                                                "color: white;")
            QApplication.processEvents() 
            self.updateStatusBar("GPS OFF")
            time.sleep(1)
            self.updateStatusBar(" ")
    

    
def window():
    app = QApplication(sys.argv)
    win = wearableWindow()
    win.show()
    sys.exit(app.exec_())

window()



