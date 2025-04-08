from fastapi import APIRouter, Header

from common.db.conn import conn

router = APIRouter()

@router.get("/{task_id}")
async def get_task(tenant_id: str, task_id: str, token: str = Header(None)):
    res = await conn.methods['read']( tenant_id, token, "task", condition = {
        "id": task_id,
    })

    task = res['data'][0]

    node_id = task['node_id']

    res = await conn.methods['read']( tenant_id, token, "node", condition = {
        "id": node_id
    })

    node = res['data'][0]

    routing_id = node['routing_id']

    res = await conn.methods['read']( tenant_id, token, "file", condition = {
        "tag1": routing_id,
        "location": "routing"
    })

    return res