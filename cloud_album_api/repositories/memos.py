import os
from typing import List, Optional

from pymongo import MongoClient

from cloud_album_api.models import Memo


mongo_username = os.environ['MONGO_USERNAME']
mongo_password = os.environ['MONGO_PASSWORD']
mongo_host = os.environ['MONGO_HOST']
mongo_scheme = os.environ['MONGO_SCHEME']
mongo_client = MongoClient(f'{mongo_scheme}://{mongo_username}:{mongo_password}@{mongo_host}')


class Memos:
    collection = memos_collection = mongo_client.cloud_album.memos

    @classmethod
    def list(cls, parent: Optional[str] = None) -> List[Memo]:
        memo_dicts = list(cls.collection.find({'parent': parent}))
        return [
            Memo.from_dict(memo_dict)
            for memo_dict in memo_dicts
        ]

    @classmethod
    def new(cls, new_memo: Memo):
        cls.collection.insert_one(new_memo.to_dict())

    @classmethod
    def delete(cls, memo_id: str):
        cls.collection.delete_one({'id': memo_id})

    @classmethod
    def update(cls, new_memo: Memo):
        cls.collection.update_one(
            {'id': new_memo.id},
            {
                '$set': {
                    'title': new_memo.title,
                    'done': new_memo.done,
                    'isList': new_memo.is_list,
                    'parent': new_memo.parent,
                },
            },
        )
