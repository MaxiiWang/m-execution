from fastapi import APIRouter
import uuid
from datetime import datetime

from common.db.conn import conn

router = APIRouter()

@router.get("/steps")
async def getSteps(tenant_id: str, task_id: str):
    res = conn.methods['read']( tenant_id, "task", condition = {
       "id": task_id
    })

    task = res['data'][0]

    res = conn.methods['read']( tenant_id, "step", condition = {
        "node_id": task['node_id']
    })
    return res

@router.post("/finish_once")
async def finishOnce(tenant_id: str, user_id: str, user: str, task_id: str):
    res = conn.methods['read']( tenant_id, "task", condition = {
        "id": task_id
    })

    current = res['data'][0]['current']

    print("current: ", current)
    print("total: ", res['data'][0]['total'])


    conn.methods['update']( tenant_id, "task", condition = {
        "id": task_id
    }, data = {
        "current": current + 1
    })

    conn.methods['write']( tenant_id, "log", data = {
        "id": str(uuid.uuid4().hex),
        "location": "execution",
        "user": user,
        "user_id": user_id,
        "tag1": task_id,
        "tag2": "finish_once",
        "message": "完成了一次生产",
        "created_at": "TIMESTAMP " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    if current + 1 >= res['data'][0]['total']:
        await finish(tenant_id, user_id, user, task_id, res['data'][0]['node_id'])
    
    return res

async def finish(tenant_id: str, user_id: str, user: str, task_id: str, node_id: str):

    conn.methods['update']( tenant_id, "task", condition = {
        "id": task_id
    }, data = {
        "status": "finished"
    })

    conn.methods['write']( tenant_id, "log", data = {
        "id": str(uuid.uuid4().hex),
        "location": "execution",
        "user": user,
        "user_id": user_id,
        "tag1": task_id,
        "tag2": "finish",
        "message": "完成了生产任务",
        "created_at": "TIMESTAMP " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    key_name = get_current_key_name()

    res = conn.methods['read']( tenant_id, "analysis", condition = {
        "date": get_today_date_string()
    })

    value = res['data'][0][key_name]

    conn.methods['update']( tenant_id, "analysis", condition = {
        "date": get_today_date_string()
    }, data = {
        key_name: value + 1
    })

    node = conn.methods['read']( tenant_id, "node", condition = {
        "id": node_id
    })['data'][0]

    print("node: ", node)
    b_if_need_after_check = node['b_need_after_check']

    if b_if_need_after_check:
        conn.methods['write']( tenant_id, "examine", data = {
            "id": str(uuid.uuid4().hex),
            "task_id": task_id,
            "user_id": user_id,
            "user": user,
            "status": "open",
            "created_at": "TIMESTAMP " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    return res

@router.post("/start")
async def start(tenant_id: str, user_id: str, task_id: str):
    res = conn.methods['read']( tenant_id, "task", condition = {
        "id": task_id
    })

    print(res)

    if res['data'][0]['actual_start_time']:
        return {
            "status": "running"
        }
        
    conn.methods['update']( tenant_id, "task", condition = {
        "id": task_id
    }, data = {
        "actual_start_time": "TIMESTAMP " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    conn.methods['write']( tenant_id, "log", data = {
        "id": str(uuid.uuid4().hex),
        "location": "task",
        "user": user_id,
        "tag1": task_id,
        "tag2": "start",
        "message": "开始执行任务",
        "created_at": "TIMESTAMP " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    return {
        "status": "running"
    }

@router.get("/problem_types")
async def getProblemTypes(tenant_id: str):
    res = conn.methods['read']( tenant_id, "app_config", condition = {
        "name": "problem_types"
    })

    res['data'] = res['data'][0]['value'][1:-1].split(',')
    return res

@router.post("/problem")
async def reportProblem(tenant_id: str, data: dict):
    print(data)
    data['id'] = str(uuid.uuid4().hex)
    data['created_at'] = "TIMESTAMP " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if "status" not in data:
        data['status'] = "open"
    conn.methods['write']( tenant_id, "problem", data = data)

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

    conn.methods['write']( tenant_id, "log", data = log_data)

    res = conn.methods['read']( tenant_id, "analysis", condition = {
        "date": get_today_date_string()
    })

    value = res['data'][0]['today_reported_problems']

    conn.methods['update']( tenant_id, "analysis", condition = {
        "date": get_today_date_string()
    }, data = {
        'today_reported_problems': value + 1
    })

    return {
        "status": "reported"
    }

@router.get("/record_time")
async def record_time(tenant_id, time):
    time = int(time)
    date = get_today_date_string()
    res = conn.methods['read']( tenant_id, "analysis", condition = {
        "date": date
    })

    today_worktime = res['data'][0]['today_worktime']

    conn.methods['update']( tenant_id, "analysis", condition = {
        "date": date
    }, data = {
        "today_worktime": today_worktime + time
    })

def get_today_date_string():
    date_str = datetime.now().strftime("%Y-%m-%d")
    return date_str

def get_current_key_name():
    current_hour = datetime.now().hour

    if current_hour < 2:
        return "tickets_finished_by_two"
    elif current_hour < 4:
        return "tickets_finished_by_four"
    elif current_hour < 6:
        return "tickets_finished_by_six"
    elif current_hour < 8:
        return "tickets_finished_by_eight"
    elif current_hour < 10:
        return "tickets_finished_by_ten"
    elif current_hour < 12:
        return "tickets_finished_by_twelve"
    elif current_hour < 14:
        return "tickets_finished_by_fourteen"
    elif current_hour < 16:
        return "tickets_finished_by_sixteen"
    elif current_hour < 18:
        return "tickets_finished_by_eighteen"
    elif current_hour < 20:
        return "tickets_finished_by_twenty"
    elif current_hour < 22:
        return "tickets_finished_by_twenty_two"
    elif current_hour < 24:
        return "tickets_finished_by_twenty_four"
    else:
        return "tickets_finished_by_two"