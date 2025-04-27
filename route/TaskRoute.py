from fastapi import APIRouter, Header
from datetime import datetime
import uuid

from common.db.conn import conn

router = APIRouter()

@router.get("/")
async def get_task(tenant_id: str, status: str=None, assignee_id: str=None, task_id: str=None, page: int=1, size: int=10, token: str = Header(None)):
    if task_id:
        res = await conn.methods['read']( tenant_id, token, "task", condition = {
            "id": task_id,
        })
        return res
    if status:
        if assignee_id:
            res = await conn.methods['read']( tenant_id, token, "task", condition = {
                "status": status,
                "assignee_id": assignee_id
            }, page_number = page, page_size = size, order_by = 'planned_end_time', desc= True)
        else:

            res = await conn.methods['read']( tenant_id, token, "task", page_number = page, page_size = size, condition = {
                "status": status
            }, order_by = 'planned_end_time', desc= True)
    else:
        if assignee_id:
            res = await conn.methods['read']( tenant_id, token, "task", condition = {
                "assignee_id": assignee_id
            }, page_number = page, page_size = size, order_by = 'planned_end_time', desc= True)
        else:
            res = await conn.methods['read']( tenant_id, token, "task", page_number = page, page_size = size, order_by = 'planned_end_time', desc= True)

    return res

@router.get("/progress")
async def get_task(tenant_id: str, assignee_id: str=None, page: int=1, size: int=10, token: str = Header(None)):
    res = await conn.methods['read']( tenant_id, token, "task", page_number = page, page_size = size, complex_condition = [{"columnName": "status", "condition": "in", "columnValue": ["open", "blocked"]}], order_by = 'planned_end_time', desc= True)

    return res

@router.get("/user")
async def get_task_users(tenant_id: str, status: str='open', token: str = Header(None)):
    res = await conn.methods['read']( tenant_id, token, "task", columns="distinct(assignee_id), assignee_nickname", condition = {
        "status": status
    })

    ret = {
        "data": [],
    }

    for key, value in res.items():
        if key != 'data':
            ret[key] = value

    for item in res['data']:
        if item['assignee_id']:
            ret['data'].append(item)
   
    return ret

@router.get("/examine")
async def get_after_check(tenant_id: str, status: str="open", page: int=1, page_size: int=10, token: str = Header(None), id: str=None):
    if id:
        res = await conn.methods['read'](tenant_id, token, "examine", condition = {
            "id": id,
        })
        return res
    
    if status:
        res = await conn.methods['read'](tenant_id, token, "examine", condition = {
            "status": status
        }, order_by = "created_at", desc = True, page_number = page, page_size = page_size)
        return res

    res = await conn.methods['read'](tenant_id, token, "examine", order_by = "created_at", desc = True, page_number = page, page_size = page_size)
    return res

@router.get("/examine/user")
async def get_after_check_users(tenant_id: str, status: str="open", page: int=1, page_size: int=10, token: str = Header(None)):
    res = await conn.methods['read'](tenant_id, token, "examine", columns="distinct(user_id), user", condition = {
        "status": status
    })

    ret = {
        "data": [],
    }

    for key, value in res.items():
        if key != 'data':
            ret[key] = value

    for item in res['data']:
        if item['user_id']:
            ret['data'].append(item)
   
    return ret

@router.get("/examine/photo")
async def get_after_check_photo(tenant_id: str, token: str = Header(None), id:str = None):
    if id:
        res = await conn.methods['read'](tenant_id, token, "file", condition = {
            "location": "task",
            "tag1": "examine",
            "tag2": id
        })
        return res
    
    res = await conn.methods['read'](tenant_id, token, "file", condition = {
        "location": "examine"
    })
    return res

@router.post("/exam")
async def create_examine(tenant_id: str, examine: dict, token: str = Header(None)):
    photo_data_list = examine.get('photos', None)

    examine.pop('photos', None)

    print(examine)
    id = examine.pop('examine_id')
    examine['examined_at'] = "TIMESTAMP " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    examine['status'] = "checked"

    res = await conn.methods['update'](tenant_id, token, "examine", condition={"id": id}, data = examine)

    if photo_data_list:
        for photo_data in photo_data_list:
            photo_data['id'] = str(uuid.uuid4().hex)
            await conn.methods['write'](tenant_id, token, "file", data=photo_data)

    return res