from fastapi import APIRouter, Header, HTTPException
import requests
from datetime import datetime, timedelta
import uuid

from common.db.conn import conn

router = APIRouter()

async def loginAndFetch(tenant_id, auth: dict, token: str = Header(None)):
    ret = {}
    url = "https://idfops-gateway.data4industry.com:30843/api/user/login"

    headers = {
        "tenant-id": tenant_id
    }

    username = auth.get("username")
    password = auth.get("password")

    payload = {
        "username": username,
        "password": password,
        "appId": "ea3574a4062f4e15af9fe31a1e6add79"
    }
    res = requests.post(url, headers=headers, json=payload).json()

    if res['code'] != 200:
        raise HTTPException(status_code=res['code'], detail=res['message'])
    else:
        ret['code'] = 200
        ret['data'] = res['data']
        url = "https://idfops-gateway.data4industry.com:30843/api/user/info"

        headers = {
            "Authorization": res['data']
        }

        res = requests.get(url, headers=headers).json()

        ret['user'] = res['data']

        return ret

@router.post("/login")
async def login(tenant_id, auth: dict, token: str = Header(None)):
    '''
    
    res = {
        "user": {
            ...
        },
        "roles": ["超级管理员"],
        "permissions": [
            { "moduleId": "order-management", "read": true, "write": true },
            { "moduleId": "routing-management", "read": true, "write": true },
            { "moduleId": "ticket-management", "read": true, "write": true },
            { "moduleId": "production-monitor", "read": true, "write": false }
        ],
    }
    '''
    ret = await loginAndFetch(tenant_id, auth)

    user_id = ret['user']['id']
    token = ret['data']
        
    res = await conn.methods['read'](tenant_id, token, "user_roles", condition = {"user_id": user_id})
    ret['roles'] = [role['role'] for role in res['data']]

    ret['permissions'] = []

    for user_role in res['data']:
        role_id = user_role['role_id']
        res = await conn.methods['read'](tenant_id, token, "role_permissions", condition = {"role_id": role_id})
        print("res['data']: ", res['data'])
        ret['permissions'] += res['data']

    return ret


def fetchUsers(page: int = 1, size: int = 10, authorization: str = Header(None)):

    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    url = 'https://idfops-gateway.data4industry.com:30843/api/user/group/list'
    headers = {
        'Authorization': authorization,
    }
    params = {
        "page": page,
        "size": size,
    }
    payload = {
        "page": page,
        "size": size,
        "all": True
    }
    
    response = requests.get(url, headers=headers, json=payload, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


@router.get("/")
async def getUsers(page: int = 1, size: int = 10, token: str = Header(None)):
    return fetchUsers(page, size, token)
    
    
@router.get("/job_count")
async def getJobCount(tenant_id, start_date: str, end_date: str, role: str = None, authorization: str = Header(None), token: str = Header(None)):
    users = fetchUsers(authorization=authorization)

    def generate_date_range(start_date, end_date):
        start = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        end = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        date_array = [(start + timedelta(days=x)).strftime("%Y-%m-%d") for x in range((end - start).days + 1)]
        return date_array

    date_array = generate_date_range(start_date, end_date)
    print(date_array)

    print(start_date, end_date, role)

@router.get("/roles")
async def getRoles(tenant_id, token: str = Header(None)):
    res = await conn.methods['read'](tenant_id, token, "roles")

    return res

@router.get("/permissions")
async def getPermissions(tenant_id, token: str = Header(None)):
    res = await conn.methods['read'](tenant_id, token, "permission")

    return res

@router.get("/user_roles")
async def getUserRoles(tenant_id: str, page: int = 1, size: int = 10, token: str = Header(None)):
    users = fetchUsers(page, size, token)

    for user in users['data']['list']:
        user_id = user['id']
        # print("user_id: ", user_id)
        res = await conn.methods['read'](tenant_id, token, "user_roles", condition = {"user_id": user_id})
        user['roles'] = res['data']
        user['role_str'] = ",".join([role['role'] for role in res['data']])

    return users

@router.get("/role_permissions")
async def getRolePermissions(tenant_id: str, role_id: str, token: str = Header(None)):
    res = await conn.methods['read'](tenant_id, token, "role_permissions", condition = {"role_id": role_id})

    return res
