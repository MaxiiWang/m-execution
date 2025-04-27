import httpx
import json
import requests

from config import Config

from common.utility.Global import G


async def write_to_iDOP(tenant_id, token, table, data:dict):
    if not token:
        raise Exception("token is None")
    
    app_id = G.get_app_id()
    table = G.get_tag_by_name(table)
    
    url = Config.ids3_server_url + "api/fabric/secondaryDikube/save"
    
    headers = {
        'appId': app_id,
        'Tenant-Id': tenant_id,
        'Authorization': token,
    }

    filter_data = {k: v for k, v in data.items() if v is not None}

    print("\n===============Adding data to iDOP=================")
    print("target: ", table)
    print("data: ", filter_data)

    payload = {
        "table": table,
        "data": filter_data
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=10.0)

    print("response: ", response.text)
    print("===================================================")

    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": response.text
        }

async def read_from_iDOP(tenant_id, token, table, columns = None, condition=None, page_number=None, page_size=None, order_by=None, desc=False, complex_condition=None):
    if not token:
        raise Exception("token is None")
        
    app_id = G.get_app_id()
    table = G.get_tag_by_name(table)
    
    url = Config.ids3_server_url + "api/fabric/secondaryDikube/search"
    
    headers = {
        'appId': app_id,
        'Tenant-Id': tenant_id,
        'Authorization': token,
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

    if complex_condition:
        filter = filter + complex_condition
    
    data = {
        "table": table
    }

    if filter != []:
        data['filter'] = filter

    if order_by:
        data['order_by'] = [{
            "column_name": order_by,
            "type": "DESC" if desc else "ASC"
        }]

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

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data, timeout=10.0)

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
    
async def update_iDOP(tenant_id, token, table, data: dict, condition):
    if not token:
        raise Exception("token is None")
    
    app_id = G.get_app_id()
    table = G.get_tag_by_name(table)
    
    url = Config.ids3_server_url + "api/fabric/secondaryDikube/update"
    
    headers = {
        'appId': app_id,
        'Tenant-Id': tenant_id,
        'Authorization': token,
    }
    
    filter_conditions = [
        {
            "columnName": k,
            "condition": "=",
            "columnValue": v
        } for k, v in condition.items()
    ]

    new_data = {k: v for k, v in data.items() if v is not None}

    payload = {
        "table": table,
        "filter": filter_conditions,
        "data": new_data
    }

    print("\n===============Updating data in iDOP=================")
    print("headers: ", headers)
    print("payload: ", payload)

    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, json=payload)

    print("response: ", response.text)
    print("===================================================")
    
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": response.text
        }

async def delete_from_iDOP(tenant_id, token, table, condition):
    if not token:
        raise Exception("token is None")
    
    app_id = G.get_app_id()
    table = G.get_tag_by_name(table)

    headers = {
        'appId': app_id,
        'Tenant-Id': tenant_id,
        'Authorization': token,
    }

    url = Config.ids3_server_url + "api/fabric/secondaryDikube/delete"

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


async def get_schema(tenant_id):
    app_id = G.get_app_id()

    url = Config.ids3_server_url + "api/fabric/secondaryDikube"
    
    headers = {
        'appId': app_id,
        'Tenant-Id': tenant_id,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": response.text
        }