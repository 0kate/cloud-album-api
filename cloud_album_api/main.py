import asyncio
import base64
import json
import os
import sys
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient

from cloud_album_api.cloud_storage import DEntryType, GoogleDrive


if os.getenv('DEV', 'false') == 'true':
    load_dotenv()


required_environment_vars = [
    'API_KEY',
    'GOOGLE_DRIVE_ROOT_FILE_ID',
    'GOOGLE_DRIVE_SECRET',
    'MONGO_USERNAME',
    'MONGO_PASSWORD',
]
for required_environment_var in required_environment_vars:
    if required_environment_var not in os.environ:
        print(f'Error: {required_environment_var} is not set.')
        sys.exit(1)

api_key = os.environ['API_KEY']
root_file_id = os.environ['GOOGLE_DRIVE_ROOT_FILE_ID']
service_account_info = json.loads(os.environ['GOOGLE_DRIVE_SECRET'])
mongo_username = os.environ['MONGO_USERNAME']
mongo_password = os.environ['MONGO_PASSWORD']
mongo_client = MongoClient(f'mongodb://{mongo_username}:{mongo_password}@cloud-album-mongo:27017')


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.middleware('http')
async def check_api_key(request: Request, call_next):
    request_api_key = request.headers.get('x-api-key', '')
    if api_key != request_api_key:
        return JSONResponse({
            'message': 'Forbbiden.',
        }, status_code=403)
    response = await call_next(request)
    return response


@app.get('/')
async def index():
    return {
        'message': 'hello',
    }


@app.get('/albums')
async def get_albums():
    global root_file_id
    global service_account_info

    gdrive = GoogleDrive(service_account_info, root_file_id)
    entries = await gdrive.ls('/')

    return {
        'albums': [
            { 'name': entry.name }
            for entry in entries
            if entry.type == DEntryType.DIRECTORY
        ],
    }


@app.get('/albums/{album_name}')
async def get_images(album_name: str):
    global root_file_id
    global service_account_info

    gdrive = GoogleDrive(service_account_info, root_file_id)
    images = await gdrive.ls(f'/{album_name}')

    return {
        'albumName': album_name,
        'images': [
            { 'name': image.name }
            for image in images
            if image.name != 'thumbnail'
        ],
    }


@app.get('/albums/{album_name}/{image_name}')
async def get_image_content(album_name: str, image_name: str):
    global root_file_id
    global service_account_info

    gdrive = GoogleDrive(service_account_info, root_file_id)
    content = await gdrive.cat(f'/{album_name}/{image_name}')
    if content is not None:
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, base64.b64encode, content)

    return {
        'albumName': album_name,
        'imageName': image_name,
        'content': content,
    }


@app.get('/memos')
async def get_memos():
    global mongo_client
    collection = mongo_client.cloud_album.memos

    memos = list(collection.find())
    for memo in memos:
        del memo['_id']

    return {
        'memos': memos,
    }


@app.post('/memos')
async def create_new_memo(req: Request):
    global mongo_client
    collection = mongo_client.cloud_album.memos

    body = await req.json()
    memo_id = str(uuid.uuid4())
    memo_title = body.get('title', '')
    collection.insert_one({
        'id': memo_id,
        'title': memo_title,
        'done': False,
    })

    return {
        'id': memo_id,
    }


@app.delete('/memos/{memo_id}', status_code=204)
async def delete_memo(memo_id: str):
    global mongo_client
    collection = mongo_client.cloud_album.memos

    collection.delete_one({ 'id': memo_id })


@app.put('/memos/{memo_id}', status_code=200)
async def update_memo(memo_id: str, req: Request):
    global mongo_client
    collection = mongo_client.cloud_album.memos

    body = await req.json()
    collection.update_one(
        { 'id': memo_id },
        {
            '$set': {
                'title': body['title'],
                'done': body['done'],
            },
        },
    )
