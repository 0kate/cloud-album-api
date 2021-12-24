import base64
import json
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.cloud_storage import DEntryType, GoogleDrive


if os.getenv('DEV', 'false') == 'true':
    load_dotenv()


required_environment_vars = [
    'API_KEY',
    'GOOGLE_DRIVE_ROOT_FILE_ID',
    'GOOGLE_DRIVE_SECRET',
]
for required_environment_var in required_environment_vars:
    if required_environment_var not in os.environ:
        print(f'Error: {required_environment_var} is not set.')
        sys.exit(1)

api_key = os.environ['API_KEY']
root_file_id = os.environ['GOOGLE_DRIVE_ROOT_FILE_ID']
service_account_info = json.loads(os.environ['GOOGLE_DRIVE_SECRET'])


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
    content = await gdrive.cat(f'/{album_name}/thumbnail')
    if content is not None:
        content = base64.b64encode(content)

    return {
        'albumName': album_name,
        'imageName': image_name,
        'content': content,
    }
