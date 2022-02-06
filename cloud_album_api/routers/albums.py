import asyncio
import base64
import json
import os

from fastapi import APIRouter, Request

from cloud_album_api.cloud_storage import GoogleDrive


root_file_id = os.environ['GOOGLE_DRIVE_ROOT_FILE_ID']
service_account_info = json.loads(os.environ['GOOGLE_DRIVE_SECRET'])
gdrive = GoogleDrive(service_account_info, root_file_id)


router = APIRouter()


@router.get('')
async def get_albums():
    global gdrive

    entries = await gdrive.ls('/')
    return {
        'albums': [
            { 'name': entry.name }
            for entry in entries
            if entry.is_directory()
        ],
    }


@router.get('/{album_name}/thumbnail')
async def get_album_thumbnail(album_name: str):
    global gdrive

    content = await gdrive.cat(f'/{album_name}/thumbnail')
    if content is not None:
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, base64.b64encode, content)

    return {
        'albumName': album_name,
        'imageName': 'thumbnail',
        'content': content,
    }


@router.get('/{album_name}/photos')
async def get_photos(album_name: str):
    global gdrive

    images = await gdrive.ls(f'/{album_name}')

    return {
        'albumName': album_name,
        'images': [
            { 'name': image.name }
            for image in images
            if image.name != 'thumbnail'
        ],
    }


@router.get('/{album_name}/photos/{photo_id}/thumbnail')
async def get_photo_thumbnail(album_name: str, photo_id: str):
    global gdrive

    content = await gdrive.cat(f'/{album_name}/{photo_id}/thumbnail')
    if content is not None:
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, base64.b64encode, content)

    return {
        'albumName': album_name,
        'imageName': f'{photo_id}/thumbnail',
        'content': content,
    }


@router.get('/{album_name}/photos/{photo_id}/content')
async def get_photo_content(album_name: str, photo_id: str):
    global gdrive

    content = await gdrive.cat(f'/{album_name}/{photo_id}/{photo_id}')
    if content is not None:
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, base64.b64encode, content)

    return {
        'albumName': album_name,
        'imageName': f'{photo_id}',
        'content': content,
    }


@router.get('/{album_name}/{image_name}')
async def get_image_content(album_name: str, image_name: str):
    global gdrive

    content = await gdrive.cat(f'/{album_name}/{image_name}')
    if content is not None:
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, base64.b64encode, content)

    return {
        'albumName': album_name,
        'imageName': image_name,
        'content': content,
    }

