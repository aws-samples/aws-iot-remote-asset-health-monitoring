import requests
import time
import json
import subprocess as sp
import argparse

#get Argument
parser = argparse.ArgumentParser()
parser.add_argument("-g", "--grafana-host", action="store", required=True, dest="ip")
parser.add_argument("-k", "--api-key", action="store", required=True, dest="api_key")
parser.add_argument("-r", "--model-id", action="store", required=True, dest="asset_model_id")
args = parser.parse_args()
ip = args.ip
api_key = args.api_key
asset_model_id = args.asset_model_id

url = f"http://{ip}/api/dashboards/db"

headers = {
    "Authorization":f"Bearer {api_key}",
    "Content-Type":"application/json",
    "Accept": "application/json"
}

def get_assets(asset_model_id):
    list_assets_cmd_output = sp.getoutput(f"aws iotsitewise list-assets --asset-model-id {asset_model_id}")
    list_assets_json = json.loads(list_assets_cmd_output)
    
    assets = list_assets_json["assetSummaries"]
    return assets

def get_asset_name(asset_id):
    describe_asset_cmd_output = sp.getoutput(f"aws iotsitewise describe-asset \
    --asset-id {asset_id}")
    describe_asset_json = json.loads(describe_asset_cmd_output) 
    return describe_asset_json["assetName"]

def get_asset_properties(asset_id):
    describe_asset_cmd_output = sp.getoutput(f"aws iotsitewise describe-asset \
    --asset-id {asset_id}")
    describe_asset_json = json.loads(describe_asset_cmd_output) 
    return describe_asset_json["assetProperties"]

def get_asset_relationship(asset_id):
    asset_relationships_cmd_output = sp.getoutput(f"aws iotsitewise list-asset-relationships \
    --asset-id {asset_id} --traversal-type PATH_TO_ROOT")
    asset_relationships_json = json.loads(asset_relationships_cmd_output) 
    return asset_relationships_json["assetRelationshipSummaries"]

assets = get_assets(asset_model_id)

for asset in assets:
    asset_id = asset["id"]
    asset_name = asset["name"]
    model_id = asset_model_id
    #Properties
    properties=get_asset_properties(asset_id)
    max_temperature_id = properties[0]["id"]
    temperature_id = properties[1]["id"]
    humidity_id = properties[2]["id"]
    pressure_id = properties[3]["id"]
    vibration_id = properties[4]["id"]
    flow_id = properties[5]["id"]
    rpm_id= properties[6]["id"]
    voltage_id = properties[7]["id"]
    amperage_id = properties[8]["id"]
    fan_id = properties[9]["id"]
    
    #Asset Parents
    asset_relationship = get_asset_relationship(asset_id)
    parent_id = asset_relationship[0]["hierarchyInfo"]["parentAssetId"]
    grandparent_id = asset_relationship[1]["hierarchyInfo"]["parentAssetId"]
    parent_name = get_asset_name(parent_id)
    grandparent_name = get_asset_name(grandparent_id)
    
    #Dashboard Header
    dashboard_name = f"{asset_name}-{parent_name}-{grandparent_name}/Status"
    dashboard_uid = f"{asset_name}-{parent_name}-{grandparent_name}"
    #Alert_name = f"{asset_name} Temperature Alert"
    
    print(f"Creating Grafana Dashboard - {dashboard_name}") 
     
    #Dashboard Data
    dashboard_data={
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": temperature_id,
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": fan_id,
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
          "name": f"Temperature alert {asset_name}",
          "message": f"temperature on {asset_name} is High the asset is unhealthy",
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": model_id,
            "propertyId": temperature_id,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-west-2",
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": model_id,
            "propertyId": fan_id,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-west-2",
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": model_id,
            "propertyId": humidity_id,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-west-2",
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": model_id,
            "propertyId": rpm_id,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-west-2",
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": humidity_id,
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": rpm_id,
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": flow_id,
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": pressure_id,
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": vibration_id,
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": model_id,
            "propertyId": flow_id,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-west-2",
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": model_id,
            "propertyId": pressure_id,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-west-2",
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": model_id,
            "propertyId": vibration_id,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-west-2",
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": voltage_id,
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "maxPageAggregations": 1,
            "propertyId": amperage_id,
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": model_id,
            "propertyId": voltage_id,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-west-2",
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
            "assetId": asset_id,
            "datasource": {
              "type": "grafana-iot-sitewise-datasource",
              "uid": None
            },
            "filter": "ALL",
            "maxPageAggregations": 1,
            "modelId": model_id,
            "propertyId": amperage_id,
            "queryType": "PropertyValueHistory",
            "refId": "A",
            "region": "us-west-2",
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
    "title": dashboard_name,
    "id": None,
    "uid": dashboard_uid,
    "version": 0,
    "weekStart": ""
    },
        "folderId": 0,
        "overwrite": True
    }
    
    r = requests.post(url = url, headers = headers, data = json.dumps(dashboard_data), verify=True)
    print(r.json())
  
    time.sleep(2)
    
print("Script finished successfully, congratulations !!!")
