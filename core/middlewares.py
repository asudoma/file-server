from aiohttp.web_middlewares import middleware
from aiohttp.web_response import json_response
from werkzeug.exceptions import BadRequest, Unauthorized

from .exceptions import FileServerError


@middleware
async def error_middleware(request, handler):
    try:
        resp = await handler(request)
    except FileServerError as exc:
        resp = json_response(exc.to_dict(), status=exc.status_code)
    except (BadRequest, Unauthorized) as exc:
        resp = json_response(exc.description, status=exc.code)
    return resp
