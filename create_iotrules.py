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




#This python script runs AWS CLI commands and relies on the permissions on your AWS CLoud9 instance
#Create IoT rules from Iot Core to Sitewise. json object reference for rules have been pre defined in /iot_rules

import time
import json
from collections import namedtuple
import os
import subprocess as sp
import argparse

#Define path 
path = os.path.abspath( os.path.dirname( __file__ ) )
print(path)

#Gets arguments 
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--roleArn", action="store", required=True, dest="roleArn")

args = parser.parse_args()
roleArn = f"{args.roleArn}"



#Function for iot_core rule creation
def CreateIoTRuleJSON(path, station_number, role_arn): #Inputs path and how many rules you like to create 
    
     
    n = station_number
    rule_out = {
          "sql": f"SELECT * FROM '/pumpingstation/{n}'",
          "description": f"Sends data to sitewise pumpingstation{n}",
          "ruleDisabled": False,
          "awsIotSqlVersion": "2016-03-23",
          "actions": [
            {
              "iotSiteWise": {
                "putAssetPropertyValueEntries":[
                                {
                                    "propertyValues": [
                                        {
                                            "timestamp": {
                                                "timeInSeconds": "${floor(timestamp() / 1E3)}", 
                                                "offsetInNanos": "0"
                                            }, 
                                            "value": {
                                                "integerValue": "${get(*, \"Pressure\")}"
                                            }
                                        }
                                    ], 
                                    "propertyAlias": f"/pumpingstation/{n}/Pressure"
                                }, 
                                {
                                    "propertyValues": [
                                        {
                                            "timestamp": {
                                                "timeInSeconds": "${floor(timestamp() / 1E3)}", 
                                                "offsetInNanos": "0"
                                            }, 
                                            "value": {
                                                "integerValue": "${get(*, \"Vibration\")}"
                                            }
                                        }
                                    ], 
                                    "propertyAlias": f"/pumpingstation/{n}/Vibration"
                                }, 
                                {
                                    "propertyValues": [
                                        {
                                            "timestamp": {
                                                "timeInSeconds": "${floor(timestamp() / 1E3)}", 
                                                "offsetInNanos": "0"
                                            }, 
                                            "value": {
                                                "integerValue": "${get(*, \"Flow\")}"
                                            }
                                        }
                                    ], 
                                    "propertyAlias": f"/pumpingstation/{n}/Flow"
                                }, 
                                {
                                    "propertyValues": [
                                        {
                                            "timestamp": {
                                                "timeInSeconds": "${floor(timestamp() / 1E3)}", 
                                                "offsetInNanos": "0"
                                            }, 
                                            "value": {
                                                "integerValue": "${get(*, \"Amperage\")}"
                                            }
                                        }
                                    ], 
                                    "propertyAlias": f"/pumpingstation/{n}/Amperage"
                                }, 
                                {
                                    "propertyValues": [
                                        {
                                            "timestamp": {
                                                "timeInSeconds": "${floor(timestamp() / 1E3)}", 
                                                "offsetInNanos": "0"
                                            }, 
                                            "value": {
                                                "integerValue": "${get(*, \"Voltage\")}"
                                            }
                                        }
                                    ], 
                                    "propertyAlias": f"/pumpingstation/{n}/Voltage"
                                }, 
                                {
                                    "propertyValues": [
                                        {
                                            "timestamp": {
                                                "timeInSeconds": "${floor(timestamp() / 1E3)}", 
                                                "offsetInNanos": "0"
                                            }, 
                                            "value": {
                                                "integerValue": "${get(*, \"Temperature\")}"
                                            }
                                        }
                                    ], 
                                    "propertyAlias": f"/pumpingstation/{n}/Temperature"
                                }, 
                                {
                                    "propertyValues": [
                                        {
                                            "timestamp": {
                                                "timeInSeconds": "${floor(timestamp() / 1E3)}", 
                                                "offsetInNanos": "0"
                                            }, 
                                            "value": {
                                                "booleanValue": "${get(*, \"Fan\")}"
                                            }
                                        }
                                    ], 
                                    "propertyAlias": f"/pumpingstation/{n}/Fan"
                                }, 
                                {
                                    "propertyValues": [
                                        {
                                            "timestamp": {
                                                "timeInSeconds": "${floor(timestamp() / 1E3)}", 
                                                "offsetInNanos": "0"
                                            }, 
                                            "value": {
                                                "integerValue": "${get(*, \"rpm\")}"
                                            }
                                        }
                                    ], 
                                    "propertyAlias": f"/pumpingstation/{n}/rpm"
                                }, 
                                {
                                    "propertyValues": [
                                        {
                                            "timestamp": {
                                                "timeInSeconds": "${floor(timestamp() / 1E3)}", 
                                                "offsetInNanos": "0"
                                            }, 
                                            "value": {
                                                "integerValue": "${get(*, \"Humidity\")}"
                                            }
                                        }
                                    ], 
                                    "propertyAlias": f"/pumpingstation/{n}/Humidity"
                                }, 
                                {
                                    "propertyValues": [
                                        {
                                            "timestamp": {
                                                "timeInSeconds": "${floor(timestamp() / 1E3)}", 
                                                "offsetInNanos": "0"
                                            }, 
                                            "value": {
                                                "stringValue": "${get(*, \"Location\")}"
                                            }
                                        }
                                    ], 
                                    "propertyAlias": f"/pumpingstation/{n}/Location"
                                }
                            ],
                "roleArn": f"{role_arn}" 
              }
            }
          ]
        }   
            
        
      
    
    
    #Create profile
    json_load = json.dumps(rule_out)
    with open(f"{path}/iot_rules/iotcore_to_sitewise_rule_pumpingstation{n}.json", 'w') as outfile:
        json.dump(rule_out, outfile)
    
      
    #Checks if a JSON rule profile already exists
    profile_exists = os.path.exists(f"{path}/iot_rules/iotcore_to_sitewise_rule_pumpingstation{n}.json")
    
    if profile_exists:
        cmd = f"aws iot create-topic-rule --rule-name pumpingstation{n} --topic-rule-payload file://{path}/iot_rules/iotcore_to_sitewise_rule_pumpingstation{n}.json"
        create_rule = sp.getoutput(cmd)
        
        print(cmd)
        print(create_rule)
   
        

        
     
for n in range(1, 11):
    CreateIoTRuleJSON(path, n, roleArn)
    
print ("Script finished gracefully !!!")
      
