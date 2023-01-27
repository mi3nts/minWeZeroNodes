
import serial
import datetime
from mintsXU4 import mintsSensorReader as mSR
from mintsXU4 import mintsDefinitions as mD
import time
import serial
import pynmea2
from collections import OrderedDict

import json

dataFolder     = mD.dataFolder
gpsPort        = mD.gpsPort
statusJsonFile = mD.statusJsonFile

baudRate  = 9600

def main():
    mSR.gpsStatus(statusJsonFile)
    reader = pynmea2.NMEAStreamReader()
    ser = serial.Serial(
    port= gpsPort,\
    baudrate=baudRate,\
    parity  =serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=0)

    lastGPRMC = time.time()
    lastGPGGA = time.time()
    delta  = 2
    print("connected to: " + ser.portstr)

    #this will store the line
    line = []
    while True:
        try:
            for c in ser.read():
                line.append(chr(c))
                if chr(c) == '\n':
                    dataString     = (''.join(line))
                    dateTime  = datetime.datetime.now()
                    
                    if (dataString.startswith("$GPGGA") and mSR.getDeltaTime(lastGPGGA,delta)):
                        if mSR.gpsStatus(statusJsonFile):
                            lastGPGGA = time.time()
                            mSR.GPSGPGGA2Write(dataString,dateTime)
                        
                    if (dataString.startswith("$GPRMC") and mSR.getDeltaTime(lastGPRMC,delta)):
                        if mSR.gpsStatus(statusJsonFile):    
                            lastGPRMC = time.time()
                            mSR.GPSGPRMC2Write(dataString,dateTime)
                       
                    line = []
                    break
        except Exception as e:
            
            print(e)
            print()
            
    ser.close()



if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    print("Monitoring GPS Sensor on port: {0}".format(gpsPort[0])+ " with baudrate " + str(baudRate))
    main()