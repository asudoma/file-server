from envparse import env

DJANGO_SECRET_KEY = env('DJANGO_SECRET_KEY')

AUTHENTICATION_BACKEND = 'core.JSONWebTokenAuthentication'

SENTRY_DSN = env('SENTRY_DSN', default='')

MAX_FILE_SIZE = env('MAX_FILE_SIZE',  1024 * 1024 * 200)

HOST = env('HOST', default='127.0.0.1')
PORT = env('PORT', default=5000, cast=int)

FILE_FIELD_NAME = 'file'

REDIS_KEY_PREFIX = 'FILESERVER'
REDIS_SCHEME = 'redis'
REDIS_HOST = env('REDIS_HOST', default='redis')
REDIS_PORT = env('REDIS_PORT_', default='6379')

REDIS_DB = env('REDIS_DB', 1)
REDIS_EXPIRE = env('REDIS_EXPIRE', 30 * 24 * 60 * 60)
REDIS_MINPOOL = env('REDIS_MINPOOL', 1)
REDIS_MAXPOOL = env('REDIS_MAXPOOL', 10)

STORAGE_CLASS = env('STORAGE_CLASS', 'core.FileSystemStorage')

BUCKET = env('BUCKET_NAME')
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
