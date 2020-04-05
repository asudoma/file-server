import aiohttp_cors
import sentry_sdk
from aiohttp import web
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from core import settings, routes
from core.middlewares import error_middleware
from core.storage import RedisStorage
from core.utils import get_class_by_path

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[AioHttpIntegration()]
    )

app = web.Application(
    middlewares=[error_middleware],
    client_max_size=settings.MAX_FILE_SIZE
)

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_methods=["OPTION", "POST", "GET"],
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

for route in routes.routes:
    cors.add(app.router.add_route(**route))


async def redis_pool(app):
    app['redis_storage'] = RedisStorage()
    await app['redis_storage'].init()
    yield
    await app['redis_storage'].close()


app.cleanup_ctx.append(redis_pool)

app['file_storage'] = get_class_by_path(settings.STORAGE_CLASS)()

web.run_app(app, host=settings.HOST, port=settings.PORT)
