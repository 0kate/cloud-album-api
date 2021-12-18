import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


if os.getenv('DEV', 'false') == 'true':
    load_dotenv()


api_key = os.getenv('API_KEY', '')
app = FastAPI()


@app.middleware('http')
async def check_api_key(request: Request, call_next):
    request_api_key = request.headers.get('x-api-key', '')
    print(api_key)
    print(request_api_key)
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
