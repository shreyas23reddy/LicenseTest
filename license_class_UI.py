"""
import all the reqiured librariers
"""
import requests
import json
import difflib
import yaml
import re
import time


from auth_header import Authentication as auth
from operations import Operation


class getData():

    def getDeviceIP(vmanage_host,vmanage_port,header,site_id):

        api_Device = '/dataservice/device?site-id='+ site_id
        url_Device = Operation.url(vmanage_host,vmanage_port,api_Device)
        DeviceIP = Operation.get_method(url_Device,header)
        return DeviceIP['data']



    def getWANIfName(vmanage_host,vmanage_port,header,deviceID):

        api_WAN_IF_Name = '/dataservice/device/control/waninterface?deviceId='+str(deviceID)
        url_WAN_IF_Name = Operation.url(vmanage_host,vmanage_port,api_WAN_IF_Name)
        WAN_IF_Name = Operation.get_method(url_WAN_IF_Name,header)
        return WAN_IF_Name['data']




class postData():

    def getInterfaceStats(vmanage_host,vmanage_port,header,data):
        api_Interface_Stats = '/dataservice/statistics/interface/aggregation'
        url_Interface_Stats = Operation.url(vmanage_host,vmanage_port,api_Interface_Stats)
        Interface_Stats = Operation.post_method(url_Interface_Stats,header,data)
        return Interface_Stats['data']
