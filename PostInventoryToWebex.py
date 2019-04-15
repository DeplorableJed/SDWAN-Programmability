#!/usr/bin/env python
"""This Python Script will post SDWAN inventory to webex Teams
"""

import ciscosparkapi
import json
import os
import requests
import urllib3
import configparser
# Disable Certificate warning
try:
    requests.packages.urllib3.disable_warnings()
except:
    pass
from requests.auth import HTTPBasicAuth
import sys

# Get the absolute path for the directory where this file is located "here"
here = os.path.abspath(os.path.dirname(__file__))

# Get the absolute path for the project / repository root
project_root = os.path.abspath(os.path.join(here, '../..'))

# Extend the system path to include the project root and import the env files
sys.path.insert(0, project_root)
import env_lab      # noqa
import env_user     # noqa


# Create a Cisco Spark object
spark = ciscosparkapi.CiscoSparkAPI(access_token=env_user.SPARK_ACCESS_TOKEN)


# Details for DNA Center Platform API calls
sdwan_host = env_lab.vManage['host']
sdwan_user = env_lab.vManage['username']
sdwan_pass = env_lab.vManage['password']
sdwan_headers = {'content-type': 'application/json'}

def initalize_connection(ipaddress,username,password):

    """
    This function will initialize a connection to the vManage
    :param ipaddress: This is the IP Address and Port number of vManage
    :param username:  This is the username for vManage (admin in our lab)
    :param password:  This is a password for vManage (admin in our lab)
    These will be set in a file called package_config.ini
    """

    # Disable warnings like unsigned certificates, etc.
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    print('SDWAN Login to ' + sdwan_host + ' as ' + sdwan_username + ' ...')
    url="https://"+sdwan_host+"/j_security_check"

    payload = "j_username="+sdwan_user+"&j_password="+password
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        }

    sess=requests.session()

    # Handle exceptions if we cannot connect to the vManage
    try:
        response = sess.request("POST", url, data=payload, headers=headers,verify=False,timeout=10)
    except requests.exceptions.ConnectionError:
        print ("Unable to Connect to "+ipaddress)
        return False

    return sess

def get_inventory(sdwan_host,session):

    print("Retrieving the inventory data from the vManage at "+sdwan_host+"\n")

    url = "https://" + sdwan_host + "/dataservice/device"
    response = session.request("GET",url,verify=False,timeout=10)
    json_string = response.json()
    #print(json_string)

    # Initialize the inventory data dictionary
    inv={}

    for item in json_string['data']:
       print(item)
       print("=======================")
    for item in json_string['data']:
       print (item['host-name']+"   "+item['board-serial']+"   "+item['version']+"   "+item['controlConnections']+"   "+item['state']+"   "+item['personality']+"   "+item['system-ip'])
       inv[item['system-ip']]=item['host-name']
    return(inv)

    for item in json_string['data']:
        system_ip=item['system-ip']
        print('{0:15}  {1:20}  {2}     {3:36}  '.format("System IP", "Hostname", "Version","UUID"))
        print('{0:15}  {1:20}  {2}     {3:36}  '.format("---------", "--------", "-------","------------------------------------"))
        print ('{0:15}  {1:20}  {2}      {3:36}  '.format(item['system-ip'],item['host-name'],item['version'],item['uuid']))


message = spark.messages.create(env_user.SPARK_ROOM_ID,
    files=[next_data_file],
    text='SDWAN - Look Mom no HANDS!')
    print(message)

    print('\n\n')
    print('Network Devices and Modules from DNA Center have been written to ' +
          next_data_file)
    for item in json_string['data']:
        system_ip=item['system-ip']
        print('{0:15}  {1:20}  {2}     {3:36}  '.format("System IP", "Hostname", "Version","UUID"))
        print('{0:15}  {1:20}  {2}     {3:36}  '.format("---------", "--------", "-------","------------------------------------"))
        print ('{0:15}  {1:20}  {2}      {3:36}  '.format(item['system-ip'],item['host-name'],item['version'],item['uuid']))
