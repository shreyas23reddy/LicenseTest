import requests
import json


class Operation():

    """
    GET Call Operation
    return response Json format
    or Error if not codes["ok"]
    """
    def get_method(url, header):

        response = requests.request("GET",url=url,headers=header,verify=False)

        if response.status_code ==  requests.codes['ok']:
            return (response.json())
        else:
            raise Exception('Error: ' + str(response.status_code))

    """
    POST Call Operation
    return response Json format
    or Error if not codes["ok"]
    """

    def post_method(url, header, data={}):


        #response = requests.request("POST", url=  url, headers = header, data = params, verify = False )
        response = requests.request("POST", url=  url, headers = header, json = data, verify = False )


        if response.status_code ==  requests.codes['ok']:
            return (response.json())
        else:
            raise Exception('Error: ' + str(response.status_code))

    """
    DELETE Call Operation
    return response Json format
    or Error if not codes["ok"]
    """

    def delete_method(url, header):

        response = requests.request("DELETE",url=url,headers=header,verify=False)

        if response.status_code ==  requests.codes['ok']:
            return (response)
        else:
            raise Exception('Error: ' + str(response.status_code))


    """
    URL function
    returning vmanage_host+vmanage_port+API
    """

    def url(vmanage_host,vmanage_port,api):
        """ return the URL for the privide API ENDpoint """
        """ function to get the url provide api endpoint """

        return f"https://{vmanage_host}:{vmanage_port}{api}"
