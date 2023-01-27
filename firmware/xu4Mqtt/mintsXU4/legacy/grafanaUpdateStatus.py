# Import tkinter and webview libraries
from fileinput import filename
from tkinter import *
from traceback import print_stack
import webview
import glob
import serial
import datetime
from mintsXU4 import mintsSensorReader as mSR
from mintsXU4 import mintsDefinitions as mD
import time
import serial
import pynmea2
from collections import OrderedDict
from os import listdir
from os.path import isfile, join
from mintsXU4 import mintsLatest as mL
import csv
import os 
import nmap, socket
import yaml
import json

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

def getHostMac():
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
                print("Host " + hostID + " found @" + ipAddress) 
                return True, hostID,hostIn['IP'];
            else:
                print("Host " + hostID + " found with incorrect IP:" + ipAddress)
                return False, 0,0;
    print("No hosts found")                
    return False, -1,0;

def readLatestTime(hostID,sensorID):
    
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
   
def writeLatestTime(hostID,sensorID,dateTime):
    fileName = latestFolder + "/" + hostID+"_"+sensorID+".json"
    mSR.directoryCheck2(fileName)
    sensorDictionary = OrderedDict([
                ("dateTime"            ,str(dateTime))
                ])
    with open(fileName, "w") as outfile:
        json.dump(sensorDictionary,outfile)

def syncHostData(hostFound,hostID,hostIP):
    if hostFound:
        mSR.directoryCheck2(dataFolder+"/"+hostID+"/")
        os.system('rsync -avzrtu -e "ssh" teamlary@' + hostIP + ":" + rawFolder + hostID +"/ " + dataFolder + "/" + hostID)

        csvDataFiles = glob.glob(dataFolder+"/"+hostID+ "/*/*/*/*.csv")
        csvDataFiles.sort()

        for csvFile in csvDataFiles:
            print("================================================")
            print(csvFile)
            try:
                with open(csvFile, "r") as f:
                    sensorID       = csvFile.split("_")[-4]
                    reader            = csv.DictReader(f)
                    rowList           = list(reader)
                    # rowList.sort()
                    # print(rowList)
                    latestDateTime    = readLatestTime(hostID,sensorID)
                    # print(latestDateTime)
                    csvLatestDateTime = datetime.datetime.strptime(rowList[-1]['dateTime'],'%Y-%m-%d %H:%M:%S.%f')

                    if csvLatestDateTime > latestDateTime:
                        for rowData in rowList:
                            dateTimeRow = datetime.datetime.strptime(rowData['dateTime'],'%Y-%m-%d %H:%M:%S.%f')
                            if dateTimeRow > latestDateTime:
                                try:
                                    print("Publishing MQTT Data for Node ID:"+hostID+ " ,Sensor: "+ sensorID+ " ,Time Stamp: "+ str(dateTimeRow))
                                    mL.writeMQTTLatestWearable(rowData,sensorID,hostID)  
                                    time.sleep(0.001)
                                    
                                except Exception as e:
                                    print(e)
                                    print("Data row not published")
                        writeLatestTime(hostID,sensorID,csvLatestDateTime)
                        print("================================================")
                        print("Latest Date Time for Node:"+ hostID + " SensorID:"+ sensorID)
                        print(csvLatestDateTime)
                        print("================================================")

            except Exception as e:
                print(e)
                print("Data file not published")
                print(csvFile)

# def gpsToggle(hostFound,hostID,hostIP):
#     if hostFound:
#         mSR.directoryCheck2(hostsStatusJsonFile)
#         out = os.popen('rsync -avzrtu -e "ssh" teamlary@' +hostIP+":"+statusJsonFile+" "+ hostsStatusJsonFile).read()
#         # print(out)
#         dateTime = datetime.datetime.now() 
#         if mSR.gpsStatus(hostsStatusJsonFile):
#             print("GPS Currently Active, Turning GPS Off")
#             out = os.popen("ssh teamlary@"+ hostIP+' "cd ' + repos + 'minWeNodes/firmware/xu4Mqtt && ./gpsHalt.sh"').read()
#             # print(out)
#             time.sleep(0.1)
#             out = os.popen('scp ' + gpsOffJsonFile + ' teamlary@' +hostIP+":"+statusJsonFile).read()
#             #print()
#             time.sleep(0.1)
#             out = os.popen("ssh teamlary@"+ hostIP+' "cd ' + repos + 'minWeNodes/firmware/xu4Mqtt && nohup ./gpsReRun.sh >/dev/null 2>&1 &"').read()
#             # print(out)
            
#             sensorDictionary = OrderedDict([
#                 ("dateTime"            ,str(dateTime)),
#         	    ("status"              ,str(12))
#                 ])

#             mL.writeMQTTLatestWearable(sensorDictionary,"MWS001",hostID) 

#         else:
   
#             print("GPS Currently Inactive, Turning GPS On")
#             out = os.popen("ssh teamlary@"+ hostIP+' "cd ' + repos + 'minWeNodes/firmware/xu4Mqtt && ./gpsHalt.sh"').read()
#             # print(out)
#             time.sleep(0.1)
#             out = os.popen('scp ' + gpsOnJsonFile + ' teamlary@' +hostIP+":"+statusJsonFile).read()
#             #print(out)
#             time.sleep(0.1)
#             out = os.popen("ssh teamlary@"+ hostIP+' "cd ' + repos + 'minWeNodes/firmware/xu4Mqtt &&  nohup ./gpsReRun.sh >/dev/null 2>&1 &"').read()
#             # print(out)
            
#             sensorDictionary = OrderedDict([
#                 ("dateTime"            ,str(dateTime)),
#         	    ("status"              ,str(11))
#                 ])
#             mL.writeMQTTLatestWearable(sensorDictionary,"MWS001",hostID) 
#         out = os.popen('rsync -avzrtu -e "ssh" teamlary@' +hostIP+":"+statusJsonFile+" "+ hostsStatusJsonFile).read()
#         print("Current GPS Status:", mSR.gpsStatus(hostsStatusJsonFile))
#     else:
#         print("No Host Found")
        



def main():
    hostFound,hostID,hostIP = getHostMac()
    syncHostData(hostFound,hostID,hostIP)
    # gpsToggle(hostFound,hostID,hostIP)


if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    main()