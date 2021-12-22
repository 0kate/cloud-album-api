import base64
import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.cloud_storage import DEntryType, GoogleDrive


if os.getenv('DEV', 'false') == 'true':
    load_dotenv()


api_key = os.getenv('API_KEY', '')
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
async def get_albums(request: Request):
    root_file_id = os.getenv('GOOGLE_DRIVE_ROOT_FILE_ID')
    if root_file_id is None:
        print('Error: root file id is not set.')
        return JSONResponse({
            'message': 'Internal server error. Please contact to the admin.',
        }, status_code=500)

    service_account_info = os.getenv('GOOGLE_DRIVE_SECRET')
    if service_account_info is None:
        print('Error: secret is not set.')
        return JSONResponse({
            'message': 'Internal server error. Please contact to the admin.',
        }, status_code=500)

    service_account_info = json.loads(service_account_info)
    gdrive = GoogleDrive(service_account_info, root_file_id)
    entries = await gdrive.ls('/')

    return {
        'albums': [
            { 'name': entry.name }
            for entry in entries
            if entry.type == DEntryType.DIRECTORY
        ],
    }


@app.get('/albums/{album_name}/thumbnail')
async def get_thumbnail(album_name: str, request: Request):
    root_file_id = os.getenv('GOOGLE_DRIVE_ROOT_FILE_ID')
    if root_file_id is None:
        print('Error: root file id is not set.')
        return JSONResponse({
            'message': 'Internal server error. Please contact to the admin.',
        }, status_code=500)

    service_account_info = os.getenv('GOOGLE_DRIVE_SECRET')
    if service_account_info is None:
        print('Error: secret is not set.')
        return JSONResponse({
            'message': 'Internal server error. Please contact to the admin.',
        }, status_code=500)

    service_account_info = json.loads(service_account_info)
    gdrive = GoogleDrive(service_account_info, root_file_id)
    content = await gdrive.cat(f'/{album_name}/thumbnail')
    if content is not None:
        content = base64.b64encode(content)

    return {
        'albumName': album_name,
        'thumbnail': content,
    }

