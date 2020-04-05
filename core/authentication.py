import jwt
from werkzeug import exceptions

from core import settings


def get_authorization_header(request):
    return request.headers.get('Authorization', '')


class JSONWebTokenAuthentication(object):
    def authenticate(self, request):
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            raise exceptions.Unauthorized()

        try:
            payload = self.jwt_decode(jwt_value)
            request.user_id = payload.get('user_id')
        except jwt.ExpiredSignature:
            msg = 'Signature has expired.'
            raise exceptions.Unauthorized(msg)
        except jwt.DecodeError as err:
            msg = 'Error decoding signature.'
            raise exceptions.Unauthorized(msg)

        return True

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = 'bearer'

        if not auth or auth[0].lower() != auth_header_prefix:
            return None
        if len(auth) == 1:
            msg = 'Invalid Authorization header. No credentials provided.'
            raise exceptions.Unauthorized(msg)
        elif len(auth) > 2:
            msg = ('Invalid Authorization header. Credentials string '
                   'should not contain spaces.')
            raise exceptions.Unauthorized(msg)
        return auth[1]

    def jwt_decode(self, token):
        return jwt.decode(token, settings.DJANGO_SECRET_KEY)
