import json
import os

import aiobotocore
import aiofiles
import aiofiles.os
import aioredis

from core import settings
from core.settings import BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

makedirs = aiofiles.os.wrap(os.makedirs)


class StorageBase(object):
    async def save(self, key, data, path, **kwargs):
        raise NotImplementedError


class RedisStorage(StorageBase):
    async def init(self, loop=None):
        address = f'{settings.REDIS_SCHEME}://{settings.REDIS_HOST}:{settings.REDIS_PORT}'
        self.storage = await aioredis.create_redis_pool(
            address,
            db=settings.REDIS_DB,
            minsize=settings.REDIS_MINPOOL,
            maxsize=settings.REDIS_MAXPOOL,
            loop=loop
        )

    async def close(self):
        self.storage.close()
        await self.storage.wait_closed()

    async def get(self, key):
        with await self.storage as conn:
            result = await conn.get(key)
            return json.loads(result) if result else {}

    async def save(self, key, data, path, **kwargs):
        with await self.storage as conn:
            await conn.set(key, json.dumps(data), expire=settings.REDIS_EXPIRE)


class NoopStorage(StorageBase):
    async def save(self, key, data, path, **kwargs):
        pass


class FileSystemStorage(StorageBase):
    ROOT_PATH = getattr(settings, 'FILE_ROOT_PATH', 'media')

    async def save(self, key, data, path, **kwargs):
        full_path = await self._create_folder(path)
        async with aiofiles.open(os.path.join(full_path, key), mode='wb') as file:
            if not isinstance(data, bytes):
                data = data.readall()
            await file.write(data)
        return os.path.join(path, key)

    async def _create_folder(self, path) -> str:
        path = os.path.join(self.ROOT_PATH, path)
        path_exists = os.path.exists(path)
        if not path_exists:
            await makedirs(path)
        return path


class S3Storage(StorageBase):
    @property
    def botoclient(self):
        session = aiobotocore.get_session()
        return session.create_client(
            's3', region_name='eu-central-1',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    async def save(self, key, data, path, **kwargs):
        full_name = os.path.join(path, key)
        async with self.botoclient as s3:
            await s3.put_object(Bucket=BUCKET, Key=full_name, Body=data)
        return full_name
