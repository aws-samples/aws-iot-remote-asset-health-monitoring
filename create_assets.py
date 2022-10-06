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

#Get Model ID from JSON file
with open(f"{path}/asset_models/model_assets_id_list.json", 'r') as openfile:
            object_in = json.load(openfile)

#the object_in format - {
                        #     "pumpmodelid": pump_model,
                        #     "pumpingstationmodelid": pumping_station_model,
                        #     "pumpingstationlocationmodel": pumping_station_location_model
                        # }

pump_model_id = object_in["pumpmodelid"]
pumpingstation_model_id = object_in["pumpingstationmodelid"] 
pumpingstationlocation_model_id = object_in["pumpingstationlocationmodel"]

print (f"cached id's {pump_model_id}, {pumpingstation_model_id}, {pumpingstationlocation_model_id}")

#create parent assets
print("Creating parent assets")

def CreateParentAssets(location_id, pumping_station_id, n, state):
    
    #copy hierarchy ID
    location_getHierarchy = sp.getoutput(f"aws iotsitewise describe-asset-model \
        --asset-model-id {location_id}")
        
    print (location_getHierarchy)
    location_getHierarchy_json = json.loads(location_getHierarchy) 
    location_hierarchy_id = location_getHierarchy_json["assetModelHierarchies"][0]["id"]
    print(location_hierarchy_id)
    
    pumping_getHierarchy = sp.getoutput(f"aws iotsitewise describe-asset-model \
        --asset-model-id {pumping_station_id}")
        
    print (pumping_getHierarchy)
    pumping_getHierarchy_json = json.loads(pumping_getHierarchy) 
    pumping_hierarchy_id = pumping_getHierarchy_json["assetModelHierarchies"][0]["id"]
    print(pumping_hierarchy_id)
        

    create_asset_location_json = sp.getoutput(f"aws iotsitewise create-asset \
        --asset-name {state} \
        --asset-model-id {location_id}")
        
    print (create_asset_location_json)

    print (f"Location {state} created")
    create_asset_location = json.loads(create_asset_location_json) 
    asset_location_id = create_asset_location["assetId"]
    print(f"Asset id is {asset_location_id}")
    time.sleep(5)
    print("waiting for asset propagation")
    
    create_asset_json = sp.getoutput(f"aws iotsitewise create-asset \
        --asset-name pumpingstation{n} \
        --asset-model-id {pumping_station_id}")
        
    print (create_asset_json)

    print (f"pumpingstation{n} created")
    create_asset = json.loads(create_asset_json) 
    pumping_asset_id = create_asset["assetId"]
    print(f"Asset id is {pumping_asset_id}")
    time.sleep(5)
    print("waiting for asset propagation")
    
    create_asset_association = sp.getoutput(f"aws iotsitewise associate-assets \
        --asset-id {asset_location_id} \
        --hierarchy-id {location_hierarchy_id} \
        --child-asset-id {pumping_asset_id}")
    
    id_list = [pumping_asset_id, pumping_hierarchy_id]
    return (id_list)

pumpingStation1_ID = CreateParentAssets(pumpingstationlocation_model_id, pumpingstation_model_id, 1, "NY" )
pumpingStation2_ID = CreateParentAssets(pumpingstationlocation_model_id, pumpingstation_model_id, 2, "CA" )
pumpingStation3_ID = CreateParentAssets(pumpingstationlocation_model_id, pumpingstation_model_id, 3, "WA" )
pumpingStation4_ID = CreateParentAssets(pumpingstationlocation_model_id, pumpingstation_model_id, 4, "NM" )
pumpingStation5_ID = CreateParentAssets(pumpingstationlocation_model_id, pumpingstation_model_id, 5, "FL" )



#Function to create assets from asset model (TODO add a check, if asset already exit skip creation and list asset instead)
def CreateAssetPumpA(asset_model_id, n):#The ID must be provided and "n" for pumpingstation number
    create_asset_json = sp.getoutput(f"aws iotsitewise create-asset \
    --asset-name pumpingstation{n}_pumpA \
    --asset-model-id {asset_model_id}")
   
    print (create_asset_json)
 
    print (f"pumpingstation{n}_pumpA created")
    create_asset = json.loads(create_asset_json) 
    asset_id = create_asset["assetId"]
    print(f"Asset id is {asset_id}")
    return asset_id

def CreateAssetPumpB(asset_model_id, n):#The ID must be provided and "n" for pumpingstation number
    create_asset_json = sp.getoutput(f"aws iotsitewise create-asset \
    --asset-name pumpingstation{n}_pumpB \
    --asset-model-id {asset_model_id}")
   
    print (create_asset_json)
 
    print (f"pumpingstation{n}_pumpB created")
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
def AssociateTimeStreamsPumpA(property_id_info_list, asset_id, number_of_messuraments, station_number):#This function will not associate streams to atributes (TODO: add argument to check if all aliases were sucesefull added and return a log)
    #loop starts from 3,0
    for x in range(0,number_of_messuraments): 
        item_alias= property_id_info_list[x][0]
        property_id = property_id_info_list[x][1]
        alias = f"/pumpingstation/{station_number}/pumpA/{item_alias}"
        #assoicate the timestream to asset
        associate_timestreams = sp.getoutput(f"aws iotsitewise associate-time-series-to-asset-property  \
        --alias {alias} \
        --asset-id {asset_id} \
        --property-id {property_id}")
        print (f"{alias} associated to Asset = {asset_id} Property {property_id}")
        time.sleep(1)# itentional delay to allow api to flow the data into the asset (TODO implemente property x stream check before removing this line 77)
                                            
def AssociateTimeStreamsPumpB(property_id_info_list, asset_id, number_of_messuraments, station_number):#This function will not associate streams to atributes (TODO: add argument to check if all aliases were sucesefull added and return a log)
    #loop starts from 3,0
    for x in range(0,number_of_messuraments): 
        item_alias= property_id_info_list[x][0]
        property_id = property_id_info_list[x][1]
        alias = f"/pumpingstation/{station_number}/pumpB/{item_alias}"
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




number_of_messuraments = 9 #(TODO: automate that to grab number from asset model desciption)
number_of_attributes = 0 #(TODO: automate that to grab number from asset model desciption)
asset_model_id = pump_model_id

#sequence FOR PUMP A pumpingstation1
pumpingStation1_pumpA_ID = CreateAssetPumpA(asset_model_id, 1)
time.sleep(1)#some delay to allow the asset creation 

#creates JSON object for asset ID info and appends data 
print (f"Requesting info of {pumpingStation1_pumpA_ID}")
#will try 5 times
tries = 0
while True:
    status = GetAssetStatus(pumpingStation1_pumpA_ID)
    if tries == 5:
        print(f"Asset {pumpingStation1_pumpA_ID} is not failed to become Active, check logs")
        break
    elif status != "ACTIVE":
        tries = tries+1
        print(f"Asset {pump_model_id} is not Active trying again")
        time.sleep(2)
    elif status == "ACTIVE":
        print (f"Asset {pumpingStation1_pumpA_ID} is Active, Association in progress")
        break
print (f"Getting Properties info for {pumpingStation1_pumpA_ID}")    
property_id_info_list = ReadPropertyID(pumpingStation1_pumpA_ID, number_of_attributes, number_of_messuraments)# The asset model for the pumping station has 13 items. 3 atributes and 10 messurements
time.sleep(1)#some delay to allow the operation
print (property_id_info_list)
AssociateTimeStreamsPumpA(property_id_info_list, pumpingStation1_pumpA_ID, number_of_messuraments, 1)
print (f"Pumping Station Number 1 is ready" )

P1_PA_asset_association = sp.getoutput(f"aws iotsitewise associate-assets \
        --asset-id {pumpingStation1_ID[0]} \
        --hierarchy-id {pumpingStation1_ID[1]} \
        --child-asset-id {pumpingStation1_pumpA_ID}")
print(P1_PA_asset_association)    
    


#sequence FOR PUMP A pumpingstation2
pumpingStation2_pumpA_ID = CreateAssetPumpA(asset_model_id, 2)
time.sleep(1)#some delay to allow the asset creation 

#creates JSON object for asset ID info and appends data 
print (f"Requesting info of {pumpingStation2_pumpA_ID}")
#will try 5 times
tries = 0
while True:
    status = GetAssetStatus(pumpingStation2_pumpA_ID)
    if tries == 5:
        print(f"Asset {pumpingStation2_pumpA_ID} is not failed to become Active, check logs")
        break
    elif status != "ACTIVE":
        tries = tries+1
        print(f"Asset {pump_model_id} is not Active trying again")
        time.sleep(2)
    elif status == "ACTIVE":
        print (f"Asset {pumpingStation2_pumpA_ID} is Active, Association in progress")
        break
print (f"Getting Properties info for {pumpingStation2_pumpA_ID}")    
property_id_info_list = ReadPropertyID(pumpingStation2_pumpA_ID, number_of_attributes, number_of_messuraments)# The asset model for the pumping station has 13 items. 3 atributes and 10 messurements
time.sleep(1)#some delay to allow the operation
print (property_id_info_list)
AssociateTimeStreamsPumpA(property_id_info_list, pumpingStation2_pumpA_ID, number_of_messuraments, 2)
print (f"Pumping Station Number 2 is ready" )

P2_PA_asset_association = sp.getoutput(f"aws iotsitewise associate-assets \
        --asset-id {pumpingStation2_ID[0]} \
        --hierarchy-id {pumpingStation2_ID[1]} \
        --child-asset-id {pumpingStation2_pumpA_ID}")
print(P2_PA_asset_association)    
    

#sequence FOR PUMP A pumpingstation3
pumpingStation3_pumpA_ID = CreateAssetPumpA(asset_model_id, 3)
time.sleep(1)#some delay to allow the asset creation 

#creates JSON object for asset ID info and appends data 
print (f"Requesting info of {pumpingStation3_pumpA_ID}")
#will try 5 times
tries = 0
while True:
    status = GetAssetStatus(pumpingStation3_pumpA_ID)
    if tries == 5:
        print(f"Asset {pumpingStation3_pumpA_ID} is not failed to become Active, check logs")
        break
    elif status != "ACTIVE":
        tries = tries+1
        print(f"Asset {pump_model_id} is not Active trying again")
        time.sleep(2)
    elif status == "ACTIVE":
        print (f"Asset {pumpingStation3_pumpA_ID} is Active, Association in progress")
        break
print (f"Getting Properties info for {pumpingStation3_pumpA_ID}")    
property_id_info_list = ReadPropertyID(pumpingStation3_pumpA_ID, number_of_attributes, number_of_messuraments)# The asset model for the pumping station has 13 items. 3 atributes and 10 messurements
time.sleep(1)#some delay to allow the operation
print (property_id_info_list)
AssociateTimeStreamsPumpA(property_id_info_list, pumpingStation3_pumpA_ID, number_of_messuraments, 3)
print (f"Pumping Station Number 3 is ready" )

P3_PA_asset_association = sp.getoutput(f"aws iotsitewise associate-assets \
        --asset-id {pumpingStation3_ID[0]} \
        --hierarchy-id {pumpingStation3_ID[1]} \
        --child-asset-id {pumpingStation3_pumpA_ID}")
print(P3_PA_asset_association) 



#sequence FOR PUMP A pumpingstation4
pumpingStation4_pumpA_ID = CreateAssetPumpA(asset_model_id, 4)
time.sleep(1)#some delay to allow the asset creation 

#creates JSON object for asset ID info and appends data 
print (f"Requesting info of {pumpingStation4_pumpA_ID}")
#will try 5 times
tries = 0
while True:
    status = GetAssetStatus(pumpingStation4_pumpA_ID)
    if tries == 5:
        print(f"Asset {pumpingStation4_pumpA_ID} is not failed to become Active, check logs")
        break
    elif status != "ACTIVE":
        tries = tries+1
        print(f"Asset {pump_model_id} is not Active trying again")
        time.sleep(2)
    elif status == "ACTIVE":
        print (f"Asset {pumpingStation4_pumpA_ID} is Active, Association in progress")
        break
print (f"Getting Properties info for {pumpingStation4_pumpA_ID}")    
property_id_info_list = ReadPropertyID(pumpingStation4_pumpA_ID, number_of_attributes, number_of_messuraments)# The asset model for the pumping station has 13 items. 3 atributes and 10 messurements
time.sleep(1)#some delay to allow the operation
print (property_id_info_list)
AssociateTimeStreamsPumpA(property_id_info_list, pumpingStation4_pumpA_ID, number_of_messuraments, 4)
print (f"Pumping Station Number 4 is ready" )

P4_PA_asset_association = sp.getoutput(f"aws iotsitewise associate-assets \
        --asset-id {pumpingStation4_ID[0]} \
        --hierarchy-id {pumpingStation4_ID[1]} \
        --child-asset-id {pumpingStation4_pumpA_ID}")
print(P4_PA_asset_association) 



#sequence FOR PUMP A pumpingstation5
pumpingStation5_pumpA_ID = CreateAssetPumpA(asset_model_id, 5)
time.sleep(1)#some delay to allow the asset creation 

#creates JSON object for asset ID info and appends data 
print (f"Requesting info of {pumpingStation5_pumpA_ID}")
#will try 5 times
tries = 0
while True:
    status = GetAssetStatus(pumpingStation5_pumpA_ID)
    if tries == 5:
        print(f"Asset {pumpingStation5_pumpA_ID} is not failed to become Active, check logs")
        break
    elif status != "ACTIVE":
        tries = tries+1
        print(f"Asset {pump_model_id} is not Active trying again")
        time.sleep(2)
    elif status == "ACTIVE":
        print (f"Asset {pumpingStation5_pumpA_ID} is Active, Association in progress")
        break
print (f"Getting Properties info for {pumpingStation5_pumpA_ID}")    
property_id_info_list = ReadPropertyID(pumpingStation5_pumpA_ID, number_of_attributes, number_of_messuraments)# The asset model for the pumping station has 13 items. 3 atributes and 10 messurements
time.sleep(1)#some delay to allow the operation
print (property_id_info_list)
AssociateTimeStreamsPumpA(property_id_info_list, pumpingStation5_pumpA_ID, number_of_messuraments, 5)
print (f"Pumping Station Number 5 is ready" )

P5_PA_asset_association = sp.getoutput(f"aws iotsitewise associate-assets \
        --asset-id {pumpingStation5_ID[0]} \
        --hierarchy-id {pumpingStation5_ID[1]} \
        --child-asset-id {pumpingStation5_pumpA_ID}")
print(P5_PA_asset_association) 



#sequence FOR PUMP B pumpingstation1
pumpingStation1_pumpB_ID = CreateAssetPumpB(asset_model_id, 1)
time.sleep(1)#some delay to allow the asset creation 

#creates JSON object for asset ID info and appends data 
print (f"Requesting info of {pumpingStation1_pumpB_ID}")
#will try 5 times
tries = 0
while True:
    status = GetAssetStatus(pumpingStation1_pumpB_ID)
    if tries == 5:
        print(f"Asset {pumpingStation1_pumpB_ID} is not failed to become Active, check logs")
        break
    elif status != "ACTIVE":
        tries = tries+1
        print(f"Asset {pump_model_id} is not Active trying again")
        time.sleep(2)
    elif status == "ACTIVE":
        print (f"Asset {pumpingStation1_pumpB_ID} is Active, Association in progress")
        break
print (f"Getting Properties info for {pumpingStation1_pumpB_ID}")    
property_id_info_list = ReadPropertyID(pumpingStation1_pumpB_ID, number_of_attributes, number_of_messuraments)# The asset model for the pumping station has 13 items. 3 atributes and 10 messurements
time.sleep(1)#some delay to allow the operation
print (property_id_info_list)
AssociateTimeStreamsPumpB(property_id_info_list, pumpingStation1_pumpB_ID, number_of_messuraments, 1)
print (f"Pumping Station Number 1 is ready" )

P1_PB_asset_association = sp.getoutput(f"aws iotsitewise associate-assets \
        --asset-id {pumpingStation1_ID[0]} \
        --hierarchy-id {pumpingStation1_ID[1]} \
        --child-asset-id {pumpingStation1_pumpB_ID}")
print(P1_PB_asset_association)    
    


#sequence FOR PUMP B pumpingstation2
pumpingStation2_pumpB_ID = CreateAssetPumpB(asset_model_id, 2)
time.sleep(1)#some delay to allow the asset creation 

#creates JSON object for asset ID info and appends data 
print (f"Requesting info of {pumpingStation2_pumpB_ID}")
#will try 5 times
tries = 0
while True:
    status = GetAssetStatus(pumpingStation2_pumpB_ID)
    if tries == 5:
        print(f"Asset {pumpingStation2_pumpB_ID} is not failed to become Active, check logs")
        break
    elif status != "ACTIVE":
        tries = tries+1
        print(f"Asset {pump_model_id} is not Active trying again")
        time.sleep(2)
    elif status == "ACTIVE":
        print (f"Asset {pumpingStation2_pumpB_ID} is Active, Association in progress")
        break
print (f"Getting Properties info for {pumpingStation2_pumpB_ID}")    
property_id_info_list = ReadPropertyID(pumpingStation2_pumpB_ID, number_of_attributes, number_of_messuraments)# The asset model for the pumping station has 13 items. 3 atributes and 10 messurements
time.sleep(1)#some delay to allow the operation
print (property_id_info_list)
AssociateTimeStreamsPumpB(property_id_info_list, pumpingStation2_pumpB_ID, number_of_messuraments, 2)
print (f"Pumping Station Number 2 is ready" )

P2_PB_asset_association = sp.getoutput(f"aws iotsitewise associate-assets \
        --asset-id {pumpingStation2_ID[0]} \
        --hierarchy-id {pumpingStation2_ID[1]} \
        --child-asset-id {pumpingStation2_pumpB_ID}")
print(P2_PB_asset_association)    
    

#sequence FOR PUMP B pumpingstation3
pumpingStation3_pumpB_ID = CreateAssetPumpB(asset_model_id, 3)
time.sleep(1)#some delay to allow the asset creation 

#creates JSON object for asset ID info and appends data 
print (f"Requesting info of {pumpingStation3_pumpB_ID}")
#will try 5 times
tries = 0
while True:
    status = GetAssetStatus(pumpingStation3_pumpB_ID)
    if tries == 5:
        print(f"Asset {pumpingStation3_pumpB_ID} is not failed to become Active, check logs")
        break
    elif status != "ACTIVE":
        tries = tries+1
        print(f"Asset {pump_model_id} is not Active trying again")
        time.sleep(2)
    elif status == "ACTIVE":
        print (f"Asset {pumpingStation3_pumpB_ID} is Active, Association in progress")
        break
print (f"Getting Properties info for {pumpingStation3_pumpB_ID}")    
property_id_info_list = ReadPropertyID(pumpingStation3_pumpB_ID, number_of_attributes, number_of_messuraments)# The asset model for the pumping station has 13 items. 3 atributes and 10 messurements
time.sleep(1)#some delay to allow the operation
print (property_id_info_list)
AssociateTimeStreamsPumpB(property_id_info_list, pumpingStation3_pumpB_ID, number_of_messuraments, 3)
print (f"Pumping Station Number 3 is ready" )

P3_PB_asset_association = sp.getoutput(f"aws iotsitewise associate-assets \
        --asset-id {pumpingStation3_ID[0]} \
        --hierarchy-id {pumpingStation3_ID[1]} \
        --child-asset-id {pumpingStation3_pumpB_ID}")
print(P3_PB_asset_association) 



#sequence FOR PUMP B pumpingstation4
pumpingStation4_pumpB_ID = CreateAssetPumpB(asset_model_id, 4)
time.sleep(1)#some delay to allow the asset creation 

#creates JSON object for asset ID info and appends data 
print (f"Requesting info of {pumpingStation4_pumpB_ID}")
#will try 5 times
tries = 0
while True:
    status = GetAssetStatus(pumpingStation4_pumpB_ID)
    if tries == 5:
        print(f"Asset {pumpingStation4_pumpB_ID} is not failed to become Active, check logs")
        break
    elif status != "ACTIVE":
        tries = tries+1
        print(f"Asset {pump_model_id} is not Active trying again")
        time.sleep(2)
    elif status == "ACTIVE":
        print (f"Asset {pumpingStation4_pumpB_ID} is Active, Association in progress")
        break
print (f"Getting Properties info for {pumpingStation4_pumpB_ID}")    
property_id_info_list = ReadPropertyID(pumpingStation4_pumpB_ID, number_of_attributes, number_of_messuraments)# The asset model for the pumping station has 13 items. 3 atributes and 10 messurements
time.sleep(1)#some delay to allow the operation
print (property_id_info_list)
AssociateTimeStreamsPumpB(property_id_info_list, pumpingStation4_pumpB_ID, number_of_messuraments, 4)
print (f"Pumping Station Number 4 is ready" )

P4_PB_asset_association = sp.getoutput(f"aws iotsitewise associate-assets \
        --asset-id {pumpingStation4_ID[0]} \
        --hierarchy-id {pumpingStation4_ID[1]} \
        --child-asset-id {pumpingStation4_pumpB_ID}")
print(P4_PB_asset_association) 



#sequence FOR PUMP B pumpingstation5
pumpingStation5_pumpB_ID = CreateAssetPumpB(asset_model_id, 5)
time.sleep(1)#some delay to allow the asset creation 

#creates JSON object for asset ID info and appends data 
print (f"Requesting info of {pumpingStation5_pumpB_ID}")
#will try 5 times
tries = 0
while True:
    status = GetAssetStatus(pumpingStation5_pumpB_ID)
    if tries == 5:
        print(f"Asset {pumpingStation5_pumpB_ID} is not failed to become Active, check logs")
        break
    elif status != "ACTIVE":
        tries = tries+1
        print(f"Asset {pump_model_id} is not Active trying again")
        time.sleep(2)
    elif status == "ACTIVE":
        print (f"Asset {pumpingStation5_pumpB_ID} is Active, Association in progress")
        break
print (f"Getting Properties info for {pumpingStation5_pumpB_ID}")    
property_id_info_list = ReadPropertyID(pumpingStation5_pumpB_ID, number_of_attributes, number_of_messuraments)# The asset model for the pumping station has 13 items. 3 atributes and 10 messurements
time.sleep(1)#some delay to allow the operation
print (property_id_info_list)
AssociateTimeStreamsPumpB(property_id_info_list, pumpingStation5_pumpB_ID, number_of_messuraments, 5)
print (f"Pumping Station Number 5 is ready" )

P5_PB_asset_association = sp.getoutput(f"aws iotsitewise associate-assets \
        --asset-id {pumpingStation5_ID[0]} \
        --hierarchy-id {pumpingStation5_ID[1]} \
        --child-asset-id {pumpingStation5_pumpB_ID}")
print(P5_PB_asset_association)




print ("All pumps have been created and the data streams have been associated")
    

