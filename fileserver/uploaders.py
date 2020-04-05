import os
from uuid import uuid4

from core import settings
from core.storage import RedisStorage, StorageBase
from .dataclassess import FileData
from .handlers import FileHandlerFactory


async def upload_file(file: FileData,
                      redis_storage: RedisStorage,
                      file_storage: StorageBase,
                      section: str = None, user_id='', **kwargs):
    file_handler = FileHandlerFactory().create_file_handler(file, section)
    file_handler.validate(section=section)
    file_data = file_handler.file_data
    file_handler.process_file()
    if section:
        file_path = os.path.join(f'{user_id}', section)
    else:
        file_path = ''
    file_path = await file_handler.save(file_storage, path=file_path)
    file_data['file_path'] = file_path

    key = str(uuid4())
    file_data.update({'id': key})
    await redis_storage.save('{}:{}'.format(settings.REDIS_KEY_PREFIX, key), file_data, file_path)
    return file_data
