import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from google.oauth2.service_account import Credentials
from googleapiclient import discovery


if os.getenv('DEV', 'false') == 'true':
    load_dotenv()


api_key = os.getenv('API_KEY', '')
app = FastAPI()


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
    cred = Credentials.from_service_account_info(service_account_info)
    gdrive = discovery.build('drive', 'v3', credentials=cred)
    response = gdrive.files().list(q=f'"{root_file_id}" in parents').execute()
    albums = [
        {
            'name': f.get('name', 'unknown'),
        }
        for f in response.get('files', [])
    ]

    return {
        'albums': albums,
    }
