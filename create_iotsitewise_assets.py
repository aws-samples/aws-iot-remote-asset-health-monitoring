
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


#Gets arguments for model ID 
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--model-id", action="store", required=True, dest="model_id")

args = parser.parse_args()
asset_model_id = args.model_id

#Function to create assets from asset model (TODO add a check, if asset already exit skip creation and list asset instead)
def CreateAsset(asset_model_id, n):#The ID must be provided and "n" for pumpingstation number
    create_asset_json = sp.getoutput(f"aws iotsitewise create-asset \
    --asset-name pumpingstation{n} \
    --asset-model-id {asset_model_id}")
   
    print (create_asset_json)
 
    print (f"pumpingstation{n} created")
    create_asset = json.loads(create_asset_json) 
    asset_id = create_asset["assetId"]
    print(f"Asset id is {asset_id}")
    return asset_id
    
#function to check Status of created asset 
def GetAssetStatus(asset_id):
    get_asset_properties_json = sp.getoutput(f"aws iotsitewise describe-asset \
    --asset-id {asset_id}")
    get_asset_properties = json.loads(get_asset_properties_json) 
    status = get_asset_properties["assetStatus"]["state"]
    print (f"Asset status is {status}")
    return (status)
    
#function to inspec created asset and read property IDs 
def ReadPropertyID(asset_id, number_of_attributes, number_of_messuraments):
    get_asset_properties_json = sp.getoutput(f"aws iotsitewise describe-asset \
    --asset-id {asset_id}")
    get_asset_properties = json.loads(get_asset_properties_json) 
    #nested function 
    def GetPropertiesInfo(get_asset_properties, number_of_attributes, number_of_messuraments):
        result = []
        status = ""
        for n in range(number_of_attributes, number_of_attributes+number_of_messuraments): #Offest of 3 to exclude the attributes
            property_id =  get_asset_properties["assetProperties"][n]["id"]
            name = get_asset_properties["assetProperties"][n]["name"]
            property_info = [name, property_id]
            result.append(property_info)
        return result    
    property_id_info_list = GetPropertiesInfo(get_asset_properties, number_of_attributes, number_of_messuraments)        
    return (property_id_info_list)
    
        
#function to associate timestrems to asset messurements
def AssociateTimeStreams(property_id_info_list, asset_id, number_of_messuraments, station_number):#This function will not associate streams to atributes (TODO: add argument to check if all aliases were sucesefull added and return a log)
    #loop starts from 3,0
    for x in range(0,number_of_messuraments): 
        item_alias= property_id_info_list[x][0]
        property_id = property_id_info_list[x][1]
        alias = f"/pumpingstation/{station_number}/{item_alias}"
        #assoicate the timestream to asset
        associate_timestreams = sp.getoutput(f"aws iotsitewise associate-time-series-to-asset-property  \
        --alias {alias} \
        --asset-id {asset_id} \
        --property-id {property_id}")
        print (f"{alias} associated to Asset = {asset_id} Property {property_id}")
        time.sleep(1)# itentional delay to allow api to flow the data into the asset (TODO implemente property x stream check before removing this line 77)
                                            

#this for loop defines how many rules and assets will be created
#note for this demostration we will be creating assests from 2-10 *(2-11 range) , as the pumping 1 will be manually created from the walkthrough
# Asset creation loop *note the loop will start from 2 due to walkthrough blog
for n in range(1, 11):
    station_number = n
    number_of_messuraments = 10 #(TODO: automate that to grab number from asset model desciption)
    number_of_attributes = 0 #(TODO: automate that to grab number from asset model desciption)
    
    asset_id = CreateAsset(asset_model_id, station_number)
    time.sleep(1)#some delay to allow the asset creation 
    print (f"Requesting info of {asset_id}")
    #will try 5 times
    tries = 0
    while True:
        status = GetAssetStatus(asset_id)
        if tries == 5:
            print(f"Asset {asset_id} is not failed to become Active, check logs")
            break
        elif status != "ACTIVE":
            tries = tries+1
            print(f"Asset {asset_id} is not Active trying again")
            time.sleep(2)
        elif status == "ACTIVE":
            print (f"Asset {asset_id} is Active, Association in progress")
            break
    print (f"Getting Properties info for {asset_id}")    
    property_id_info_list = ReadPropertyID(asset_id, number_of_attributes, number_of_messuraments)# The asset model for the pumping station has 13 items. 3 atributes and 10 messurements
    time.sleep(1)#some delay to allow the operation
    print (property_id_info_list)
    AssociateTimeStreams(property_id_info_list, asset_id, number_of_messuraments, station_number)
    print (f"Pumping Station Number {station_number} is ready" )
            
    
print ("The script finished gracefully congratulations !!!!")
    

