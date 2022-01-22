import datetime
import os
import uuid

from fastapi import APIRouter, Request
from pymongo import MongoClient

from cloud_album_api.anniversary import Anniversary


mongo_username = os.environ['MONGO_USERNAME']
mongo_password = os.environ['MONGO_PASSWORD']
mongo_client = MongoClient(f'mongodb://{mongo_username}:{mongo_password}@cloud-album-mongo')
anniversaries_collection = mongo_client.cloud_album.anniversaries


router = APIRouter()


@router.get('')
async def get_anniversaries():
    global anniversaries_collection

    anniversaries = list(anniversaries_collection.find())
    return {
        'anniversaries': [
            Anniversary.from_dict(anniversary)
            for anniversary in anniversaries
        ],
    }


@router.post('')
async def create_new_anniversary(req: Request):
    global anniversaries_collection

    body = await req.json()
    new_anniversary = Anniversary(
        id=str(uuid.uuid4()),
        title=body.get('title', ''),
        date=datetime.datetime.strptime(
            body.get('date', ''), '%Y-%m-%d %H:%M:%S'),
        type=body.get('type', ''),
    )
    anniversaries_collection.insert_one(new_anniversary.to_dict())

    return {
        'id': new_anniversary.id,
    }


@router.delete('/{anniversary_id}', status_code=204)
async def delete_anniversary(anniversary_id: str):
    global anniversaries_collection

    anniversaries_collection.delete_one({ 'id': anniversary_id })
