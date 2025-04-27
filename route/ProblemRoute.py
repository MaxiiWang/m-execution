from fastapi import APIRouter, Header, Body
import uuid
from datetime import datetime

from common.db.conn import conn

router = APIRouter()

@router.get("/type")
async def get_problem_type(tenant_id: str, token: str = Header(None)):
    res = await conn.methods['read'](tenant_id, token, "problem_type")
    
    return res

@router.get("/")
async def get_problem(tenant_id: str, token: str = Header(None), id:str = None, task_id: str = None, status: str = None, user_id: str = None):
    print("id", id)
    if id:
        res = await conn.methods['read'](tenant_id, token, "problem", condition = {
            "id": id,
        })
        return res
    
    if task_id:
        if status:
            res = await conn.methods['read'](tenant_id, token, "problem", condition = {
                "task_id": task_id,
                "status": status,
                "if_block": True
            },
            order_by = 'created_at', desc= True)
        else:
            res = await conn.methods['read'](tenant_id, token, "problem", condition = {
                "task_id": task_id,
                "if_block": True
            },
            order_by = 'created_at', desc= True)
    else:
        if status:
            if user_id:
                res = await conn.methods['read'](tenant_id, token, "problem", condition = {
                    "status": status,
                    "user_id": user_id
                },
                order_by = 'created_at', desc= True)
            else:
                res = await conn.methods['read'](tenant_id, token, "problem", condition = {
                    "status": status
                },
                order_by = 'created_at', desc= True)
        else:
            if user_id:
                res = await conn.methods['read'](tenant_id, token, "problem", condition = {
                    "user_id": user_id
                },
                order_by = 'created_at', desc= True)
            else:
                res = await conn.methods['read'](tenant_id, token, "problem",
                order_by = 'created_at', desc= True)
    
    return res

@router.get("/photo")
async def get_problem_photo(tenant_id: str, token: str = Header(None), id:str = None, problem_id: str = None, status: str = None):
    if id:
        res = await conn.methods['read'](tenant_id, token, "file", condition = {
            "id": id,
        })
        return res
    
    if problem_id:
        if status:
            res = await conn.methods['read'](tenant_id, token, "file", condition = {
                "location": "problem",
                "tag2": problem_id,
                "tag1": status,
            })
            return res

        else:
            res = await conn.methods['read'](tenant_id, token, "file", condition = {
                "location": "problem",
                "tag2": problem_id,
            })
            return res

@router.post("/")
async def reportProblem(tenant_id: str, data: dict, token: str = Header(None)):
    photo_data_list = data.get('photos', None)

    data.pop('photos', None)

    from pytz import timezone

    tz = timezone('Asia/Shanghai')  # Replace 'Asia/Shanghai' with your desired timezone
    data['created_at'] = "TIMESTAMP " + datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

    if "status" not in data:
        data['status'] = "open"
    await conn.methods['write']( tenant_id, token, "problem", data = data)

    if data['if_block']:
        await conn.methods['update']( tenant_id, token, "task", condition = {
            "id": data['task_id']
        }, data = {
            'status': 'blocked'
        })

    if photo_data_list:
        for photo_data in photo_data_list:
            photo_data['id'] = str(uuid.uuid4().hex)
            await conn.methods['write'](tenant_id, token, "file", data=photo_data)

    log_data = {
        "id": str(uuid.uuid4().hex),
        "location": "execution",
        "user": data['user'],
        "user_id": data['user_id'],
        "tag1": data['task_id'],
        "tag2": "problem",
        "tag3": data['id'],
        "message": "上报生产问题：" + data['problem_type'],
        "created_at": "TIMESTAMP " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    await conn.methods['write']( tenant_id, token, "log", data = log_data)

    res = await conn.methods['read']( tenant_id, token, "analysis", condition = {
        "date": get_today_date_string()
    })

    # value = res['data'][0]['today_reported_problems']

    # await conn.methods['update']( tenant_id, token, "analysis", condition = {
    #     "date": get_today_date_string()
    # }, data = {
    #     'today_reported_problems': value + 1
    # })

    return {
        "status": "reported"
    }

@router.post("/resolve")
async def resolve_problem(tenant_id: str, problem_id: str, task_id: str, user: str, user_id: str, data: dict, token: str = Header(None)):
    photo_data_list = data.get('photos', None)
    
    data = {
        "status": "resolved",
        "resolved_user": user,
        "resolved_user_id": user_id,
        "resolved_at": "TIMESTAMP " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "resolved_description": data['resolved_description']
    }
    res = await conn.methods['update'](tenant_id, token, "problem", condition={"id": problem_id}, data=data)

    res = await conn.methods['read'](tenant_id, token, "problem", condition={"id": problem_id, "status": "open", "if_block": True})

    if len(res['data']) == 0:
        res = await conn.methods['update'](tenant_id, token, "task", condition={"id": task_id}, data={"status": "open"})
    
    if photo_data_list:
        for photo_data in photo_data_list:
            photo_data['id'] = str(uuid.uuid4().hex)
            await conn.methods['write'](tenant_id, token, "file", data=photo_data)
    
    return res

@router.get("/user")
async def get_problem_user(tenant_id: str, status: str, token: str = Header(None)):
    res = await conn.methods['read'](tenant_id, token, "problem", columns="distinct(user_id), user", condition = {
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


def get_today_date_string():
    date_str = datetime.now().strftime("%Y-%m-%d")
    return date_str

