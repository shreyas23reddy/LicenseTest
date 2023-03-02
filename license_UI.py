import requests
import json
import yaml
import re
import time
import sys
import csv
import argparse
from datetime import datetime
import itertools


from auth_header import Authentication as auth
from operations import Operation
from license_class_UI import getData
from license_class_UI import postData
from license_class_UI import findTlocExt
from query import queryPayload




if __name__=='__main__':

    while True:

        """ Adding cli via Arg parse """

        parser = argparse.ArgumentParser()

        parser.add_argument("-a","--address", help="vManage IP address")
        parser.add_argument("-p","--port", default=8443, help="vManage port")
        parser.add_argument("-u","--username", help="vManage username")
        parser.add_argument("-pw","--password", help="vManage password")



        subparser = parser.add_subparsers(dest='command',help="'sid' - run script on a specific site id's")

        """'sid' will pull the detials from a specific site-id's in the overlay """


        sid = subparser.add_parser('sid')


        sid.add_argument('-id', nargs = '+', required=True, help= "-id 10 20 30")
        sid.add_argument('-tlocext',choices=["yes","no"],default="no",help = "will identify TLOC EXT interface only when the interface is directly connected. 'yes/no'")


        args = parser.parse_args()

        vmanage_host = args.address
        vmanage_port = args.port
        username = args.username
        password = args.password


        """ GET the TOKEN from Authnetication call"""
        header= auth.get_header(vmanage_host, vmanage_port,username, password)

        """ data collection Dict """
        deviceInfo_data = {}
        Lic_data={}

        now = datetime.now()


        for site_id in args.id:

            """ To get the details of a specific Site-ID  '/dataservice/device?site-id='+site_id """
            deviceInfo = getData.getDeviceIP(vmanage_host,vmanage_port,header,site_id)

            if deviceInfo == []:
                print(f"""
                please verify if the site-id {site_id} is valid
                """)

            else:
                for iter_deviceInfo in deviceInfo:

                    if iter_deviceInfo["site-id"] not in deviceInfo_data:
                        deviceInfo_data[iter_deviceInfo["site-id"]] = {}
                        Lic_data[iter_deviceInfo["site-id"]] = {"interfaceStats_kbps":[],"License-Tier":"T0"}
                    if iter_deviceInfo["system-ip"] not in deviceInfo_data[iter_deviceInfo["site-id"]]:
                        deviceInfo_data[iter_deviceInfo["site-id"]][iter_deviceInfo["system-ip"]] = {}

                    deviceInfo_data[iter_deviceInfo["site-id"]][iter_deviceInfo["system-ip"]] = {
                    "host-name":iter_deviceInfo["host-name"],
                    "uuid":iter_deviceInfo["uuid"],
                    "reachability":iter_deviceInfo["reachability"],
                    "validity":iter_deviceInfo["validity"],
                    "wanIFName-stats":{},
                    "TlocEXT-IfName":[],
                    }


                    wanIFName = getData.getWANIfName(vmanage_host,vmanage_port,header,iter_deviceInfo["system-ip"])

                    for iter_wanIFName in wanIFName:
                        TransportIfName = re.split(r"\.", iter_wanIFName["interface"])[0]
                        #TransportIfName = (iter_wanIFName["interface"])
                        # append the interface name to deviceInfo_data
                        if TransportIfName not in deviceInfo_data[iter_deviceInfo["site-id"]][iter_deviceInfo["system-ip"]]["wanIFName-stats"]:
                            deviceInfo_data[iter_deviceInfo["site-id"]][iter_deviceInfo["system-ip"]]["wanIFName-stats"][TransportIfName]=[]

                if (len(deviceInfo_data[site_id])) == 2 and args.tlocext == "yes":
                    deviceInfo_data = findTlocExt.findIfTlocext(vmanage_host,vmanage_port,header,deviceInfo_data,site_id)








        #print(deviceInfo_data)


        for iterSiteID in deviceInfo_data:

            for iterSystemIP in list(deviceInfo_data[iterSiteID].keys()):

                if (deviceInfo_data[iterSiteID][iterSystemIP]['reachability'] == 'reachable') and (deviceInfo_data[iterSiteID][iterSystemIP]['validity'] == 'valid'):

                    for iterTransportIfName in deviceInfo_data[iterSiteID][iterSystemIP]["wanIFName-stats"]:

                        """
                        we would be unable to use sub interface to pull interface Stats
                        so we would create a physical interface.
                        """


                        """
                        data = queryPayload.statsIFAgg(iterSystemIP , iterTransportIfName, duration = "2", interval = 30)
                        create a query payload to pull the interface stats
                        duration is in hours, interval is in minutes
                        """

                        data = queryPayload.statsIFAgg(iterSystemIP , iterTransportIfName, duration = "2", interval = 30)

                        time.sleep(0.3)

                        print(f"pulling the interface stats of Site-ID {iterSiteID} -- System-IP {iterSystemIP} -- TLOC parent Interface {iterTransportIfName}")

                        interfaceStats = postData.getInterfaceStats(vmanage_host,vmanage_port,header,data)

                        deviceInfo_data[iterSiteID][iterSystemIP]["wanIFName-stats"][iterTransportIfName]=interfaceStats





                        """
                        if data is null this would be the first interface iteration per site.
                        if the subsequent interface stats have less number of data

                        Lic_data[iter_deviceInfo["site-id"]] = {"interfaceStats"=[],"License-Tier":"T0"}
                        """

                        if (iterTransportIfName not in deviceInfo_data[iterSiteID][iterSystemIP]["TlocEXT-IfName"]):
                            #print(interfaceStats)
                            if  Lic_data[iterSiteID]["interfaceStats_kbps"]== []:
                                for iter_interfaceStats in interfaceStats:
                                    Lic_data[iterSiteID]["interfaceStats_kbps"].append(iter_interfaceStats['tx_kbps']+iter_interfaceStats['rx_kbps'])
                            elif len(Lic_data[iterSiteID]["interfaceStats_kbps"]) >= len(interfaceStats):
                                for index,iter_interfaceStats in enumerate(interfaceStats):
                                    Lic_data[iterSiteID]["interfaceStats_kbps"][index] += (iter_interfaceStats['tx_kbps']+iter_interfaceStats['rx_kbps'])
                            else:
                                for index in range(len(Lic_data[iterSiteID]["interfaceStats_kbps"])):
                                    Lic_data[iterSiteID]["interfaceStats_kbps"][index] += (interfaceStats[index]['tx_kbps']+interfaceStats[index]['rx_kbps'])


            AggMbps = max(Lic_data[iterSiteID]["interfaceStats_kbps"])/1000

            if AggMbps <= 50:
                Lic_data[iterSiteID]["License-Tier"] = "T0"
            elif 50 < AggMbps <= 400:
                Lic_data[iterSiteID]["License-Tier"] = "T1"
            elif 400 < AggMbps <= 2000:
                Lic_data[iterSiteID]["License-Tier"] = "T2"
            elif 2000 < AggMbps <= 20000:
                Lic_data[iterSiteID]["License-Tier"] = "T3"

            #print(Lic_data)

        print("===========")
        print(Lic_data)
        print("===========")
        print(deviceInfo_data)
        print("===========")

        exit()
