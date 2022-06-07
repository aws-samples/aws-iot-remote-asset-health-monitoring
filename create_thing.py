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
#Create IoT thing for simulation and define thing policy, create and dowload certs 

import json
from collections import namedtuple
import os
import subprocess as sp

#Define path 
path = os.path.abspath( os.path.dirname( __file__ ) )
print(path)
#Gets role arn 

#defines iot thing creation command
def CreateThing():
     create_thing_json = sp.getoutput("aws iot create-thing --thing-name all_pumping_stations")
     create_thing = json.loads(create_thing_json)
     print(create_thing)
     thing_id = create_thing["thingName"]
     return(thing_id)
     
#defines policy creation function and command    
def CreatePolicy():

    cli_cmd = f'aws iot create-policy --policy-name "pumping_station_simulation" --policy-document file://thing_policy.json'
    print(cli_cmd)
    create_policy_json = sp.getoutput(cli_cmd)
    print(create_policy_json)
    create_policy = json.loads(create_policy_json)
    print(create_policy)
    policy_name = create_policy["policyName"]
    return(policy_name)

#defines certificates and keys creation command 
def CreateCertKeys():
    create_cert_key_json = sp.getoutput('aws iot create-keys-and-certificate \
    --certificate-pem-outfile "all_pumping_stations.cert.pem" \
    --public-key-outfile "all_pumping_stations.public.key" \
    --private-key-outfile "all_pumping_stations.private.key" \
    --set-as-active')
    print(create_cert_key_json)
    create_cert_key = json.loads(create_cert_key_json)  
    return (create_cert_key["certificateArn"])

#attach policy to certificate
def Attachpolicy(policy_name, target):
    cli_cmd = sp.getoutput(f'aws iot attach-policy \
    --policy-name "{policy_name}"\
    --target "{target}"')
    print(cli_cmd)

    
#attach cert to thing 
def AttachCert(principal, thing_name):
    cli_cmd = sp.getoutput(f'aws iot attach-thing-principal \
    --thing-name "{thing_name}"\
    --principal "{principal}"')
    print(cli_cmd)

#get root CA
def GetRootCa():
    shell_cmd = sp.getoutput("curl -o root-CA.crt https://www.amazontrust.com/repository/AmazonRootCA1.pem")
    print(shell_cmd)
    
    
    
GetRootCa()    
thing_name = CreateThing()
policy_name = CreatePolicy()
principal = CreateCertKeys()
Attachpolicy(policy_name, principal)
AttachCert(principal, thing_name)