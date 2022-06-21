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







import requests
import time
import json
from collections import namedtuple
import os
import subprocess as sp
import argparse


#get Argument
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--workspace-id", action="store", required=True, dest="workspace_id",)
parser.add_argument("-r", "--model-id", action="store", required=True, dest="asset_model_id")
args = parser.parse_args()
workspace_id = args.workspace_id
asset_model_id = args.asset_model_id


#creates Grafana API KEy 
def GetGrafanaAPIKey(key_name, key_role, ttl, workspaces_id):
  cli_cmd = f'aws grafana create-workspace-api-key --key-name "{key_name}" --key-role "{key_role}" --seconds-to-live {ttl} --workspace-id "{workspaces_id}"'
  print(cli_cmd)
  create_key = sp.getoutput(cli_cmd)
  get_key = json.loads(create_key)
  print(get_key)
  return (get_key["key"])
  
  

#access the workspace info
def GetGrafanaWorkspaceInfo(workspace_id):
    get_workspace_info_json = sp.getoutput(f"aws grafana describe-workspace --workspace-id {workspace_id}")
    get_workspace_info = json.loads(get_workspace_info_json)
    workspace_id = workspace_id
    print(get_workspace_info)
    endpoint = get_workspace_info["workspace"]['endpoint']
    workspace_info = [workspace_id, endpoint]
    print("workspace found")
    print(workspace_info)
    return(workspace_info)
  

#function to list all assets 
def GetAssetsId(asset_model_id,):
  get_assets_id_json = sp.getoutput(f"aws iotsitewise list-assets --asset-model-id {asset_model_id}")
  get_assets_id = json.loads(get_assets_id_json)
  n = 10 # make this a external var that pulls from other code 
  result =[]
  
  for n in range(0,n):
    asset_name = get_assets_id["assetSummaries"][n]["id"]
    asset_id = get_assets_id["assetSummaries"][n]["name"] 
    assets_info = [asset_name, asset_id]  
    result.append(assets_info)
  print (result)    
  return (result)

#this fucntion has been modified for the grafana template creation 
def ReadPropertyID(assets_info, n, number_of_attributes, number_of_messuraments):
    asset_id = assets_info[n][0]
    asset_name = assets_info[n][1]
    get_asset_properties_json = sp.getoutput(f"aws iotsitewise describe-asset \
    --asset-id {asset_id}")
    get_asset_properties = json.loads(get_asset_properties_json) 
    #nested function buuilds list
    def GetPropertiesInfo(get_asset_properties, number_of_attributes, number_of_messuraments):
      result = []
      for n in range(number_of_attributes, number_of_attributes+number_of_messuraments): #Offest of 3 to exclude the attributes
          property_id =  get_asset_properties["assetProperties"][n]["id"]
          name = get_asset_properties["assetProperties"][n]["name"]
          property_info = [name, property_id]
          result.append(property_info)
      return result
    property_id_info_list = GetPropertiesInfo(get_asset_properties, number_of_attributes, number_of_messuraments)        
    return(property_id_info_list)
    

#pre-loop info
grafana_workspace_Info = GetGrafanaWorkspaceInfo(workspace_id)
grafana_workspace_ID = workspace_id

assets_info = GetAssetsId(asset_model_id)

#defines Grafana Access
API_KEY = GetGrafanaAPIKey("Admin", "ADMIN", 864000, grafana_workspace_ID)
server = grafana_workspace_Info[1]
url = f"https://{server}/api/dashboards/db"
headers = {
    "Authorization":f"Bearer {API_KEY}",
    "Content-Type":"application/json",
    "Accept": "application/json"
}
  
print(url)
print("running grafana dashboard formation")
print(f"list of assets {assets_info}")

for n in range(10):
  
  number_of_messuraments = 10
  number_of_attributes = 0
  
  property_list = ReadPropertyID(assets_info,n,number_of_attributes,number_of_messuraments)
  
  Model_ID = f"{asset_model_id}"
  Asset_ID = f"{assets_info[n][0]}"
  Asset_name = f"{assets_info[n][1]}"
  
  Temperature_ID = f"{property_list[0][1]}"
  Humidity_ID = f"{property_list[1][1]}"
  Pressure_ID = f"{property_list[2][1]}"
  Vibration_ID = f"{property_list[3][1]}"
  Flow_ID = f"{property_list[4][1]}"
  rpm_ID = f"{property_list[5][1]}"
  Voltage_ID = f"{property_list[6][1]}"
  Amperage_ID = f"{property_list[7][1]}"
  Fan_ID = f"{property_list[8][1]}"
  Location_ID = f"{property_list[9][1]}"
  
  
  
    
  Dashboard_name = f"{Asset_name}/Status/Time_series"
  Dashboard_uid = f"{Asset_name}"
  Alert_name = f"{Asset_name} Temperature Alert"
  #builds mega object json payload with the complete dashboard formation 
  print(f"Creating Grafana Dashboard for {Asset_name}") 
  
  dashboard_template = {
    "dashboard": {
        "annotations": {
      "list": [
        {
          "builtIn": 1,
          "datasource": "-- Grafana --",
          "enable": True,
          "hide": True,
          "iconColor": "rgba(0, 211, 255, 1)",
          "name": "Annotations & Alerts",
          "target": {
            "limit": 100,
            "matchAny": False,
            "tags": [],
            "type": "dashboard"
          },
          "type": "dashboard"
        }
      ]
    },
    "editable": True,
    "fiscalYearStartMonth": 0,
    "graphTooltip": 0,
    "id": 1,
    "links": [],
    "liveNow": False,
    "panels": [
      {
        "fieldConfig": {
          "defaults": {
            "mappings": [],
            "max": 120,
            "min": 0,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "orange",
                  "value": 60
                },
                {
                  "color": "red",
                  "value": 70
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 6,
          "w": 3,
          "x": 0,
          "y": 0
        },
        "id": 12,
        "options": {
          "orientation": "auto",
          "reduceOptions": {
            "calcs": [],
            "fields": "",
            "values": True
          },
          "showThresholdLabels": False,
          "showThresholdMarkers": True
        },
        "pluginVersion": "8.4.7",
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": Temperature_ID,
            "queryType": "PropertyValue",
            "refId": "A"
          }
        ],
        "title": "Temperature",
        "type": "gauge"
      },
      {
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "mappings": [],
            "max": 120,
            "min": 0,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "orange",
                  "value": 60
                },
                {
                  "color": "red",
                  "value": 70
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 6,
          "w": 2,
          "x": 3,
          "y": 0
        },
        "id": 13,
        "options": {
          "colorMode": "value",
          "graphMode": "area",
          "justifyMode": "auto",
          "orientation": "auto",
          "reduceOptions": {
            "calcs": [],
            "fields": "/^Fan$/",
            "values": True
          },
          "textMode": "value"
        },
        "pluginVersion": "8.4.7",
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": Fan_ID,
            "queryType": "PropertyValue",
            "refId": "A"
          }
        ],
        "title": "Fan operation",
        "type": "stat"
      },
      {
        "alert": {
          "alertRuleTags": {},
          "conditions": [
            {
              "evaluator": {
                "params": [
                  66
                ],
                "type": "gt"
              },
              "operator": {
                "type": "and"
              },
              "query": {
                "params": [
                  "A",
                  "10s",
                  "now"
                ]
              },
              "reducer": {
                "params": [],
                "type": "last"
              },
              "type": "query"
            }
          ],
          "executionErrorState": "alerting",
          "for": "1m",
          "frequency": "5s",
          "handler": 1,
          "name": f"Temperature alert {Asset_name}",
          "message": f"temperature on {Asset_name} is High the asset is unhealthy",
          "noDataState": "no_data",
          "notifications": []
        },
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            },
            "custom": {
              "axisLabel": "",
              "axisPlacement": "auto",
              "barAlignment": 0,
              "drawStyle": "line",
              "fillOpacity": 0,
              "gradientMode": "none",
              "hideFrom": {
                "legend": False,
                "tooltip": False,
                "viz": False
              },
              "lineInterpolation": "smooth",
              "lineStyle": {
                "fill": "solid"
              },
              "lineWidth": 1,
              "pointSize": 1,
              "scaleDistribution": {
                "type": "linear"
              },
              "showPoints": "auto",
              "spanNulls": False,
              "stacking": {
                "group": "A",
                "mode": "none"
              },
              "thresholdsStyle": {
                "mode": "off"
              }
            },
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 50
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 11,
          "w": 5,
          "x": 5,
          "y": 0
        },
        "id": 2,
        "options": {
          "legend": {
            "calcs": [],
            "displayMode": "list",
            "placement": "bottom"
          },
          "tooltip": {
            "mode": "single",
            "sort": "none"
          }
        },
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": Model_ID,
            "propertyId": Temperature_ID,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-east-1",
            "timeOrdering": "ASCENDING"
          }
        ],
        "thresholds": [
          {
            "colorMode": "critical",
            "op": "gt",
            "value": 66,
            "visible": True
          }
        ],
        "title": "Temperature",
        "type": "timeseries"
      },
      {
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            },
            "custom": {
              "axisLabel": "",
              "axisPlacement": "auto",
              "barAlignment": 0,
              "drawStyle": "line",
              "fillOpacity": 0,
              "gradientMode": "none",
              "hideFrom": {
                "legend": False,
                "tooltip": False,
                "viz": False
              },
              "lineInterpolation": "smooth",
              "lineStyle": {
                "fill": "solid"
              },
              "lineWidth": 1,
              "pointSize": 1,
              "scaleDistribution": {
                "type": "linear"
              },
              "showPoints": "auto",
              "spanNulls": False,
              "stacking": {
                "group": "A",
                "mode": "none"
              },
              "thresholdsStyle": {
                "mode": "off"
              }
            },
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 11,
          "w": 4,
          "x": 10,
          "y": 0
        },
        "id": 8,
        "options": {
          "legend": {
            "calcs": [],
            "displayMode": "list",
            "placement": "bottom"
          },
          "tooltip": {
            "mode": "single",
            "sort": "none"
          }
        },
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": Model_ID,
            "propertyId": Fan_ID,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-east-1",
            "timeOrdering": "ASCENDING"
          }
        ],
        "title": "Fan",
        "type": "timeseries"
      },
      {
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            },
            "custom": {
              "axisLabel": "",
              "axisPlacement": "auto",
              "barAlignment": 0,
              "drawStyle": "line",
              "fillOpacity": 0,
              "gradientMode": "none",
              "hideFrom": {
                "legend": False,
                "tooltip": False,
                "viz": False
              },
              "lineInterpolation": "smooth",
              "lineStyle": {
                "fill": "solid"
              },
              "lineWidth": 1,
              "pointSize": 1,
              "scaleDistribution": {
                "type": "linear"
              },
              "showPoints": "auto",
              "spanNulls": False,
              "stacking": {
                "group": "A",
                "mode": "none"
              },
              "thresholdsStyle": {
                "mode": "off"
              }
            },
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "blue",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 60
                }
              ]
            }
          },
          "overrides": [
            {
              "__systemRef": "hideSeriesFrom",
              "matcher": {
                "id": "byNames",
                "options": {
                  "mode": "exclude",
                  "names": [
                    "Humidity"
                  ],
                  "prefix": "All except:",
                  "readOnly": True
                }
              },
              "properties": [
                {
                  "id": "custom.hideFrom",
                  "value": {
                    "legend": False,
                    "tooltip": False,
                    "viz": True
                  }
                }
              ]
            },
            {
              "matcher": {
                "id": "byName",
                "options": "Humidity"
              },
              "properties": [
                {
                  "id": "color",
                  "value": {
                    "fixedColor": "blue",
                    "mode": "fixed"
                  }
                }
              ]
            }
          ]
        },
        "gridPos": {
          "h": 11,
          "w": 5,
          "x": 14,
          "y": 0
        },
        "id": 3,
        "options": {
          "legend": {
            "calcs": [],
            "displayMode": "list",
            "placement": "bottom"
          },
          "tooltip": {
            "mode": "single",
            "sort": "none"
          }
        },
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": Model_ID,
            "propertyId": Humidity_ID,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-east-1",
            "timeOrdering": "ASCENDING"
          }
        ],
        "title": "Humidity",
        "type": "timeseries"
      },
      {
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            },
            "custom": {
              "axisLabel": "",
              "axisPlacement": "auto",
              "barAlignment": 0,
              "drawStyle": "line",
              "fillOpacity": 0,
              "gradientMode": "none",
              "hideFrom": {
                "legend": False,
                "tooltip": False,
                "viz": False
              },
              "lineInterpolation": "smooth",
              "lineStyle": {
                "fill": "solid"
              },
              "lineWidth": 1,
              "pointSize": 1,
              "scaleDistribution": {
                "type": "linear"
              },
              "showPoints": "auto",
              "spanNulls": False,
              "stacking": {
                "group": "A",
                "mode": "none"
              },
              "thresholdsStyle": {
                "mode": "off"
              }
            },
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": [
            {
              "matcher": {
                "id": "byName",
                "options": "rpm"
              },
              "properties": [
                {
                  "id": "color",
                  "value": {
                    "fixedColor": "super-light-green",
                    "mode": "fixed"
                  }
                }
              ]
            }
          ]
        },
        "gridPos": {
          "h": 11,
          "w": 5,
          "x": 19,
          "y": 0
        },
        "id": 5,
        "options": {
          "legend": {
            "calcs": [],
            "displayMode": "list",
            "placement": "bottom"
          },
          "tooltip": {
            "mode": "single",
            "sort": "none"
          }
        },
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": Model_ID,
            "propertyId": rpm_ID,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-east-1",
            "timeOrdering": "ASCENDING"
          }
        ],
        "title": "rpm",
        "type": "timeseries"
      },
      {
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "mappings": [],
            "max": 120,
            "min": 0,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "orange",
                  "value": 60
                },
                {
                  "color": "red",
                  "value": 70
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 5,
          "w": 3,
          "x": 0,
          "y": 6
        },
        "id": 15,
        "options": {
          "colorMode": "value",
          "graphMode": "area",
          "justifyMode": "auto",
          "orientation": "auto",
          "reduceOptions": {
            "calcs": [
              "lastNotNull"
            ],
            "fields": "",
            "values": False
          },
          "textMode": "auto"
        },
        "pluginVersion": "8.4.7",
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": Humidity_ID,
            "queryType": "PropertyValue",
            "refId": "A"
          }
        ],
        "title": "Humidity",
        "type": "stat"
      },
      {
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "mappings": [],
            "max": 120,
            "min": 0,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "orange",
                  "value": 60
                },
                {
                  "color": "red",
                  "value": 70
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 5,
          "w": 2,
          "x": 3,
          "y": 6
        },
        "id": 16,
        "options": {
          "colorMode": "value",
          "graphMode": "area",
          "justifyMode": "auto",
          "orientation": "auto",
          "reduceOptions": {
            "calcs": [
              "lastNotNull"
            ],
            "fields": "",
            "values": False
          },
          "textMode": "auto"
        },
        "pluginVersion": "8.4.7",
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": rpm_ID,
            "queryType": "PropertyValue",
            "refId": "A"
          }
        ],
        "title": "RPM",
        "type": "stat"
      },
      {
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "mappings": [],
            "max": 120,
            "min": 0,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "orange",
                  "value": 60
                },
                {
                  "color": "red",
                  "value": 70
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 7,
          "w": 1,
          "x": 0,
          "y": 11
        },
        "id": 18,
        "options": {
          "colorMode": "value",
          "graphMode": "area",
          "justifyMode": "auto",
          "orientation": "auto",
          "reduceOptions": {
            "calcs": [
              "lastNotNull"
            ],
            "fields": "",
            "values": False
          },
          "textMode": "auto"
        },
        "pluginVersion": "8.4.7",
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": Flow_ID,
            "queryType": "PropertyValue",
            "refId": "A"
          }
        ],
        "title": "Flow",
        "type": "stat"
      },
      {
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "mappings": [],
            "max": 120,
            "min": 0,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "orange",
                  "value": 60
                },
                {
                  "color": "red",
                  "value": 70
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 7,
          "w": 2,
          "x": 1,
          "y": 11
        },
        "id": 17,
        "options": {
          "colorMode": "value",
          "graphMode": "area",
          "justifyMode": "auto",
          "orientation": "auto",
          "reduceOptions": {
            "calcs": [
              "lastNotNull"
            ],
            "fields": "",
            "values": False
          },
          "textMode": "auto"
        },
        "pluginVersion": "8.4.7",
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": Pressure_ID,
            "queryType": "PropertyValue",
            "refId": "A"
          }
        ],
        "title": "Pressure",
        "type": "stat"
      },
      {
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "mappings": [],
            "max": 120,
            "min": 0,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "orange",
                  "value": 60
                },
                {
                  "color": "red",
                  "value": 70
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 7,
          "w": 2,
          "x": 3,
          "y": 11
        },
        "id": 14,
        "options": {
          "colorMode": "value",
          "graphMode": "area",
          "justifyMode": "auto",
          "orientation": "auto",
          "reduceOptions": {
            "calcs": [
              "lastNotNull"
            ],
            "fields": "",
            "values": False
          },
          "textMode": "auto"
        },
        "pluginVersion": "8.4.7",
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": Vibration_ID,
            "queryType": "PropertyValue",
            "refId": "A"
          }
        ],
        "title": "Vibration",
        "type": "stat"
      },
      {
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            },
            "custom": {
              "axisLabel": "",
              "axisPlacement": "auto",
              "barAlignment": 0,
              "drawStyle": "line",
              "fillOpacity": 0,
              "gradientMode": "none",
              "hideFrom": {
                "legend": False,
                "tooltip": False,
                "viz": False
              },
              "lineInterpolation": "smooth",
              "lineStyle": {
                "fill": "solid"
              },
              "lineWidth": 1,
              "pointSize": 1,
              "scaleDistribution": {
                "type": "linear"
              },
              "showPoints": "auto",
              "spanNulls": False,
              "stacking": {
                "group": "A",
                "mode": "none"
              },
              "thresholdsStyle": {
                "mode": "off"
              }
            },
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": [
            {
              "matcher": {
                "id": "byName",
                "options": "Flow"
              },
              "properties": [
                {
                  "id": "color",
                  "value": {
                    "fixedColor": "dark-purple",
                    "mode": "fixed"
                  }
                }
              ]
            }
          ]
        },
        "gridPos": {
          "h": 7,
          "w": 5,
          "x": 5,
          "y": 11
        },
        "id": 6,
        "options": {
          "legend": {
            "calcs": [],
            "displayMode": "list",
            "placement": "bottom"
          },
          "tooltip": {
            "mode": "single",
            "sort": "none"
          }
        },
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": Model_ID,
            "propertyId": Flow_ID,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-east-1",
            "timeOrdering": "ASCENDING"
          }
        ],
        "title": "Flow",
        "type": "timeseries"
      },
      {
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            },
            "custom": {
              "axisLabel": "",
              "axisPlacement": "auto",
              "barAlignment": 0,
              "drawStyle": "line",
              "fillOpacity": 0,
              "gradientMode": "none",
              "hideFrom": {
                "legend": False,
                "tooltip": False,
                "viz": False
              },
              "lineInterpolation": "smooth",
              "lineStyle": {
                "fill": "solid"
              },
              "lineWidth": 1,
              "pointSize": 1,
              "scaleDistribution": {
                "type": "linear"
              },
              "showPoints": "auto",
              "spanNulls": False,
              "stacking": {
                "group": "A",
                "mode": "none"
              },
              "thresholdsStyle": {
                "mode": "off"
              }
            },
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": [
            {
              "matcher": {
                "id": "byName",
                "options": "Temperature"
              },
              "properties": [
                {
                  "id": "color",
                  "value": {
                    "fixedColor": "yellow",
                    "mode": "fixed"
                  }
                }
              ]
            },
            {
              "matcher": {
                "id": "byName",
                "options": "Pressure"
              },
              "properties": [
                {
                  "id": "color",
                  "value": {
                    "fixedColor": "orange",
                    "mode": "fixed"
                  }
                }
              ]
            }
          ]
        },
        "gridPos": {
          "h": 7,
          "w": 9,
          "x": 10,
          "y": 11
        },
        "id": 10,
        "options": {
          "legend": {
            "calcs": [],
            "displayMode": "list",
            "placement": "bottom"
          },
          "tooltip": {
            "mode": "single",
            "sort": "none"
          }
        },
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": Model_ID,
            "propertyId": Pressure_ID,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-east-1",
            "timeOrdering": "ASCENDING"
          }
        ],
        "title": "Pressure",
        "type": "timeseries"
      },
      {
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            },
            "custom": {
              "axisLabel": "",
              "axisPlacement": "auto",
              "barAlignment": 0,
              "drawStyle": "line",
              "fillOpacity": 0,
              "gradientMode": "none",
              "hideFrom": {
                "legend": False,
                "tooltip": False,
                "viz": False
              },
              "lineInterpolation": "smooth",
              "lineStyle": {
                "fill": "solid"
              },
              "lineWidth": 1,
              "pointSize": 1,
              "scaleDistribution": {
                "type": "linear"
              },
              "showPoints": "auto",
              "spanNulls": False,
              "stacking": {
                "group": "A",
                "mode": "none"
              },
              "thresholdsStyle": {
                "mode": "off"
              }
            },
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": [
            {
              "__systemRef": "hideSeriesFrom",
              "matcher": {
                "id": "byNames",
                "options": {
                  "mode": "exclude",
                  "names": [
                    "Vibration"
                  ],
                  "prefix": "All except:",
                  "readOnly": True
                }
              },
              "properties": [
                {
                  "id": "custom.hideFrom",
                  "value": {
                    "legend": False,
                    "tooltip": False,
                    "viz": True
                  }
                }
              ]
            },
            {
              "matcher": {
                "id": "byName",
                "options": "Vibration"
              },
              "properties": [
                {
                  "id": "color",
                  "value": {
                    "fixedColor": "semi-dark-yellow",
                    "mode": "fixed"
                  }
                }
              ]
            }
          ]
        },
        "gridPos": {
          "h": 7,
          "w": 5,
          "x": 19,
          "y": 11
        },
        "id": 9,
        "options": {
          "legend": {
            "calcs": [],
            "displayMode": "list",
            "placement": "bottom"
          },
          "tooltip": {
            "mode": "single",
            "sort": "none"
          }
        },
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": Model_ID,
            "propertyId": Vibration_ID,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-east-1",
            "timeOrdering": "ASCENDING"
          }
        ],
        "title": "Vibration",
        "type": "timeseries"
      },
      {
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "mappings": [],
            "max": 120,
            "min": 0,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "orange",
                  "value": 60
                },
                {
                  "color": "red",
                  "value": 70
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 5,
          "w": 3,
          "x": 0,
          "y": 18
        },
        "id": 20,
        "options": {
          "colorMode": "value",
          "graphMode": "area",
          "justifyMode": "auto",
          "orientation": "auto",
          "reduceOptions": {
            "calcs": [
              "lastNotNull"
            ],
            "fields": "",
            "values": False
          },
          "textMode": "auto"
        },
        "pluginVersion": "8.4.7",
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": Voltage_ID,
            "queryType": "PropertyValue",
            "refId": "A"
          }
        ],
        "title": "Voltage",
        "type": "stat"
      },
      {
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "mappings": [],
            "max": 120,
            "min": 0,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "orange",
                  "value": 60
                },
                {
                  "color": "red",
                  "value": 70
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 5,
          "w": 2,
          "x": 3,
          "y": 18
        },
        "id": 19,
        "options": {
          "colorMode": "value",
          "graphMode": "area",
          "justifyMode": "auto",
          "orientation": "auto",
          "reduceOptions": {
            "calcs": [
              "lastNotNull"
            ],
            "fields": "",
            "values": False
          },
          "textMode": "auto"
        },
        "pluginVersion": "8.4.7",
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": Amperage_ID,
            "queryType": "PropertyValue",
            "refId": "A"
          }
        ],
        "title": "Amperage",
        "type": "stat"
      },
      {
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            },
            "custom": {
              "axisLabel": "",
              "axisPlacement": "auto",
              "barAlignment": 0,
              "drawStyle": "line",
              "fillOpacity": 0,
              "gradientMode": "none",
              "hideFrom": {
                "legend": False,
                "tooltip": False,
                "viz": False
              },
              "lineInterpolation": "smooth",
              "lineStyle": {
                "fill": "solid"
              },
              "lineWidth": 1,
              "pointSize": 1,
              "scaleDistribution": {
                "type": "linear"
              },
              "showPoints": "auto",
              "spanNulls": False,
              "stacking": {
                "group": "A",
                "mode": "none"
              },
              "thresholdsStyle": {
                "mode": "off"
              }
            },
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": [
            {
              "__systemRef": "hideSeriesFrom",
              "matcher": {
                "id": "byNames",
                "options": {
                  "mode": "exclude",
                  "names": [
                    "Voltage"
                  ],
                  "prefix": "All except:",
                  "readOnly": True
                }
              },
              "properties": [
                {
                  "id": "custom.hideFrom",
                  "value": {
                    "legend": False,
                    "tooltip": False,
                    "viz": True
                  }
                }
              ]
            },
            {
              "matcher": {
                "id": "byName",
                "options": "Voltage"
              },
              "properties": [
                {
                  "id": "color",
                  "value": {
                    "fixedColor": "super-light-orange",
                    "mode": "fixed"
                  }
                }
              ]
            }
          ]
        },
        "gridPos": {
          "h": 5,
          "w": 11,
          "x": 5,
          "y": 18
        },
        "id": 4,
        "options": {
          "legend": {
            "calcs": [],
            "displayMode": "list",
            "placement": "bottom"
          },
          "tooltip": {
            "mode": "single",
            "sort": "none"
          }
        },
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": Model_ID,
            "propertyId": Voltage_ID,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-east-1",
            "timeOrdering": "ASCENDING"
          }
        ],
        "title": "Voltage",
        "type": "timeseries"
      },
      {
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            },
            "custom": {
              "axisLabel": "",
              "axisPlacement": "auto",
              "barAlignment": 0,
              "drawStyle": "line",
              "fillOpacity": 0,
              "gradientMode": "none",
              "hideFrom": {
                "legend": False,
                "tooltip": False,
                "viz": False
              },
              "lineInterpolation": "smooth",
              "lineStyle": {
                "fill": "solid"
              },
              "lineWidth": 1,
              "pointSize": 1,
              "scaleDistribution": {
                "type": "linear"
              },
              "showPoints": "auto",
              "spanNulls": False,
              "stacking": {
                "group": "A",
                "mode": "none"
              },
              "thresholdsStyle": {
                "mode": "off"
              }
            },
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": [
            {
              "matcher": {
                "id": "byName",
                "options": "Amperage"
              },
              "properties": [
                {
                  "id": "color",
                  "value": {
                    "fixedColor": "super-light-yellow",
                    "mode": "fixed"
                  }
                }
              ]
            }
          ]
        },
        "gridPos": {
          "h": 5,
          "w": 8,
          "x": 16,
          "y": 18
        },
        "id": 7,
        "options": {
          "legend": {
            "calcs": [],
            "displayMode": "list",
            "placement": "bottom"
          },
          "tooltip": {
            "mode": "single",
            "sort": "none"
          }
        },
        "targets": [
          {
            "assetId": Asset_ID,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": Model_ID,
            "propertyId": Amperage_ID,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-east-1",
            "timeOrdering": "ASCENDING"
          }
        ],
        "title": "Amperage",
        "type": "timeseries"
      },
        {
        "gridPos": {
          "h": 4,
          "w": 24,
          "x": 0,
          "y": 23
        },
        "id": 22,
        "options": {
          "alertName": "",
          "dashboardAlerts": False,
          "dashboardTitle": "",
          "maxItems": 10,
          "showOptions": "current",
          "sortOrder": 1,
          "stateFilter": {
            "alerting": False,
            "execution_error": False,
            "no_data": False,
            "ok": False,
            "paused": False,
            "pending": False
          },
          "tags": []
        },
        "pluginVersion": "8.4.7",
        "title": "Alerts",
        "type": "alertlist"
      }
    ],
    "refresh": "5s",
    "schemaVersion": 35,
    "style": "dark",
    "tags": [],
    "templating": {
      "list": []
    },
    "time": {
      "from": "now-15m",
      "to": "now"
    },
    "timepicker": {},
    "timezone": "",
    "title": Dashboard_name,
    "id": None,
    "uid": Dashboard_uid,
    "version": 0,
    "weekStart": ""
    },
    "folderId": 0,
    "overwrite": True
  }
  
  new_dashboard_data = dashboard_template
                        
 
  
                        
  r = requests.post(url = url, headers = headers, data = json.dumps(new_dashboard_data), verify=True)
  print(r.json())
  
  time.sleep(2)
  
print("the scrip has finished sucesefully, congratulations !!!")
  
