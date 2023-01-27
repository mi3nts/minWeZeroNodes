import json
import serial
import datetime
import os
import csv
#import deepdish as dd
import time
import paho.mqtt.client as mqttClient
import yaml
from mintsXU4 import mintsDefinitions as mD

import ssl

dataFolder          = mD.dataFolder
dataFolderReference = mD.dataFolderReference
macAddress          = mD.macAddress
mqttPort            = mD.mqttPort
mqttBroker          = mD.mqttBroker
mqttCredentialsFile = mD.mqttCredentialsFile

# FOR MQTT 
credentials = yaml.load(open(mqttCredentialsFile),Loader=yaml.FullLoader)
connected   = False  # Stores the connection status
broker      = mqttBroker
port        = mqttPort # Secure port
mqttUN      = credentials['mqtt']['username']  
mqttPW      = credentials['mqtt']['password'] 
tlsCert     = "/etc/ssl/certs/ca-certificates.crt"  # Put here the path of your TLS cert
mqtt_client = mqttClient.Client()

def on_connect(client, userdata, flags, rc):
    global connected  # Use global variable
    if rc == 0:

        print("[INFO] Connected to broker")
        connected = True  # Signal connection
    else:
        print("[INFO] Error, connection failed")


def on_publish(client, userdata, result):
    print("MQTT Published!")


def connect(mqtt_client, mqtt_username, mqtt_password, broker_endpoint, port):
    global connected

    if not mqtt_client.is_connected():
        print("Reconnecting")
        mqtt_client.username_pw_set(mqtt_username, password=mqtt_password)
        mqtt_client.on_connect = on_connect
        mqtt_client.on_publish = on_publish
        mqtt_client.tls_set(ca_certs=tlsCert, certfile=None,
                            keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
                            tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
        mqtt_client.tls_insecure_set(False)
        mqtt_client.connect(broker_endpoint, port=port)
        mqtt_client.loop_start()

        attempts = 0

        while not connected and attempts < 5:  # Wait for connection
            print(connected)
            print("Attempting to connect...")
            time.sleep(1)
            attempts += 1

    if not connected:
        print("[ERROR] Could not connect to broker")
        return False

    return True

# Added for wearable sensor Oct 13th 2022
def writeJSONLatestWearable(hostID,sensorName,sensorDictionary):
    directoryIn  = dataFolder+"/"+hostID+"/"+sensorName+".json"
    print(directoryIn)
    try:
        with open(directoryIn,'w') as fp:
            json.dump(sensorDictionary, fp)

    except:
        print("Json Data Not Written")

def writeMQTTLatestWearable(hostID,sensorName,sensorDictionary):

    if connect(mqtt_client, mqttUN, mqttPW, broker, port):
        try:
            mqtt_client.publish(hostID+"/"+sensorName,json.dumps(sensorDictionary))

        except Exception as e:
            print("[ERROR] Could not publish data, error: {}".format(e))
    
    return True
    

def writeMQTTLatest(sensorDictionary,sensorName):

    if connect(mqtt_client, mqttUN, mqttPW, broker, port):
        try:
            mqtt_client.publish(macAddress+"/"+sensorName,json.dumps(sensorDictionary))

        except Exception as e:
            print("[ERROR] Could not publish data, error: {}".format(e))
    
    return True
    



def writeJSONLatest(sensorDictionary,sensorName):
    directoryIn  = dataFolder+"/"+macAddress+"/"+sensorName+".json"
    print(directoryIn)
    try:
        with open(directoryIn,'w') as fp:
            json.dump(sensorDictionary, fp)

    except:
        print("Json Data Not Written")

def writeJSONLatestReference(sensorDictionary,sensorName):
    directoryIn  = dataFolderReference+"/"+macAddress+"/"+sensorName+".json"
    print(directoryIn)
    try:
        with open(directoryIn,'w') as fp:
            json.dump(sensorDictionary, fp)

    except:
        print("Json Data Not Written")


def readJSONLatestAll(sensorName):
    try:
        directoryIn  = dataFolder+"/"+macAddress+"/"+sensorName+".json"
        with open(directoryIn, 'r') as myfile:
            # dataRead=myfile.read()
            dataRead=json.load(myfile)

        time.sleep(0.01)
        return dataRead, True;
    except:
        print("Data Conflict!")
        return "NaN", False