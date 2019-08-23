#!/usr/bin/env python
"""This Python Script will post a message to a webex Teams space when a policy is activated or deactivated
"""

import ciscosparkapi
import requests
import urllib3
import datetime
import time
import os
import json
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


# Details for SDWAN Center Platform API calls from env_lab file
sdwan_host = env_lab.vManage['host']
sdwan_user = env_lab.vManage['username']
sdwan_pass = env_lab.vManage['password']
sdwan_headers = {'content-type': 'application/json'}

# Details for ServiceNow API Access
snow_url = env_lab.serviceNow['url']
snow_user = env_lab.serviceNow['username']
snow_pass = env_lab.serviceNow['password']


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

    print('SDWAN Login to ' + sdwan_host + ' as ' + sdwan_user + ' ...')
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
        print ('{0:15}  {1:20}  {2}     {3:36}  '.format("System IP", "Hostname", "Version","UUID"))
        print ('{0:15}  {1:20}  {2}     {3:36}  '.format("---------", "--------", "-------","------------------------------------"))
        print ('{0:15}  {1:20}  {2}      {3:36}  '.format(item['system-ip'],item['host-name'],item['version'],item['uuid']))


def policy_cycle(sdwan_host,session):
    policy_id = "c19aa591-3993-4f67-a76c-5194b368345f"
    activate_policy_url = "https://%s/dataservice/template/policy/vsmart/activate/c19aa591-3993-4f67-a76c-5194b368345f"%(sdwan_host)
    deactivate_policy_url = "https://%s/dataservice/template/policy/vsmart/deactivate/c19aa591-3993-4f67-a76c-5194b368345f"%(sdwan_host)
    payload = "{\n }"
    headers = {'Content-Type':'application/json'}
    i=0
    while i<3:
        i+=1
        response = session.request("GET",activate_policy_url,verify=False,timeout=10)
        data = response.content
        print (data)
        t = datetime.datetime.now()
        print ("Policy Activated @ %s "%t)
        message = spark.messages.create(env_user.SPARK_ROOM_ID,text='Look No Hands')
        print(message)
        print('\n\n')
        time.sleep(1)

        response = session.request("GET",deactivate_policy_url,verify=False,timeout=10)
        data = response.content
        print (data)
        t = datetime.datetime.now()
        print ("Policy Deactivated @ %s "%t)
        message = spark.messages.create(env_user.SPARK_ROOM_ID,text='Look I Have HANDS!')
        print(message)
        print('\n\n')
        time.sleep(1)



def get_user_sys_id(snow_user):

    # find the ServiceNow user_id for the specified user

    url = snow_url + '/table/sys_user?sysparm_limit=1'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.get(url, auth=(snow_user, snow_pass), headers=headers)
    user_json = response.json()
    return user_json['result'][0]['sys_id']


def create_incident(description, comment, snow_user, severity):

    # This function will create a new incident with the {description}, {comments}, severity for the {user}

    caller_sys_id = get_user_sys_id(snow_user)
    print (caller_sys_id)
    url = snow_url + '/table/incident'
    payload = {'short_description': description,
               'comments': (comment + ', \nIncident created using APIs by caller by PUT_YOUR_NAME_HERE'),
               'caller_id': caller_sys_id,
               'urgency': severity
               }
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(url, auth=(snow_user, snow_pass), data=json.dumps(payload), headers=headers)
    incident_json = response.json()
    return incident_json['result']['number']


session=initalize_connection(sdwan_host,sdwan_user,sdwan_pass)
if session != False:
    print ("Connection to vManage successful")
    message = spark.messages.create(env_user.SPARK_ROOM_ID,text='Python was here')
    print(message)
    print('\n\n')
    policy_cycle(sdwan_host,session)
    comments = 'There has been a policy change on : ' + sdwan_host
    create_incident('Policy Change', comments, snow_user,3)
    print('Incident opened on Service-Now')
