import json
import os
from typing import List, Optional

from cloud_album_api.lib.cloud_storage import GoogleDrive
from cloud_album_api.models import Album


root_file_id = os.environ['GOOGLE_DRIVE_ROOT_FILE_ID']
service_account_info = json.loads(os.environ['GOOGLE_DRIVE_SECRET'])


class Albums:
    gdrive = GoogleDrive(service_account_info, root_file_id)

    @classmethod
    async def list(cls) -> List[Album]:
        entries = await cls.gdrive.ls('/')
        return [Album(entry.name) for entry in entries if entry.is_directory()]

    @classmethod
    async def get_thumbnail(cls, album_name: str) -> Optional[bytes]:
        content = await cls.gdrive.cat(f'/{album_name}/thumbnail')
        return content
