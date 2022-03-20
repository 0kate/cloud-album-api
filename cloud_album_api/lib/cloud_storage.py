import asyncio
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

    def is_directory(self) -> bool:
        return self.type == DEntryType.DIRECTORY


class CloudStorage(metaclass=ABCMeta):
    @abstractmethod
    async def ls(self, path: str) -> List[DEntry]:
        ...

    @abstractmethod
    async def cat(self, path: str) -> Optional[bytes]:
        ...


class GoogleDrive(CloudStorage):
    def __init__(self, service_account_info: dict, root_file_id: str):
        cred = Credentials.from_service_account_info(service_account_info)
        self._gdrive = discovery.build('drive', 'v3', credentials=cred)
        self._root_file_id = root_file_id

    async def ls(self, path: str) -> List[DEntry]:
        loop = asyncio.get_event_loop()
        target_file_id = await self._resolve_path(path)
        files = []
        if target_file_id is not None:
            query = self._gdrive.files().list(q=f'"{target_file_id}" in parents')
            response = await loop.run_in_executor(None, query.execute)
            files = response.get('files', [])
        return [
            DEntry(
                type=DEntryType.DIRECTORY if f.get('mimeType', '') == 'application/vnd.google-apps.folder' else DEntryType.FILE,
                name=f.get('name', 'unknown'),
            )
            for f in files
        ]

    async def cat(self, path: str) -> Optional[bytes]:
        loop = asyncio.get_event_loop()
        target_file_id = await self._resolve_path(path)
        content = None
        if target_file_id is not None:
            request = self._gdrive.files().get_media(fileId=target_file_id)
            _, content = await loop.run_in_executor(None, request.http.request, request.uri, request.method)
        return content

    async def ln(self, path: str) -> Optional[str]:
        loop = asyncio.get_event_loop()
        target_file_id = await self._resolve_path(path)
        link = None
        if target_file_id is not None:
            request = self._gdrive.files().get(fileId=target_file_id, fields='webContentLink')
            file_data = await loop.run_in_executor(None, request.execute)

            request = self._gdrive.permissions().create(
                fileId=target_file_id,
                body={
                    'type': 'anyone',
                    'role': 'reader',
                },
                fields='id',
            )
            await loop.run_in_executor(None, request.execute)
            link = file_data['webContentLink']
        return link

    async def suppress_file(self, path: str):
        target_file_id = await self._resolve_path(path)
        request = self._gdrive.permissions().delete(fileId=target_file_id, permissionId='anyoneWithLink')
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, request.execute)

    async def _resolve_path(self, path: str) -> Optional[str]:
        loop = asyncio.get_event_loop()
        file_id = self._root_file_id
        entry_names = iter([name for name in path.split('/') if len(name) > 0])
        while True:
            query = self._gdrive.files().list(q=f'"{file_id}" in parents')
            response = await loop.run_in_executor(None, query.execute)
            files = response.get('files', [])

            try:
                next_entry = None
                target_entry_name = next(entry_names)
                for f in files:
                    if target_entry_name == f.get('name', ''):
                        next_entry = f
                        break
                if next_entry is None:
                    break
                file_id = next_entry.get('id', None)
                if next_entry.get('mimeType', '') != 'application/vnd.google-apps.folder':
                    break
            except StopIteration:
                break
        return file_id
