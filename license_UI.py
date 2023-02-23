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


        sid.add_argument('-id', nargs = '+', required=True)


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
        print(args.id)

        for site_id in args.id:

            """ To get the details of a specific Site-ID  '/dataservice/device?site-id='+site_id """
            deviceInfo = getData.getDeviceIP(vmanage_host,vmanage_port,header,site_id)

            if deviceInfo == []:
                print(f"""please verify if the site-id {site_id} is valid""")
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
                    "wanIFName":[]
                    }


        print(deviceInfo_data["20"]["20.20.20.1"])



        exit()
