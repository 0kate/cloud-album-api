import datetime
import uuid
from typing import Optional

from fastapi import APIRouter, Request, Query

from cloud_album_api.models import Anniversary
from cloud_album_api.repositories import Anniversaries


router = APIRouter()


@router.get('')
async def get_anniversaries(
        from_date: Optional[str] = Query(None, alias='from'),
        sort: Optional[str] = None):
    anniversaries = Anniversaries.list()

    if from_date is not None:
        from_datetime = datetime.datetime.strptime(from_date, '%Y-%m-%d')
        anniversaries = [
            anniversary
            for anniversary in anniversaries
            if anniversary.date >= from_datetime
        ]
    if sort:
        anniversaries.sort(key=lambda anniversary: anniversary.to_dict()[sort])

    return {
        'anniversaries': anniversaries,
    }


@router.post('')
async def create_new_anniversary(req: Request):
    body = await req.json()
    new_anniversary = Anniversary(
        id=str(uuid.uuid4()),
        title=body.get('title', ''),
        date=datetime.datetime.strptime(
            body.get('date', ''), '%Y-%m-%d %H:%M:%S'),
        type=body.get('type', ''),
    )
    Anniversaries.new(new_anniversary)

    return {
        'id': new_anniversary.id,
    }


@router.delete('/{anniversary_id}', status_code=204)
async def delete_anniversary(anniversary_id: str):
    Anniversaries.delete(anniversary_id)
