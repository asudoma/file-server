import os
import typing as tp
from uuid import uuid4

import magic

from core.exceptions import UnsupportedFormatError
from core.storage import StorageBase
from fileserver.dataclassess import FileData


class FileHandlerFactory:
    def create_file_handler(self, file: FileData, section=None) -> 'FileHandler':
        file_body = file.file_body
        file_body.seek(0, os.SEEK_END)
        length = file_body.tell()
        file_body.seek(0)
        mime_type = magic.from_buffer(file_body.read(length), mime=True)
        file_body.seek(0)
        handler: tp.Type[FileHandler] = FileHandler.get_class_for_mime_type(mime_type)
        if not handler or not handler.supports_section(section):
            raise UnsupportedFormatError()
        return handler(file_body.raw, file.file_name, mime_type, length)


class FileHandler:
    DEFAULT_EXT = ''
    allowed_sections: tp.List[str] = []
    mime_types = []

    def __init__(self, file_stream, filename, type_, length):
        self.file_stream = file_stream
        self.orig_file_name = filename
        self.file_type = type_
        self.file_length = length
        self._file_name = None
        self.clear_file_name = None
        self.after_init()
        self._file_data = None
        self._extra_data = {}

    @property
    def file_data(self):
        if not self._file_data:
            self._file_data = self._get_file_data()
        return self._file_data

    @property
    def file_name(self):
        if not self._file_name:
            self.clear_file_name = uuid4().hex
            self._file_name = f'{self.clear_file_name}.{self.DEFAULT_EXT}'
        return self._file_name

    @property
    def extra_data(self):
        if not self._extra_data:
            self._extra_data = self._get_extra_data()
        return self._extra_data

    @classmethod
    def get_class_for_mime_type(cls, mime_type: str) -> tp.Optional[tp.Type['FileHandler']]:
        def recursive_subclasses(class_):
            subclasses = class_.__subclasses__()
            return set([s for s in subclasses if not s.__subclasses__()]).union(
                [s for c in subclasses for s in recursive_subclasses(c)]
            )

        for subclass in recursive_subclasses(cls):
            if mime_type in subclass.get_mime_types():
                return subclass
        return None

    @classmethod
    def get_mime_types(cls):
        if not cls.mime_types:
            raise ValueError(f'The "mime_types" param is not specified for {cls}.')
        return cls.mime_types

    @classmethod
    def supports_section(cls, section=None):
        if section:
            return section in cls.allowed_sections
        return True

    def after_init(self):
        pass

    def _get_file_data(self):
        return {
            'file_name': self.file_name,
            'file_type': self.file_type,
            'orig_file_name': self.orig_file_name,
            'file_size': self.file_length,
            'extra_data': self.extra_data
        }

    def _get_extra_data(self):
        return self._extra_data

    def process_file(self):
        pass

    async def save(self, storage: StorageBase, path):
        self.file_stream.seek(0)
        return await storage.save(self.file_name, self.file_stream, path)

    def validate(self, **kwargs):
        pass
