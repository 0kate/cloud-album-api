from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

from google.oauth2.service_account import Credentials
from googleapiclient import discovery


class DEntryType(Enum):
    FILE = auto()
    DIRECTORY = auto()


@dataclass
class DEntry:
    type: DEntryType
    name: str


class CloudStorage(metaclass=ABCMeta):
    @abstractmethod
    async def ls(self, path: str) -> List[DEntry]:
        ...


class GoogleDrive(CloudStorage):
    def __init__(self, service_account_info: dict, root_file_id: str):
        cred = Credentials.from_service_account_info(service_account_info)
        self._gdrive = discovery.build('drive', 'v3', credentials=cred)
        self._root_file_id = root_file_id

    async def ls(self, path: str) -> List[DEntry]:
        response = self._gdrive.files().list(q=f'"{self._root_file_id}" in parents').execute()
        print(response['files'])
        return [
            DEntry(
                type=DEntryType.DIRECTORY if f.get('mimeType', '') == 'application/vnd.google-apps.folder' else DEntryType.FILE,
                name=f.get('name', 'unknown'),
            )
            for f in response.get('files', [])
        ]

    async def cat(self, path: str) -> Optional[bytes]:
        entry_names = iter([name for name in path.split('/') if len(name) > 0])
        parent_file_id = self._root_file_id

        target_entry_name = next(entry_names)
        content = None
        while True:
            response = self._gdrive.files().list(q=f'"{parent_file_id}" in parents').execute()
            files = response.get('files', [])
            entry_name_id_map = {
                f.get('name', 'unknown'): f.get('id', '')
                for f in files
            }
            if target_entry_name not in entry_name_id_map:
                break
            next_file_id = entry_name_id_map[target_entry_name]
            if len(files) == 1:
                request = self._gdrive.files().get_media(fileId=files[0]['id'])
                response, content = request.http.request(request.uri, request.method)
                break
            target_entry_name = next(entry_names)
            parent_file_id = next_file_id
        return content