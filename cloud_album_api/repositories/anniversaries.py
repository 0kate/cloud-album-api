import os
from typing import List

from pymongo import MongoClient

from cloud_album_api.models import Anniversary


mongo_username = os.environ['MONGO_USERNAME']
mongo_password = os.environ['MONGO_PASSWORD']
mongo_client = MongoClient(f'mongodb://{mongo_username}:{mongo_password}@cloud-album-mongo')


class Anniversaries:
    collection = mongo_client.cloud_album.anniversaries

    @classmethod
    def list(cls) -> List[Anniversary]:
        anniversary_dicts = list(cls.collection.find())
        return [
            Anniversary.from_dict(anniversary_dict)
            for anniversary_dict in anniversary_dicts
        ]

    @classmethod
    def new(cls, new_anniversary: Anniversary):
        cls.collection.insert_one(new_anniversary.to_dict())

    @classmethod
    def delete(cls, anniversary_id: str):
        cls.collection.delete_one({'id': anniversary_id})
