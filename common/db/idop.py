import requests

from config import Config

from common.utility.Global import G



def write_to_iDOP(tenant_id, table, data:dict):
    app_id = G.get_app_id()
    
    url = Config.DFOps_SERVER_URL + "api/fabric/secondaryDikube/save"
    
    headers = {
        'appId': app_id,
        'tenantId': tenant_id,
    }

    filter_data = {k: v for k, v in data.items() if v is not None}

    print("\n===============Adding data to iDOP=================")
    print("target: ", table)
    print("data: ", filter_data)
    payload = {
        "table": table,
        "data": filter_data
    }

    response = requests.post(url, headers=headers, json=payload)

    print("response: ", response.text)
    print("===================================================")

    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": response.text
        }

def read_from_iDOP(tenant_id, table, columns = None, condition=None, page_number=None, page_size=None, order_by=None, desc=False):
    app_id = G.get_app_id()
    
    url = Config.DFOps_SERVER_URL + "api/fabric/secondaryDikube/search"
    
    headers = {
        'appId': app_id,
        'tenantId': tenant_id,
    }

    filter = []

    if condition:
        for key, value in condition.items():
            if value and value != "null" and value != []:
                if type(value) == list:
                    filter.append({
                        "columnName": key,
                        "condition": "in",
                        "columnValue": value
                    })
                else:
                    filter.append({
                        "columnName": key,
                        "condition": "=",
                        "columnValue": value
                    })
    
    data = {
        "table": table
    }

    if filter != []:
        data['filter'] = filter

    if order_by:
        data['sorter'] = {
            "field": order_by,
            "order": "descend" if desc else "ascend"
        }

    if columns:
        data['query'] = columns

    if page_number:
        data['page_number'] = page_number
    if page_size:
        data['page_size'] = page_size

    import json

    print("\n===============Reading data from iDOP=================")
    print("target: ", json.dumps(headers))
    print("data: ", json.dumps(data))

    response = requests.post(url, headers=headers, json=data)

    res_data = response.text

    bracket_list = []
    bStarted = False
    index = -1

    for i in res_data:
        index += 1
        if i == "{":
            if not bStarted:
                bStarted = True
                bracket_list.append(i)
            else:
                if len(bracket_list) == 0:
                    res_data = res_data[:index]
                    break
                else:
                    bracket_list.append(i)
        elif i == "}":
            bracket_list.pop()

    try:
        res_data = json.loads(res_data)
    except:
        return {
            "code": 400,
            "error": res_data
        }

    print("response: ", response.text)
    print("===================================================")

        
    if response.status_code == 200:
        return {
            "code": res_data['code'],
            "data": res_data['data']['result'],
            "total": res_data['data']['total']
        }
    else:
        return {
            "code": 400,
            "error": response.text if response.text else "未知错误，请联系管理员"
        }
    
def update_iDOP(tenant_id, table, data: dict, condition):
    app_id = G.get_app_id()
    
    url = Config.DFOps_SERVER_URL + "api/fabric/secondaryDikube/update"
    
    headers = {
        'appId': app_id,
        'tenantId': tenant_id,
    }
    
    filter_conditions = [
        {
            "columnName": k,
            "condition": "=",
            "columnValue": v
        } for k, v in condition.items()
    ]
    
    payload = {
        "table": table,
        "filter": filter_conditions,
        "data": data
    }

    print("\n===============Updating data in iDOP=================")
    print("target: ", table)
    print("data: ", data)

    response = requests.put(url, headers=headers, json=payload)

    print("response: ", response.text)
    print("===================================================")
    
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": response.text
        }

def delete_from_iDOP(tenant_id, table, condition):
    app_id = G.get_app_id()

    headers = {
        'appId': app_id,
        'tenantId': tenant_id,
    }

    url = Config.DFOps_SERVER_URL + "api/fabric/secondaryDikube/delete"

    filter_conditions = [
        {
            "columnName": k,
            "condition": "=",
            "columnValue": v
        } for k, v in condition.items()
    ]

    payload = {
        "table": table,
        "filter": filter_conditions
    }

    response = requests.delete(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        return {
            "code": 400,
            "message": response.text
        }


def get_schema(tenant_id):
    app_id = G.get_app_id()

    url = Config.DFOps_SERVER_URL + "api/fabric/secondaryDikube"
    
    headers = {
        'appId': app_id,
        'tenantId': tenant_id,
    }
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": response.text
        }