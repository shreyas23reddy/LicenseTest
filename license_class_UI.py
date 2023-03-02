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

    def getARP(vmanage_host,vmanage_port,header,site_id):

        api_ARP = '/dataservice/device/arp?deviceId='+ site_id
        url_ARP = Operation.url(vmanage_host,vmanage_port,api_ARP)
        ARP = Operation.get_method(url_ARP,header)
        return ARP['data']


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






class findTlocExt():

    """
    will identify TLOC EXT interface only when the interface is directly connected.
    we are comparing the ARP dynamic address with static address on the remote side
    to identify if the interface is extended using TLOC ext or not
    re.split(r"\.", iter_edge1_ARP['interface'])[0]
    """

    def findIfTlocext(vmanage_host,vmanage_port,header,deviceInfo_data,site_id):

        getARP_edge1 = getData.getARP(vmanage_host,vmanage_port,header,(list((deviceInfo_data[site_id]).keys()))[0])
        getARP_edge2 = getData.getARP(vmanage_host,vmanage_port,header,(list((deviceInfo_data[site_id]).keys()))[1])


        for iter_edge1_ARP in getARP_edge1:
            if ((iter_edge1_ARP["vpn-id"] == "Default") or (iter_edge1_ARP["vpn-id"] == "0")) and (iter_edge1_ARP["mode"] == "ios-arp-mode-dynamic"):
                for iter_edge2_ARP in getARP_edge2:
                    if (((((iter_edge2_ARP["vpn-id"] == "Default") or (iter_edge2_ARP["vpn-id"] == "0")) and (iter_edge2_ARP["mode"] == "ios-arp-mode-interface")) and iter_edge1_ARP["hardware"] == iter_edge2_ARP["hardware"] ) and iter_edge1_ARP["address"] == iter_edge2_ARP["address"]):
                        if (re.split(r"\.", iter_edge2_ARP['interface'])[0]) in deviceInfo_data[site_id][iter_edge2_ARP["vdevice-name"]]["wanIFName-stats"] and (((re.split(r"\.", iter_edge2_ARP['interface'])[0]) not in deviceInfo_data[site_id][iter_edge2_ARP["vdevice-name"]]["TlocEXT-IfName"])):
                            deviceInfo_data[site_id][iter_edge2_ARP["vdevice-name"]]["TlocEXT-IfName"].append(re.split(r"\.", iter_edge2_ARP['interface'])[0])


        for iter_edge2_ARP in getARP_edge2:
            if ((iter_edge2_ARP["vpn-id"] == "Default") or (iter_edge2_ARP["vpn-id"] == "0")) and (iter_edge2_ARP["mode"] == "ios-arp-mode-dynamic"):
                for iter_edge1_ARP in getARP_edge1:
                    if (((((iter_edge1_ARP["vpn-id"] == "Default") or (iter_edge1_ARP["vpn-id"] == "0")) and (iter_edge1_ARP["mode"] == "ios-arp-mode-interface")) and iter_edge2_ARP["hardware"] == iter_edge1_ARP["hardware"] ) and iter_edge2_ARP["address"] == iter_edge1_ARP["address"]):
                        if ((re.split(r"\.", iter_edge1_ARP['interface'])[0]) in deviceInfo_data[site_id][iter_edge1_ARP["vdevice-name"]]["wanIFName-stats"]) and ((re.split(r"\.", iter_edge1_ARP['interface'])[0]) not in deviceInfo_data[site_id][iter_edge1_ARP["vdevice-name"]]["TlocEXT-IfName"]):
                            deviceInfo_data[site_id][iter_edge1_ARP["vdevice-name"]]["TlocEXT-IfName"].append(re.split(r"\.", iter_edge1_ARP['interface'])[0])

        return deviceInfo_data
