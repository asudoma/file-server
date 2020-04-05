import functools

from werkzeug.exceptions import Unauthorized

from . import settings
from .utils import get_class_by_path


def authorize(f):
    @functools.wraps(f)
    def wrapper(request):
        try:
            authentication_backend = get_class_by_path(settings.AUTHENTICATION_BACKEND)
            authenticator = authentication_backend()
        except Exception:
            raise Unauthorized()
        authenticator.authenticate(request)
        return f(request)

    return wrapper
