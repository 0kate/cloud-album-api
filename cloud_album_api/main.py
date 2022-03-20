import json
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient

from cloud_album_api.routers import AlbumsRouter, AnniversariesRouter, MemosRouter


# required_environment_vars = [
#     'API_KEY',
#     'GOOGLE_DRIVE_ROOT_FILE_ID',
#     'GOOGLE_DRIVE_SECRET',
#     'MONGO_USERNAME',
#     'MONGO_PASSWORD',
#     'MONGO_HOST',
# ]
# for required_environment_var in required_environment_vars:
#     if required_environment_var not in os.environ:
#         print(f'Error: {required_environment_var} is not set.')
#         sys.exit(1)

api_key = os.environ['API_KEY']
root_file_id = os.environ['GOOGLE_DRIVE_ROOT_FILE_ID']
service_account_info = json.loads(os.environ['GOOGLE_DRIVE_SECRET'])
mongo_username = os.environ['MONGO_USERNAME']
mongo_password = os.environ['MONGO_PASSWORD']
mongo_host = os.environ['MONGO_HOST']
mongo_scheme = os.environ.get('MONGO_SCHEME', 'mongodb+srv')
mongo_client = MongoClient(f'{mongo_scheme}://{mongo_username}:{mongo_password}@{mongo_host}')


app = FastAPI()
app.include_router(AlbumsRouter, prefix='/albums')
app.include_router(AnniversariesRouter, prefix='/anniversaries')
app.include_router(MemosRouter, prefix='/memos')


@app.middleware('http')
async def check_api_key(request: Request, call_next):
    request_api_key = request.headers.get('x-api-key', '')
    if api_key != request_api_key:
        return JSONResponse({
            'message': 'Forbbiden.',
        }, status_code=403)
    response = await call_next(request)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/')
async def index():
    return {
        'message': 'hello',
    }
