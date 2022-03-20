import asyncio
import base64

from fastapi import APIRouter

from cloud_album_api.repositories import Albums, Photos


router = APIRouter()


@router.get('')
async def get_albums():
    albums = await Albums.list()
    return {
        'albums': [
            album.to_dict()
            for album in albums
        ],
    }


@router.get('/{album_name}/thumbnail')
async def get_album_thumbnail(album_name: str):
    content = await Albums.get_thumbnail(album_name)
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
    photos = await Photos.list(album_name)

    return {
        'albumName': album_name,
        'images': [photo.to_dict() for photo in photos],
    }


@router.get('/{album_name}/photos/{photo_id}/thumbnail')
async def get_photo_thumbnail(album_name: str, photo_id: str):
    link = await Photos.get_thumbnail(album_name, photo_id)

    return {
        'albumName': album_name,
        'imageName': f'{photo_id}/thumbnail',
        'link': link,
    }


@router.delete('/{album_name}/photos/{photo_id}/thumbnail/link', status_code=204)
async def hide_thumbnail_link(album_name: str, photo_id: str):
    await Photos.suppress_thumbnail(album_name, photo_id)


@router.get('/{album_name}/photos/{photo_id}')
async def get_photo(album_name: str, photo_id: str):
    link = await Photos.get_link(album_name, photo_id)

    return {
        'albumName': album_name,
        'imageName': f'{photo_id}',
        'link': link,
    }


@router.delete('/{album_name}/photos/{photo_id}/link', status_code=204)
async def hide_photo_link(album_name: str, photo_id: str):
    await Photos.suppress_photo(album_name, photo_id)


# @router.get('/{album_name}/{image_name}')
# async def get_image_content(album_name: str, image_name: str):
#     global gdrive

#     content = await gdrive.cat(f'/{album_name}/{image_name}')
#     if content is not None:
#         loop = asyncio.get_event_loop()
#         content = await loop.run_in_executor(None, base64.b64encode, content)

#     return {
#         'albumName': album_name,
#         'imageName': image_name,
#         'content': content,
#     }

