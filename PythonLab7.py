import requests
import urllib3
import configparser



def initalize_connection(ipaddress,username,password):

    """
    This function will initialize a connection to thevManage
    :param ipaddress: This is the IP Address and Port number of vManage 
    :param username:  This is the username for vManage (admin in our lab)
    :param password:  This is a password for vManage (admin in our lab)
    These will be set in a file called package_config.ini
    """

    # Disable warnings like unsigned certificates, etc.
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    url="https://"+ipaddress+"/j_security_check"

    payload = "j_username="+username+"&j_password="+password
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

def get_inventory(serveraddress,session):

    print("Retrieving the inventory data from the vManage at "+serveraddress+"\n")

    url = "https://" + serveraddress + "/dataservice/device"
    response = session.request("GET",url,verify=False,timeout=10)
    json_string = response.json()
    #print(json_string)
    
    for item in json_string['data']:
       print(item)
       print("=======================") 
    for item in json_string['data']:
       print (item['host-name']+"   "+item['board-serial']+"   "+item['version']+"   "+item['controlConnections']+"   "+item['state']+"   "+item['personality']+"   "+item['system-ip'])

    #for item in json_string['data']:
        #system_ip=item['system-ip']
        #print('{0:15}  {1:20}  {2}     {3:36}  '.format("System IP", "Hostname", "Version","UUID"))
        #print('{0:15}  {1:20}  {2}     {3:36}  '.format("---------", "--------", "-------","------------------------------------"))
        #print ('{0:15}  {1:20}  {2}      {3:36}  '.format(item['system-ip'],item['host-name'],item['version'],item['uuid']))

def get_statistic(serveraddress,session):
    print("---------------------------------------------------------------------")
    print("Retrieving the statistic data from the vManage at "+serveraddress)
    print("---------------------------------------------------------------------")

    url = "https://" + serveraddress + "/dataservice/device"
    response = session.request("GET",url,verify=False,timeout=10)
    json_string = response.json()

    for item in json_string['data']:
        system_ip=item['system-ip']
        print('{0:15}  {1:20}  {2}     {3:36}  '.format("System IP", "Hostname", "Version","UUID"))
        print('{0:15}  {1:20}  {2}     {3:36}  '.format("---------", "--------", "-------","------------------------------------"))
        print ('{0:15}  {1:20}  {2}      {3:36}  '.format(item['system-ip'],item['host-name'],item['version'],item['uuid']))

        print ("Retrieving Statistics for "+system_ip)
        url = "https://"+serveraddress+"/dataservice/device/interface/stats?deviceId="+system_ip
        response = session.request("GET", url,verify=False)
        json_string=response.json()
        rx=0
        tx=0
        #print(json_string)
        for stats in json_string['data']:
             # We only want to print the ipv4 interfaces
            if stats['af-type']!='ipv6':
                 print('      {0:9}     {1:10}   {2:10d}      {3:10d}'.format(stats['ifname'],stats['vpn-id'],int(stats['tx-packets']),int(stats['rx-packets'])))
            rx=rx+int(stats['rx-packets'])
            tx=tx+int(stats['tx-packets'])
        print('                                 {0}      {1}'.format("----------","----------"))
        print('      {0:9}     {1:10}   {2:10d}      {3:10d}'.format(" ","Total",tx,rx))
    print ("\n")
        


# Open up the configuration file and get all application defaults
try:
    config = configparser.ConfigParser()
    config.read('package_config.ini')
    serveraddress = config.get("application","serveraddress")
    username = config.get("application","username")
    password = config.get("application","password")
    systemip = config.get("application","systemip")
except configparser.Error:
    print ("Cannot Parse package_config.ini")
    exit(-1)
    
print ("Viptela Configuration:")
print ("vManage Server Address: "+serveraddress)
print ("vManage Username: "+username)

session=initalize_connection(serveraddress,username,password)
if session != False:
    print ("Successful you will issue API commands here in later labs")
    get_inventory(serveraddress,session)
    get_statistic(serveraddress,session)
