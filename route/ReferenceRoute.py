from fastapi import APIRouter, Header

from common.db.conn import conn

router = APIRouter()

@router.get("/{task_id}")
async def get_task(tenant_id: str, task_id: str):
    res = conn.methods['read']( tenant_id, "task", condition = {
        "id": task_id,
    })

    task = res['data'][0]

    node_id = task['node_id']

    res = conn.methods['read']( tenant_id, "node", condition = {
        "id": node_id
    })

    node = res['data'][0]

    routing_id = node['routing_id']

    res = conn.methods['read']( tenant_id, "file", condition = {
        "tag1": routing_id,
        "location": "routing"
    })

    return res