# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


'''
/* This file has been modify to be a IoT simulator client and it does
 * follow the same priciples of AWS blog code examples under the 
 * Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * Code contributions and error reporting is encouraged and appreciated, feel free
 * to reach out
 '''
 

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import random
import datetime 
import os
import uuid
from os.path import exists
import subprocess as sp


AllowedActions = ['both', 'publish', 'subscribe']

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")
    
   
    
# Read in command-line parameters
parser = argparse.ArgumentParser()
#removed from original example for the blog demostration
#parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                    help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="/sdk/python/test", help="Targeted topic")
parser.add_argument("-m", "--mode", action="store", dest="mode", default="both",
                    help="Operation modes: %s"%str(AllowedActions))
parser.add_argument("-M", "--message", action="store", dest="message", default="Hello World!",
                    help="Message to publish")

# Gets endpoint
def GetEndpoint():
    cli_cmd = sp.getoutput('aws iot describe-endpoint \
        --endpoint-type "iot:Data-ATS"')
    endpoint_info = json.loads(cli_cmd)
    return(endpoint_info["endpointAddress"])
endpoint = GetEndpoint() 



args = parser.parse_args()
host = f"{endpoint}"
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
useWebsocket = args.useWebsocket
clientId = args.clientId
topic = args.topic
topic1 = "/pumpingstation/1"
topic2 = "/pumpingstation/2"
topic3 = "/pumpingstation/3"
# topic4 = "/pumpingstation/4"
# topic5 = "/pumpingstation/5"



if args.mode not in AllowedActions:
    parser.error("Unknown --mode option %s. Must be one of %s" % (args.mode, str(AllowedActions)))
    exit(2)

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Port defaults
if args.useWebsocket and not args.port:  # When no port override for WebSocket, default to 443
    port = 443
if not args.useWebsocket and not args.port:  # When no port override for non-WebSocket, default to 8883
    port = 8883

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
myAWSIoTMQTTClient.configureMQTTOperationTimeout = 0
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
if args.mode == 'both' or args.mode == 'subscribe':
    myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
time.sleep(2)

#make directory for simulation and create simulation dependency files 

#indentify the path 
directory = "datagen"
parent_dir =  (""+os.getcwd()+"")
path = os.path.join(parent_dir,directory)

#THIS FUNCTION HAS BEEN REMOVED FOR RE-INVENT WORKSHOP
###################################################
#Checks if a simulation profile already exists
profile_exists = os.path.exists(path)

if profile_exists:
    print("Your Profile is already created")
    
    
    #If the profile is not present satart configuration
else:
    #creates Directory for the datageneration JSON_objects and support files
    os.mkdir(path)
    print("Directory '% s' created" % directory)
    
    
    
    #THIS FUNCTION HAS BEEN REMOVED FOR RE-INVENT WORKSHOP
    ####################################################
    #Creation of the simulation profile 
    #Ask about the desired simulation and creates a simulation profile 
    #print("Enter the number of machines you'd like to create (max 1000)")
    n_machines = 10 
    
    #print("Please select your anomaly type"+"\n"+"0 = none"+"\n"+"1 = Contextual outliers")
    anomaly_type = 1
    
    if anomaly_type == 1:
        machine_affected = random.randint(1,n_machines)
        print("Running Contextual outliers anomaly on machine {}.".format(machine_affected))
    else:
        print("Anomaly Not Running")
        machine_affected = 0
    
    simulation_profile ={
                          "Units": n_machines,
                          "AnomalyType":anomaly_type,
                          "MachineAffected": machine_affected
                         
                        }
                        
    with open(""+path+"/simulation_profile.json", 'a') as outfile:
           json.dump(simulation_profile, outfile)
           print(" Simulation profile created")
    
    ####################################################
    #creates UUID repository for (max 999 units)
    #Generates a 1000 units of UUID and save in the file 
    uuid_object = []
    for n in range (1,n_machines+1):
        
        generate_uuid = uuid.uuid4()
        str_uuid = str(generate_uuid)
        item = {n:str_uuid}
        
        uuid_object.append(item)
    
    jsonData=json.dumps(uuid_object)    
    
    with open(""+path+"/uuid_repo.json", 'a') as outfile:
           json.dump(uuid_object, outfile)
           print("{} UUID items created".format(n))
    
    
    #THIS FUNCTION HAS BEEN REMOVED FOR RE-INVENT WORKSHOP
    #####################################################
    #creates Object with list of state ( max 1000 items)
    states_object= []
    for n in range (1,n_machines+1):
        
        states = [ 'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
               'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
               'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
               'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
               'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
               
        state_pick = random.choice(states)
        item = {n:state_pick}
        
        states_object.append(item)
    
    jsonData=json.dumps(states_object)
    
    
    with open(""+path+"/states_list.json", 'a') as outfile:
           json.dump(states_object, outfile)
           print("{} States items created".format(n))


# Publish to the same topic in a loop forever
loopCount = 0
while True:
    
    #This portion has been added for demo purposes in this blog post only 
    
    #indentify the path 
    directory = "datagen"
    parent_dir =  (""+os.getcwd()+"")
    path = os.path.join(parent_dir,directory)
    #print(f"Working from {path}")
    
    ##### Define functions and classes####
    
    #Read JSON object function 
    #Reads the simulation profile - simulation_profile.json
    def readProfile():
        with open(""+path+"/simulation_profile.json", 'r') as openfile:
            object_in = json.load(openfile)
            
        return object_in   
    
    
    #prepare the json file, run once. This function create the baseline template for the data generation
    def datagen_template(n):
        number = str(n)
        datagen_template_data= {
                        "Name" : "pumpingstation"+number,
                        "Location" : "",
                        "UUID" : "",
                        "timestamp": "",
                        "Inference": "",  #provision for inference action from AWS 
                        "Temperature": 50, 
                        "Humidity": 60,
                        "Pressure": 255,
                        "Vibration" : 13, 
                        "Flow": 20,
                        "rpm": 340,
                        "PowerConsumption": 4000,
                        "Amperage": 15,
                        "Voltage": 220,
                        "Fan": False,
                                
                                
                                      
                    }              
            
    
        with open(""+path+"/machine"+number+'.json', 'w') as outfile:
         json.dump(datagen_template_data, outfile)
    
    
    #Read JSON object function 
    #uses UUID to create machine indetification, copies a UUID from uuid_repo.json base don machine number (1-999)
    def readUUID(item):
        with open(""+path+"/"+'uuid_repo.json') as openfile:
            json_uuid_in = json.load(openfile)
            
            n = item-1
            item_s = str(item)
            
            UUID = json_uuid_in[n][item_s]
        
        
        return UUID
    
    #Read JSON object function
    #Uses the pre define state in the json object  states_list.json
    def readLocation(item):
        with open(""+path+"/"+'states_list.json') as openfile:
            json_location_in = json.load(openfile)
            
            n = item-1
            item_s = str(item)
            
            location = json_location_in[n][item_s]
        
        
        return location
    
    
    
    
    #Read JSON object function.
    #evaluate JSON data in and generates new data 
    def ReadJSON(n):
        number = str(n)
        with open(""+path+"/machine"+number+'.json') as openfile:
            json_object_in = json.load(openfile)
            
            #Read profile
            profile = readProfile()
            
            
            #picks the UUID from uui_repo.json
            UUID = readUUID(n)
            #repeats location 
            location = readLocation(n)
            #TIMESTAMP
            timestamp = datetime.datetime.now()
            format_timestamp = timestamp.isoformat()
            
            
            
            
            
            #Evaluating values and setting random increments
            #Check if anomaly is to be generated
            
            if profile["MachineAffected"] == n:
                
                
                #Builds the out message with anomaly
                
                #TEMPERATURE 
                #baseline value Fahrenheit
                temperature = temperature = json_object_in["Temperature"]
                if json_object_in["Temperature"] in range (50,66):
                    temperature = json_object_in["Temperature"] + 21
                elif json_object_in["Temperature"] in range (67,79):
                    temperature = json_object_in["Temperature"] + random.randint(-1,1) 
                elif json_object_in["Temperature"] <=66:
                    temperature = json_object_in["Temperature"] + 1
                elif json_object_in["Temperature"] >=80:
                    temperature = json_object_in["Temperature"] -1
                    
                #HUMIDITY
                #baseline value %
                humidity = json_object_in["Humidity"]
                if json_object_in["Humidity"] in range (60,70):
                    humidity = json_object_in["Humidity"] + random.randint(-1,1)
                elif json_object_in["Humidity"] <=65:
                    humidity = json_object_in["Humidity"] + 1
                elif json_object_in["Humidity"] >=70:
                    humidity = json_object_in["Humidity"] -1 
                    
                #PRESSURE
                #baseline value PSI 
                pressure = json_object_in["Pressure"]
                if json_object_in["Pressure"] in range (220,260):
                    pressure = json_object_in["Pressure"] + random.randint(-10,10)
                elif json_object_in["Pressure"] <=220:
                    pressure = json_object_in["Pressure"] + 5
                elif json_object_in["Pressure"] >=250:
                    pressure = json_object_in["Pressure"] - 5
                    
                #VIBRATION 
                 #baseline value for vibration frequency
                vibration = json_object_in["Vibration"]
                if json_object_in["Vibration"] in range (10,20):
                    vibration = json_object_in["Vibration"] + random.randint(-1,1)
                elif json_object_in["Vibration"] <=15:
                    vibration = json_object_in["Vibration"] + 1
                elif json_object_in["Vibration"] >=20:
                    vibration = json_object_in["Vibration"] -1
                   
                    
                #FLOW
                #baseline value for flow, cubic meters per second 
                flow = json_object_in["Flow"]
                if json_object_in["Flow"] in range (10,20):
                    flow = json_object_in["Flow"] + random.randint(-2,2)
                elif json_object_in["Flow"] <=10:
                    flow = json_object_in["Flow"] + 1
                elif json_object_in["Flow"] >=20:
                    flow = json_object_in["Flow"] - 1
                
                #RPM
                #baseline value fro RPM 
                rpm =json_object_in["rpm"]
                if json_object_in["rpm"] in range (359,429):
                    rpm = json_object_in["rpm"] + 10
                elif json_object_in["rpm"] in range (430,449):
                    rpm = json_object_in["rpm"] + random.randint(-10,10) 
                elif json_object_in["rpm"] <=350:
                    rpm = json_object_in["rpm"] + 10
                elif json_object_in["rpm"] >=450:
                    rpm = json_object_in["rpm"] - 10
                    
                    
                #POWER_CONSUPTION
                #baseline value for the power consuption
                power_consumption = json_object_in["PowerConsumption"]
                power_consumption_randomize = [-25,-50,25,50]
                if json_object_in["PowerConsumption"] in range (4100,4500):
                    power_consumption = json_object_in["PowerConsumption"] + random.choice(power_consumption_randomize)
                elif json_object_in["PowerConsumption"] <=4100:
                    power_consumption = json_object_in["PowerConsumption"] + 25
                elif json_object_in["PowerConsumption"] >=4500:
                    power_consumption = json_object_in["PowerConsumption"] - 25    
                
                #AMPERAGE   
                #baseline value for amperage
                amperage = json_object_in["Amperage"]
                if json_object_in["Amperage"] in range (16,20):
                    amperage = json_object_in["Amperage"] + random.randint(-1,1)
                elif json_object_in["Amperage"] <=16:
                    amperage = json_object_in["Amperage"] + 1
                elif json_object_in["Amperage"] >=20:
                    amperage = json_object_in["Amperage"] - 1
                    
                #VOLTAGE  
                #baseline value for voltage
                voltage = json_object_in["Voltage"]
                if json_object_in["Voltage"] in range (215,219):
                    voltage = json_object_in["Voltage"] + random.randint(-1,1)
                elif json_object_in["Voltage"] <=215:
                    voltage = json_object_in["Voltage"] + 1
                elif json_object_in["Voltage"] >=219:
                    voltage = json_object_in["Voltage"] - 1
                    
                #OVERRIDE - FAN
                #during anomaly FAN is always TRUE
                manual_override = True
                
               
                
                
                out_message = {
                            "Name" : "pumpingstation"+number,
                            "Location" : location,
                            "UUID" : UUID,
                            "timestamp": format_timestamp,
                            "Inference": "",  #provision for inference action from AWS 
                            "Temperature": temperature, 
                            "Humidity": humidity,
                            "Pressure": pressure,
                            "Vibration" : vibration, 
                            "Flow": flow,
                            "rpm": rpm,
                            "PowerConsumption": power_consumption,
                            "Amperage": amperage,
                            "Voltage": voltage,
                            "Fan": manual_override,
                                   
                                }
                                          
                                        
                        
                
            else:    
                
                #Builds the out message without anomaly   
                    
                #TEMPERATURE 
                #baseline value Fahrenheit
                temperature = json_object_in["Temperature"]
                if json_object_in["Temperature"] in range (45,55):
                    temperature = json_object_in["Temperature"] + random.randint(-1,1)
                elif json_object_in["Temperature"] <=45:
                    temperature = json_object_in["Temperature"] + 1
                elif json_object_in["Temperature"] >=55:
                    temperature = json_object_in["Temperature"] -1
                    
                #HUMIDITY
                #baseline value %
                humidity = json_object_in["Humidity"] 
                if json_object_in["Humidity"] in range (60,65):
                    humidity = json_object_in["Humidity"] + random.randint(-1,1)
                elif json_object_in["Humidity"] <=60:
                    humidity = json_object_in["Humidity"] + 1
                elif json_object_in["Humidity"] >=65:
                    humidity = json_object_in["Humidity"] -1 
                    
                #PRESSURE
                #baseline value PSI 
                pressure = json_object_in["Pressure"]
                if json_object_in["Pressure"] in range (240,260):
                    pressure = json_object_in["Pressure"] + random.randint(-10,10)
                elif json_object_in["Pressure"] <=240:
                    pressure = json_object_in["Pressure"] + 5
                elif json_object_in["Pressure"] >=260:
                    pressure = json_object_in["Pressure"] - 5
                    
                #VIBRATION 
                #baseline value for vibration frequency
                vibration = json_object_in["Vibration"]
                if json_object_in["Vibration"] in range (11,14):
                    vibration = json_object_in["Vibration"] + random.randint(-1,1)
                elif json_object_in["Vibration"] <=11:
                    vibration = json_object_in["Vibration"] + 1
                elif json_object_in["Vibration"] >=14:
                    vibration = json_object_in["Vibration"] -1
                   
                    
                #FLOW
                #baseline value for flow, cubic meters per second 
                flow = json_object_in["Flow"]
                if json_object_in["Flow"] in range (15,25):
                    flow = json_object_in["Flow"] + random.randint(-2,2)
                elif json_object_in["Flow"] <=15:
                    flow = json_object_in["Flow"] + 1
                elif json_object_in["Flow"] >=25:
                    flow = json_object_in["Flow"] - 1
                
                #RPM
                #baseline value for level starting from 50%
                rpm = json_object_in["rpm"]
                if json_object_in["rpm"] in range (300,350):
                    rpm = json_object_in["rpm"] + random.randint(-10,10)
                elif json_object_in["rpm"] <=300:
                    rpm = json_object_in["rpm"] + 10
                elif json_object_in["rpm"] >=350:
                    rpm = json_object_in["rpm"] - 10
                    
                #POWER_CONSUPTION
                #baseline value for the power consuption
                power_consumption = json_object_in["PowerConsumption"]
                power_consumption_randomize = [-25,-50,25,50]
                if json_object_in["PowerConsumption"] in range (3800,4200):
                    power_consumption = json_object_in["PowerConsumption"] + random.choice(power_consumption_randomize)
                elif json_object_in["PowerConsumption"] <=3800:
                    power_consumption = json_object_in["PowerConsumption"] + 25
                elif json_object_in["PowerConsumption"] >=4200:
                    power_consumption = json_object_in["PowerConsumption"] - 25    
                
                #AMPERAGE   
                #baseline value for amperage
                amperage = json_object_in["Amperage"]
                if json_object_in["Amperage"] in range (12,16):
                    amperage = json_object_in["Amperage"] + random.randint(-1,1)
                elif json_object_in["Amperage"] <=12:
                    amperage = json_object_in["Amperage"] + 1
                elif json_object_in["Amperage"] >=16:
                    amperage = json_object_in["Amperage"] - 1
                    
                #VOLTAGE  
                #baseline value for voltage
                voltage = json_object_in["Voltage"]
                if json_object_in["Voltage"] in range (218,224):
                    voltage = json_object_in["Voltage"] + random.randint(-1,1)
                elif json_object_in["Voltage"] <=218:
                    voltage = json_object_in["Voltage"] + 1
                elif json_object_in["Voltage"] >=224:
                    voltage = json_object_in["Voltage"] - 1
                    
               
               #OVERRIDE - FAN
                #during normal operation FAN is always false
                manual_override = False
                
                
                
                
                out_message = {
                            "Name" : "pumpingstation"+number,
                            "Location" : location,
                            "UUID" : UUID,
                            "timestamp": format_timestamp,
                            "Inference": "",  #provision for inference action from AWS 
                            "Temperature": temperature, 
                            "Humidity": humidity,
                            "Pressure": pressure,
                            "Vibration" : vibration, 
                            "Flow": flow,
                            "rpm": rpm,
                            "PowerConsumption": power_consumption,
                            "Amperage": amperage,
                            "Voltage": voltage,
                            "Fan": manual_override,
                            
                                
                                          
                        }  
            
            return out_message
    
    
    #Write results from evaluation to JSON object in memory
    def WriteJSON(n,strng):
        number = str(n)
        with open(""+path+"/machine"+number+'.json', 'w') as outfile:
            json.dump(strng, outfile)
        
    current_profile = readProfile()           
    for n in range(1,current_profile["Units"]+1):
        datagen_template(n)
    
    for n in range (1,current_profile["Units"]+1):
    
        #read json file latest data
        json_object_in = ReadJSON(n)
        json_object_in_1 = ReadJSON(1)
        json_object_in_2 = ReadJSON(2)
        json_object_in_3 = ReadJSON(3)
        json_object_in_4 = ReadJSON(4)
        json_object_in_5 = ReadJSON(5)
        json_object_in_6 = ReadJSON(6)
        json_object_in_7 = ReadJSON(7)
        json_object_in_8 = ReadJSON(8)
        json_object_in_9 = ReadJSON(9)
        json_object_in_10 = ReadJSON(10)
        WriteJSON(n,json_object_in)
        
     
    
    
    if args.mode == 'both' or args.mode == 'publish':
        
  
        
        
        
        message1 = {'station': {},'pumpA': {}, 'pumpB' : {}}
        #message['message'] = args.message
        message1['station']['sequence'] = loopCount
        message1['station']['Alias'] = "/pumpingstation/001"
        message1['station']['Location'] = json_object_in_1["Location"]
        message1['station']['UUID'] = json_object_in_1["UUID"]
        message1['station']['Inference'] = json_object_in_1["Inference"]
        
        message1['pumpA']['Temperature'] = json_object_in_1["Temperature"]
        message1['pumpA']['Humidity'] = json_object_in_1["Humidity"]
        message1['pumpA']['Pressure'] = json_object_in_1["Pressure"]
        message1['pumpA']['Vibration'] = json_object_in_1["Vibration"]
        message1['pumpA']['Flow'] = json_object_in_1["Flow"]
        message1['pumpA']['rpm'] = json_object_in_1["rpm"]
        message1['pumpA']['Amperage'] = json_object_in_1["Amperage"]
        message1['pumpA']['Voltage'] = json_object_in_1["Voltage"]
        message1['pumpA']['Fan'] = json_object_in_1["Fan"]
        
        message1['pumpB']['Temperature'] = json_object_in_2["Temperature"]
        message1['pumpB']['Humidity'] = json_object_in_2["Humidity"]
        message1['pumpB']['Pressure'] = json_object_in_2["Pressure"]
        message1['pumpB']['Vibration'] = json_object_in_2["Vibration"]
        message1['pumpB']['Flow'] = json_object_in_2["Flow"]
        message1['pumpB']['rpm'] = json_object_in_2["rpm"]
        message1['pumpB']['Amperage'] = json_object_in_2["Amperage"]
        message1['pumpB']['Voltage'] = json_object_in_2["Voltage"]
        message1['pumpB']['Fan'] = json_object_in_2["Fan"]
        
        
        message2 = {'station': {},'pumpA': {}, 'pumpB' : {}}
        #message['message'] = args.message
        message2['station']['sequence'] = loopCount
        message2['station']['Alias'] = "/pumpingstation/002"
        message2['station']['Location'] = json_object_in_2["Location"]
        message2['station']['UUID'] = json_object_in_2["UUID"]
        message2['station']['Inference'] = json_object_in_2["Inference"]
    
        message2['pumpA']['Temperature'] = json_object_in_3["Temperature"]
        message2['pumpA']['Humidity'] = json_object_in_3["Humidity"]
        message2['pumpA']['Pressure'] = json_object_in_3["Pressure"]
        message2['pumpA']['Vibration'] = json_object_in_3["Vibration"]
        message2['pumpA']['Flow'] = json_object_in_3["Flow"]
        message2['pumpA']['rpm'] = json_object_in_3["rpm"]
        message2['pumpA']['Amperage'] = json_object_in_3["Amperage"]
        message2['pumpA']['Voltage'] = json_object_in_3["Voltage"]
        message2['pumpA']['Fan'] = json_object_in_3["Fan"]
        
        message2['pumpB']['Temperature'] = json_object_in_4["Temperature"]
        message2['pumpB']['Humidity'] = json_object_in_4["Humidity"]
        message2['pumpB']['Pressure'] = json_object_in_4["Pressure"]
        message2['pumpB']['Vibration'] = json_object_in_4["Vibration"]
        message2['pumpB']['Flow'] = json_object_in_4["Flow"]
        message2['pumpB']['rpm'] = json_object_in_4["rpm"]
        message2['pumpB']['Amperage'] = json_object_in_4["Amperage"]
        message2['pumpB']['Voltage'] = json_object_in_4["Voltage"]
        message2['pumpB']['Fan'] = json_object_in_4["Fan"]
        
        
        message3 = {'station': {},'pumpA': {}, 'pumpB' : {}}
        #message['message'] = args.message
        message3['station']['sequence'] = loopCount
        message3['station']['Alias'] = "/pumpingstation/003"
        message3['station']['Location'] = json_object_in_3["Location"]
        message3['station']['UUID'] = json_object_in_3["UUID"]
        message3['station']['Inference'] = json_object_in_3["Inference"]
        
        message3['pumpA']['Temperature'] = json_object_in_5["Temperature"]
        message3['pumpA']['Humidity'] = json_object_in_5["Humidity"]
        message3['pumpA']['Pressure'] = json_object_in_5["Pressure"]
        message3['pumpA']['Vibration'] = json_object_in_5["Vibration"]
        message3['pumpA']['Flow'] = json_object_in_5["Flow"]
        message3['pumpA']['rpm'] = json_object_in_5["rpm"]
        message3['pumpA']['Amperage'] = json_object_in_5["Amperage"]
        message3['pumpA']['Voltage'] = json_object_in_5["Voltage"]
        message3['pumpA']['Fan'] = json_object_in_5["Fan"]
        
        message3['pumpB']['Temperature'] = json_object_in_6["Temperature"]
        message3['pumpB']['Humidity'] = json_object_in_6["Humidity"]
        message3['pumpB']['Pressure'] = json_object_in_6["Pressure"]
        message3['pumpB']['Vibration'] = json_object_in_6["Vibration"]
        message3['pumpB']['Flow'] = json_object_in_6["Flow"]
        message3['pumpB']['rpm'] = json_object_in_6["rpm"]
        message3['pumpB']['Amperage'] = json_object_in_6["Amperage"]
        message3['pumpB']['Voltage'] = json_object_in_6["Voltage"]
        message3['pumpB']['Fan'] = json_object_in_6["Fan"]

       #REMOVED for re - invent

        # message4 = {'station': {},'pumpA': {}, 'pumpB' : {}}
        # #message['message'] = args.message
        # message4['station']['sequence'] = loopCount
        # message4['station']['Alias'] = "/pumpingstation/004"
        # message4['station']['Location'] = json_object_in_4["Location"]
        # message4['station']['UUID'] = json_object_in_4["UUID"]
        # message4['station']['Inference'] = json_object_in_4["Inference"]
        
        # message4['pumpA']['Temperature'] = json_object_in_7["Temperature"]
        # message4['pumpA']['Humidity'] = json_object_in_7["Humidity"]
        # message4['pumpA']['Pressure'] = json_object_in_7["Pressure"]
        # message4['pumpA']['Vibration'] = json_object_in_7["Vibration"]
        # message4['pumpA']['Flow'] = json_object_in_7["Flow"]
        # message4['pumpA']['rpm'] = json_object_in_7["rpm"]
        # message4['pumpA']['Amperage'] = json_object_in_7["Amperage"]
        # message4['pumpA']['Voltage'] = json_object_in_7["Voltage"]
        # message4['pumpA']['Fan'] = json_object_in_7["Fan"]
        
        # message4['pumpB']['Temperature'] = json_object_in_8["Temperature"]
        # message4['pumpB']['Humidity'] = json_object_in_8["Humidity"]
        # message4['pumpB']['Pressure'] = json_object_in_8["Pressure"]
        # message4['pumpB']['Vibration'] = json_object_in_8["Vibration"]
        # message4['pumpB']['Flow'] = json_object_in_8["Flow"]
        # message4['pumpB']['rpm'] = json_object_in_8["rpm"]
        # message4['pumpB']['Amperage'] = json_object_in_8["Amperage"]
        # message4['pumpB']['Voltage'] = json_object_in_8["Voltage"]
        # message4['pumpB']['Fan'] = json_object_in_8["Fan"]
        
        # message5 = {'station': {},'pumpA': {}, 'pumpB' : {}}
        # #message['message'] = args.message
        # message5['station']['sequence'] = loopCount
        # message5['station']['Alias'] = "/pumpingstation/005"
        # message5['station']['Location'] = json_object_in_5["Location"]
        # message5['station']['UUID'] = json_object_in_5["UUID"]
        # message5['station']['Inference'] = json_object_in_5["Inference"]
        
        # message5['pumpA']['Temperature'] = json_object_in_9["Temperature"]
        # message5['pumpA']['Humidity'] = json_object_in_9["Humidity"]
        # message5['pumpA']['Pressure'] = json_object_in_9["Pressure"]
        # message5['pumpA']['Vibration'] = json_object_in_9["Vibration"]
        # message5['pumpA']['Flow'] = json_object_in_9["Flow"]
        # message5['pumpA']['rpm'] = json_object_in_9["rpm"]
        # message5['pumpA']['Amperage'] = json_object_in_9["Amperage"]
        # message5['pumpA']['Voltage'] = json_object_in_9["Voltage"]
        # message5['pumpA']['Fan'] = json_object_in_9["Fan"]
        
        # message5['pumpB']['Temperature'] = json_object_in_10["Temperature"]
        # message5['pumpB']['Humidity'] = json_object_in_10["Humidity"]
        # message5['pumpB']['Pressure'] = json_object_in_10["Pressure"]
        # message5['pumpB']['Vibration'] = json_object_in_10["Vibration"]
        # message5['pumpB']['Flow'] = json_object_in_10["Flow"]
        # message5['pumpB']['rpm'] = json_object_in_10["rpm"]
        # message5['pumpB']['Amperage'] = json_object_in_10["Amperage"]
        # message5['pumpB']['Voltage'] = json_object_in_10["Voltage"]
        # message5['pumpB']['Fan'] = json_object_in_10["Fan"]
        
        
    #REmoved for Re-invent workshop 
        # message6 = {}
        # #message['message'] = args.message
        # message6['sequence'] = loopCount
        # message6['Alias'] = "/pumpingstation/006"
        # message6['Location'] = json_object_in_6["Location"]
        # message6['UUID'] = json_object_in_6["UUID"]
        # message6['Inference'] = json_object_in_6["Inference"]
        
        
        # message7 = {}
        # #message['message'] = args.message
        # message7['sequence'] = loopCount
        # message7['Alias'] = "/pumpingstation/007"
        # message7['Location'] = json_object_in_7["Location"]
        # message7['UUID'] = json_object_in_7["UUID"]
        # message7['Inference'] = json_object_in_7["Inference"]
      
        
        # message8 = {}
        # #message['message'] = args.message
        # message8['sequence'] = loopCount
        # message8['Alias'] = "/pumpingstation/008"
        # message8['Location'] = json_object_in_8["Location"]
        # message8['UUID'] = json_object_in_8["UUID"]
        # message8['Inference'] = json_object_in_8["Inference"]
        
        
        # message9 = {}
        # #message['message'] = args.message
        # message9['sequence'] = loopCount
        # message9['Alias'] = "/pumpingstation/009"
        # message9['Location'] = json_object_in_9["Location"]
        # message9['UUID'] = json_object_in_9["UUID"]
        # message9['Inference'] = json_object_in_9["Inference"]
        
        
        # message10 = {}
        # #message['message'] = args.message
        # message10['sequence'] = loopCount
        # message10['Alias'] = "/pumpingstation/010"
        # message10['Location'] = json_object_in_10["Location"]
        # message10['UUID'] = json_object_in_10["UUID"]
        # message10['Inference'] = json_object_in_10["Inference"]
        
        
        
        messageJson1 = json.dumps(message1)
        messageJson2 = json.dumps(message2)
        messageJson3 = json.dumps(message3)
        #messageJson4 = json.dumps(message4)
        #messageJson5 = json.dumps(message5)
        # messageJson6 = json.dumps(message6)
        # messageJson7 = json.dumps(message7)
        # messageJson8 = json.dumps(message8)
        # messageJson9 = json.dumps(message9)
        # messageJson10 = json.dumps(message5)
        
        myAWSIoTMQTTClient.publish(topic1, messageJson1, 1)
        myAWSIoTMQTTClient.publish(topic2, messageJson2, 1)
        myAWSIoTMQTTClient.publish(topic3, messageJson3, 1)
        #myAWSIoTMQTTClient.publish(topic4, messageJson4, 1)
        #myAWSIoTMQTTClient.publish(topic5, messageJson5, 1)
        # myAWSIoTMQTTClient.publish(topic6, messageJson6, 1)
        # myAWSIoTMQTTClient.publish(topic7, messageJson7, 1)
        # myAWSIoTMQTTClient.publish(topic8, messageJson8, 1)
        # myAWSIoTMQTTClient.publish(topic9, messageJson9, 1)
        # myAWSIoTMQTTClient.publish(topic10, messageJson10, 1)
     
        if args.mode == 'publish':
            print('Published topic %s: %s\n' % (topic1, messageJson1))
        else:
            
        loopCount += 1
    time.sleep(5)
