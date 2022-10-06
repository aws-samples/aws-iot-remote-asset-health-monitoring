#! /bin/bash

#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#the Software, and to permit persons to whom the Software is furnished to do so.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#Exit script when it encounters an error
set -e

#Install Python if it doesn't exist
if ! python3 --version | grep -i 'python'; then
  echo "Python doesn't exist. Starting installation process."
  yum install python37 #install Python 3.7
fi

#Install pip3 if it doesn't exist
if ! pip3 --version | grep -i 'pip'; then
  echo "pip3 package is not installed. Starting installation process."
  yum install python3-pip
fi

#Install boto3 if it doesn't exist
if ! pip3 list | grep -i 'boto3'; then
  echo "boto3 package is not installed. Starting installation process."
  pip3 install boto3
fi

#Install Python AWS IoT SDK if doesn't exist
if ! pip3 list | grep -i 'awsiotpythonsdk'; then
  echo "AWSIoTPythonSDK package is not installed. Starting installation process."
  pip3 install AWSIoTPythonSDK
fi

#Remove AWS CLI version 1 and install CLI version 2
yum -y remove awscli
cd /tmp
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -u awscliv2.zip
./aws/install

#Clear bash cache
hash aws

#Download and install grafana
GRAFANA_RPM=grafana-9.1.7-1.x86_64.rpm
wget https://dl.grafana.com/oss/release/${GRAFANA_RPM}
yum -y install $GRAFANA_RPM

#Create a port forwarding service
/sbin/iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 3000
/sbin/iptables-save > /etc/grafana-iptables.rules
cat <<EOF > /etc/systemd/system/grafana-prtfwd.service
[Unit]
Description = Port forwarding for Grafana
Before=network.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c "/sbin/iptables-restore < /etc/grafana-iptables.rules"

[Install]
WantedBy=multi-user.target
EOF

systemctl enable grafana-prtfwd.service
systemctl start grafana-prtfwd.service

#Install sitewise datasource plugin
mkdir /var/lib/grafana/plugins
SITEWISE_PLUGIN_VERSION=1.4.1
grafana-cli plugins install grafana-iot-sitewise-datasource $SITEWISE_PLUGIN_VERSION

#Create a SiteWise datasource - alternative
#cd /home/ec2-user/$GIT_REPO_NAME
#GRAFANA_CUSTOM=grafana-custom.tgz
#tar zxf $GRAFANA_CUSTOM -C /home/ec2-user/
#cd /home/ec2-user/grafana/
#sed -e "s/AWS_REGION/$REGION/g" datasources.json.in > datasources.json
#curl -X "POST" "http://localhost:3000/api/datasources" -H "Content-Type: application/json" --user "admin:$PASS" --data-binary @datasources.json

#Start grafana server and change default password

systemctl enable grafana-server.service
systemctl start grafana-server.service

PASS=grafana123
grafana-cli admin reset-admin-password $PASS