import os
import sys
import shutil
import datetime
import time
from mintsXU4 import mintsSensorReader as mSR
from mintsXU4 import mintsDefinitions as mD
import yaml

dataFolder    = mD.dataFolder
dataFolderRef = mD.dataFolderReference
macAddress    = mD.macAddress
hostsFile     = mD.hostsFile

hosts     = yaml.load(open(hostsFile),Loader=yaml.FullLoader)
hostNodes = hosts['nodeIDs']

def main():
    dateStart      = datetime.date(2015, 1, 1)
    deleteDaysBack = 60
    dateEnd =  datetime.date.today() -  datetime.timedelta(deleteDaysBack)

    deleteDays = [dateStart + datetime.timedelta(days=x) for x in range((dateEnd-dateStart).days + 1)]

    # Deleting for hosts
    for hostIn in hostNodes:
        hostID = hostIn['nodeID']
         
        for deleteDate in deleteDays:
            try:
#                time.sleep(.01)
                dirPath = os.path.normpath(getDeletePathHost(deleteDate,hostID))
                print("Deleting: "+ dirPath)
                if os.path.exists(dirPath):
                    shutil.rmtree(dirPath)

            except OSError as e:
                print ("Error: %s - %s." % (e.filename, e.strerror))
    

    # Deleting for mac add     
    for deleteDate in deleteDays:
        try:
            dirPath = os.path.normpath(getDeletePath(deleteDate))
            print("Deleting: "+ dirPath)
            if os.path.exists(dirPath):
                shutil.rmtree(dirPath)

        except OSError as e:
            print ("Error: %s - %s." % (e.filename, e.strerror))
        

    for deleteDate in deleteDays:
        try:
            dirPath = os.path.normpath(getDeletePathRef(deleteDate))
            print("Deleting: "+ dirPath)
            if os.path.exists(dirPath):
                shutil.rmtree(dirPath)

        except OSError as e:
            print ("Error: %s - %s." % (e.filename, e.strerror))

def getDeletePathHost(deleteDate,hostID):
    # deleteDate =  datetime.datetime.now() -  datetime.timedelta(daysBefore)
    deletePath = dataFolder+"/"+hostID+"/"+str(deleteDate.year).zfill(4)  + \
    "/" + str(deleteDate.month).zfill(2)+ "/"+str(deleteDate.day).zfill(2)
    # print(deletePath)
    return deletePath;


def getDeletePath(deleteDate):
    # deleteDate =  datetime.datetime.now() -  datetime.timedelta(daysBefore)
    deletePath = dataFolder+"/"+macAddress+"/"+str(deleteDate.year).zfill(4)  + \
    "/" + str(deleteDate.month).zfill(2)+ "/"+str(deleteDate.day).zfill(2)
    # print(deletePath)
    return deletePath;
  

def getDeletePathRef(deleteDate):
    # deleteDate =  datetime.datetime.now() -  datetime.timedelta(daysBefore)
    deletePath = dataFolderRef+"/"+macAddress+"/"+str(deleteDate.year).zfill(4)  + \
    "/" + str(deleteDate.month).zfill(2)+ "/"+str(deleteDate.day).zfill(2)
    # print(deletePath)

    return deletePath;


if __name__ == '__main__':
  main()
