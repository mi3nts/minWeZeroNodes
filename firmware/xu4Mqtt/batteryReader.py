import datetime
import odroid_wiringpi as wpi
import time
from collections import OrderedDict
from mintsXU4 import mintsSensorReader as mSR
import os
wpi.wiringPiSetup()

debug  = False 

def main():
    while True:
        try:
            dateTime          = datetime.datetime.now()
            batteryLevelRaw   = wpi.analogRead(25)
            referenceLevelRaw = wpi.analogRead(29)
            batteryLevel      = batteryLevelRaw*(2.1*2)/(4095)
            #batteryLevelPercetage = batteryLevel*(100/4.2)
            batteryLevelPercetage = (batteryLevel-2.5)*(100)/(3.25-2.5)


            sensorDictionary =  OrderedDict([
                    ("dateTime"               ,str(dateTime)), # always the same
                    ("batteryLevelRaw"        ,str(batteryLevelRaw)), # check with arduino code
                    ("batteryLevel"           ,str(batteryLevel)),
                    ("batteryLevelPercetage"  ,str(batteryLevelPercetage)),
                    ("referenceLevelRaw"      ,str(referenceLevelRaw))
                    ])
            
            if batteryLevelPercetage< 5:
                # Shut Down Node 
                print("Low Battery - Shutting Down PC")
#                os.system("sudo shutdown now")
    

            mSR.sensorFinisher(dateTime,"MWBL001",sensorDictionary)
            time.sleep(30)


        except Exception as e:
            print(e)
            break


if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")
    print("Monitoring Battery level for Mints Wearable Node")
    main()
