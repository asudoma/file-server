from aiohttp import web
from aiohttp.web_exceptions import HTTPRequestEntityTooLarge
from aiohttp.web_request import Request, FileField
from aiohttp.web_response import json_response

from core import settings
from core.decorators import authorize
from core.exceptions import OversizeFileError, FileServerError
from .constants import Sections
from .dataclassess import FileData
from .uploaders import upload_file


async def index(request: Request):
    return web.Response(body='File Server')


@authorize
async def upload(request: Request):
    try:
        post = await request.post()
        file: FileField = post[settings.FILE_FIELD_NAME]
    except HTTPRequestEntityTooLarge:
        raise OversizeFileError()
    except Exception as exc:
        sentry_client = request.app.get('sentry_client')
        if sentry_client:
            sentry_client.captureException()
        raise FileServerError('Файл не был получен', field='file')
    redis_storage = request.app.get('redis_storage')
    file_storage = request.app.get('file_storage')
    data = FileData(file_name=file.filename, file_body=file.file)

    section = request.query.get('section')
    if not section or not Sections.contains(section):
        return json_response()

    data = await upload_file(data, redis_storage, file_storage, section, user_id=request.user_id)
    return json_response(data)
