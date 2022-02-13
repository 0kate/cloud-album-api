import uuid

from fastapi import APIRouter, Request

from cloud_album_api.models import Memo
from cloud_album_api.repositories import Memos


router = APIRouter()


@router.get('')
async def get_memos():
    memos = Memos.list()
    return {
        'memos': memos,
    }


@router.post('')
async def create_new_memo(req: Request):
    body = await req.json()
    new_memo = Memo(
        id=str(uuid.uuid4()),
        title=body.get('title', ''),
        is_list=body.get('isList', False),
        parent=body.get('parent'),
    )
    Memos.new(new_memo)

    return {
        'id': new_memo.id,
    }


@router.get('/{parent_id}')
async def get_child_memos(parent_id: str):
    child_memos = Memos.list(parent=parent_id)
    return {
        'memos': child_memos,
    }


@router.delete('/{memo_id}', status_code=204)
async def delete_memo(memo_id: str):
    Memos.delete(memo_id)


@router.put('/{memo_id}', status_code=200)
async def update_memo(memo_id: str, req: Request):
    body = await req.json()
    new_memo = Memo(
        id=memo_id,
        title=body.get('title', ''),
        done=body.get('done', False),
        is_list=body.get('isList', False),
        parent=body.get('parent'),
    )
    Memos.update(new_memo)
