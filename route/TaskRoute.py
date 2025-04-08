from fastapi import APIRouter, Header

from common.db.conn import conn

router = APIRouter()

@router.get("/")
async def get_task(tenant_id: str, assignee_id: str=None, task_id: str=None, status: str='open', page: int=1, size: int=10, token: str = Header(None)):
    if task_id:
        res = await conn.methods['read']( tenant_id, token, "task", condition = {
            "id": task_id,
        })
    else:
        if status == 'ALL':
            res = await conn.methods['read']( tenant_id, token, "task", page_number = page, page_size = size, condition = {
                "assignee_id": assignee_id
            })
        elif status == 'open':
            res = await conn.methods['read']( tenant_id, token, "task", condition = {
                # "status": "open",
                "assignee_id": assignee_id
            }, page_number = page, page_size = size)

    return res