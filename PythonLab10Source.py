def get_user_sys_id(snow_user):

    # find the ServiceNow user_id for the specified user

    url = snow_url + 'table/sys_user?sysparm_limit=1'
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
               'comments': (comment + ', \nIncident created using APIs by caller ' + snow_user),
               'caller_id': caller_sys_id,
               'urgency': severity
               }
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(url, auth=(snow_user, snow_pass), data=json.dumps(payload), headers=headers)
    incident_json = response.json()
    return incident_json['result']['number']
