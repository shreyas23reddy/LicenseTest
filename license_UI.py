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
        sid.add_argument('-tlocext',choices=["yes","no"],default="no",help = "will help identifying the TLOCEXT interface 'yes/no'")


        args = parser.parse_args()

        vmanage_host = args.address
        vmanage_port = args.port
        username = args.username
        password = args.password


        """ GET the TOKEN from Authnetication call"""
        header= auth.get_header(vmanage_host, vmanage_port,username, password)

        """ data collection Dict """
        deviceInfo_data = {}

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
                    if iter_deviceInfo["system-ip"] not in deviceInfo_data[iter_deviceInfo["site-id"]]:
                        deviceInfo_data[iter_deviceInfo["site-id"]][iter_deviceInfo["system-ip"]] = {}

                    deviceInfo_data[iter_deviceInfo["site-id"]][iter_deviceInfo["system-ip"]] = {
                    "host-name":iter_deviceInfo["host-name"],
                    "uuid":iter_deviceInfo["uuid"],
                    "reachability":iter_deviceInfo["reachability"],
                    "validity":iter_deviceInfo["validity"],
                    "wanIFName-stats":{},
                    "TlocEXT-IfName":[]
                    }


                    wanIFName = getData.getWANIfName(vmanage_host,vmanage_port,header,iter_deviceInfo["system-ip"])

                    for iter_wanIFName in wanIFName:

                        #if have a sub-interface strip the sub-interface tag
                        #TransportIfName = re.split(r"\.", iter_wanIFName["interface"])[0]
                        TransportIfName = (iter_wanIFName["interface"])
                        # append the interface name to deviceInfo_data
                        if TransportIfName not in deviceInfo_data[iter_deviceInfo["site-id"]][iter_deviceInfo["system-ip"]]["wanIFName-stats"]:
                            deviceInfo_data[iter_deviceInfo["site-id"]][iter_deviceInfo["system-ip"]]["wanIFName-stats"][TransportIfName]=[]

                if (len(deviceInfo_data[site_id])) == 2 and args.tlocext == "yes":
                    deviceInfo_data = findTlocExt.findIfTlocext(vmanage_host,vmanage_port,header,deviceInfo_data,site_id)










        print(deviceInfo_data)


        exit()
