import requests
import sys
import time
import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
 
 
class rest_api_lib:
    def __init__(self, vmanage_ip, username, password):
        self.vmanage_ip = "1.4.28.28"
        self.username = "admin"
        self.password = "admin"
        self.session = {}
        self.login(self.vmanage_ip, username, password)
 
    def login(self, vmanage_ip, username, password):
        base_url_str = 'https://%s/'%vmanage_ip
        login_action = '/j_security_check'
        login_data = {'j_username' : username, 'j_password' : password}
        login_url = base_url_str + login_action
        url = base_url_str + login_url
        sess = requests.session()
        login_response = sess.post(url=login_url, data=login_data, verify=False)
        self.session[vmanage_ip] = sess
 
        policy_id = "PUT_YOUR_POLICY_ID_HERE"
        activate_policy_url = "https://%s/dataservice/template/policy/vsmart/activate/PUT_YOUR_POLICY_ID_HERE"%(self.vmanage_ip)
        deactivate_policy_url = "https://%s/dataservice/template/policy/vsmart/deactivate/PUT_YOUR_POLICY_ID_HERE"%(self.vmanage_ip)
        payload = "{\n }"
        headers = {'Content-Type':'application/json'}
        i=0
        while i<5:
            i+=1
            response = self.session[self.vmanage_ip].post(url=activate_policy_url, data=payload, headers=headers, verify=False)
            data = response.content
            print (data)
            t = datetime.datetime.now()
            print ("Policy Activated @ %s "%t)
            time.sleep(100)
 
            response = self.session[self.vmanage_ip].post(url=deactivate_policy_url, data=payload, headers=headers, verify=False)
            data = response.content
            print (data)
            t = datetime.datetime.now()
            print ("Policy Deactivated @ %s "%t)
            time.sleep(100)
 
 
def main():
    vmanage_ip,username,password = "1.4.28.28","admin","admin"
    obj = rest_api_lib(vmanage_ip, username, password)
 
if __name__ == "__main__":
    sys.exit(main())
