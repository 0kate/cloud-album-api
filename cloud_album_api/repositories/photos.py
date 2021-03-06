import json
import os
from typing import List, Optional

from cloud_album_api.lib.cloud_storage import GoogleDrive
from cloud_album_api.models import Photo


root_file_id = os.environ['GOOGLE_DRIVE_ROOT_FILE_ID']
service_account_info = json.loads(os.environ['GOOGLE_DRIVE_SECRET'])


class Photos:
    gdrive = GoogleDrive(service_account_info, root_file_id)

    @classmethod
    async def list(cls, album_name: str) -> List[Photo]:
        photo_entries = await cls.gdrive.ls(f'/{album_name}')
        return [
            Photo(name=photo_entry.name)
            for photo_entry in photo_entries
            if photo_entry.name != 'thumbnail'
        ]

    @classmethod
    async def get_thumbnail(cls, album_name: str, photo_id: str) -> Optional[str]:
        link = await cls.gdrive.ln(f'/{album_name}/{photo_id}/thumbnail')
        return link

    @classmethod
    async def get_link(cls, album_name: str, photo_id: str) -> Optional[str]:
        link = await cls.gdrive.ln(f'/{album_name}/{photo_id}/{photo_id}')
        return link

    @classmethod
    async def suppress_thumbnail(cls, album_name: str, photo_id: str):
        await cls.gdrive.suppress_file(f'/{album_name}/{photo_id}/thumbnail')

    @classmethod
    async def suppress_photo(cls, album_name: str, photo_id: str):
        await cls.gdrive.suppress_file(f'/{album_name}/{photo_id}/{photo_id}')
