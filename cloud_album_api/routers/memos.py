import os
import uuid

from fastapi import APIRouter, Request
from pymongo import MongoClient

from cloud_album_api.memo import Memo


mongo_username = os.environ['MONGO_USERNAME']
mongo_password = os.environ['MONGO_PASSWORD']
mongo_client = MongoClient(f'mongodb://{mongo_username}:{mongo_password}@cloud-album-mongo')
memos_collection = mongo_client.cloud_album.memos


router = APIRouter()


@router.get('')
async def get_memos():
    global memos_collection

    memos = list(memos_collection.find({'parent': None}))
    return {
        'memos': [
            Memo.from_dict(memo).to_dict()
            for memo in memos
        ],
    }


@router.post('')
async def create_new_memo(req: Request):
    global memos_collection

    body = await req.json()
    new_memo = Memo(
        id=str(uuid.uuid4()),
        title=body.get('title', ''),
        is_list=body.get('isList', False),
        parent=body.get('parent'),
    )
    memos_collection.insert_one(new_memo.to_dict())

    return {
        'id': new_memo.id,
    }


@router.get('/{parent_id}')
async def get_child_memos(parent_id: str):
    global memos_collection

    child_memos = list(memos_collection.find({ 'parent': parent_id }))
    return {
        'memos': [
            Memo.from_dict(memo).to_dict()
            for memo in child_memos
        ],
    }


@router.delete('/{memo_id}', status_code=204)
async def delete_memo(memo_id: str):
    global memos_collection

    memos_collection.delete_one({ 'id': memo_id })


@router.put('/{memo_id}', status_code=200)
async def update_memo(memo_id: str, req: Request):
    global memos_collection

    body = await req.json()
    memos_collection.update_one(
        { 'id': memo_id },
        {
            '$set': {
                'title': body.get('title', ''),
                'done': body.get('done', False),
                'isList': body.get('isList', False),
                'parent': body.get('parent'),
            },
        },
    )
