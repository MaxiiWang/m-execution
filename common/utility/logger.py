from common.utility import Global as G
from common.db import conn

# data = [{
    #     "location": "order",
    #     "user": user_id,
    #     "tag1": result['data'],
    #     "tag2": "order",
    #     "tag3": "add",
    #     "message": "新增订单"
    # }]

async def take_logs(tenant_id, data_list):
    for data in data_list:
        take_log(tenant_id, data)

def take_log(tenant_id, data):
    conn.methods['write'](tenant_id, "log", data=data)
