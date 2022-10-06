
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
import time
import json
from collections import namedtuple
import os
import subprocess as sp
import argparse

#Define path 
path = os.path.abspath( os.path.dirname( __file__ ) )
print(path)

#Function to create assets from asset model (TODO add a check, if asset already exit skip creation and list asset instead)
def CreatepumpModel():#The ID must be provided and "n" for pumpingstation number
    create_asset_json = sp.getoutput(f"aws iotsitewise create-asset-model \
    --cli-input-json file://{path}/asset_models/pump_model.json")
    model_info = json.loads(create_asset_json)
    assetModelId = model_info["assetModelId"]
   
    print (model_info)
    return (assetModelId)

def CreatepumpingStationModel(childAssetId):
    
    #Create Json file for input
    model_json = {
                    "assetModelName": "PumpingStation",
                    "assetModelDescription": "a model of a pumping station with 2 pumps ",
                    "assetModelProperties": [
                                                {
                                                    "name": "UUID",
                                                    "dataType": "STRING",
                                                    "type": {
                                                        "attribute": {
                                                            "defaultValue":"N/A"
                                                                     }
                                                            }
                                                }
                                                ],
                                                "assetModelHierarchies":[
                                                    {
                                                        "name": "Pump asset model",
                                                        "childAssetModelId": f"{childAssetId}"
                                                    }
                                                ]
                }
    
    
    with open(f"{path}/asset_models/pumpingstation_model.json", 'w') as outfile:
        json.dump(model_json, outfile, indent=4 )
    
    create_asset_json = sp.getoutput(f"aws iotsitewise create-asset-model \
    --cli-input-json file://{path}/asset_models/pumpingstation_model.json")
    model_info = json.loads(create_asset_json)
    assetModelId = model_info["assetModelId"]
   
    print (model_info)
    return (assetModelId)
    
    
def CreatepumpingStatioLocationModel(childAssetId):
    
    #Create Json file for input
    model_json = {
                    "assetModelName": "PumpingStationLocation",
                    "assetModelDescription": "Location of the pumpingStation - State ",
                    "assetModelProperties": [
                                                {
                                                    "name": "Location_State",
                                                    "dataType": "STRING",
                                                    "type": {
                                                        "attribute": {
                                                            "defaultValue":"N/A"
                                                                     }
                                                            }
                                                }
                                                ],
                                                "assetModelHierarchies":[
                                                    {
                                                        "name": "PumpingStation asset model",
                                                        "childAssetModelId": f"{childAssetId}"
                                                    }
                                                ]
                }
    
    
    with open(f"{path}/asset_models/pumpingstationlocation_model.json", 'w') as outfile:
        json.dump(model_json, outfile, indent=4 )
    
    create_asset_json = sp.getoutput(f"aws iotsitewise create-asset-model \
    --cli-input-json file://{path}/asset_models/pumpingstationlocation_model.json")
    model_info = json.loads(create_asset_json)
    assetModelId = model_info["assetModelId"]
   
    print (model_info)
    return (assetModelId) 

def CreateOrganizationModel(childAssetId):
    
    #Create Json file for input
    model_json = {
                    "assetModelName": "Organization",
                    "assetModelDescription": "The organization / company managing the assets ",
                    "assetModelProperties": [
                                                {
                                                    "name": "OrganizationID",
                                                    "dataType": "STRING",
                                                    "type": {
                                                        "attribute": {
                                                            "defaultValue":"123456789"
                                                                     }
                                                            }
                                                }
                                                ],
                                                "assetModelHierarchies":[
                                                    {
                                                        "name": "Location of assets ",
                                                        "childAssetModelId": f"{childAssetId}"
                                                    }
                                                ]
                }
    
    
    with open(f"{path}/asset_models/organization_model.json", 'w') as outfile:
        json.dump(model_json, outfile, indent=4 )
    
    create_asset_json = sp.getoutput(f"aws iotsitewise create-asset-model \
    --cli-input-json file://{path}/asset_models/organization_model.json")
    model_info = json.loads(create_asset_json)
    assetModelId = model_info["assetModelId"]
   
    print (model_info)
    return (assetModelId) 
 
pump_model = CreatepumpModel()
print ("waiting for resource propagation")
time.sleep(10)
pumping_station_model = CreatepumpingStationModel(pump_model)
print ("waiting for resource propagation")
time.sleep(10)
pumping_station_location_model = CreatepumpingStatioLocationModel(pumping_station_model)
print ("waiting for resource propagation")
time.sleep(10)
organization_model = CreateOrganizationModel(pumping_station_location_model)

model_assets_id_list = {
                            "pumpmodelid": pump_model,
                            "pumpingstationmodelid": pumping_station_model,
                            "pumpingstationlocationmodel": pumping_station_location_model,
                            "organizationmodelid": organization_model
                        }

with open(f"{path}/asset_models/model_assets_id_list.json", 'w') as outfile:
        json.dump(model_assets_id_list, outfile, indent=4 )