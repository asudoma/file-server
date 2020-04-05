from core.utils import format_bytes

from . import settings


class FileServerError(Exception):
    error_code = 'invalid'

    def __init__(self, message=None, status_code=400, field=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.field = field

    def to_dict(self):
        data = {
            'internalMessage': 'Invalid input',
            'userMessage': self.message,
            'errorCode': self.error_code,
        }
        return data


class OversizeFileError(FileServerError):
    error_code = 'file_oversize'

    def __init__(self):
        message = f'Размер файла не должен превышать {format_bytes(settings.MAX_FILE_SIZE)}'
        super().__init__(message=message, field='file')


class AlbumCoverMinSizeError(FileServerError):
    error_code = 'image_wrongsize'

    def __init__(self, min_width, min_height):
        message = f'Размер изображения должен быть минимум {min_width}х{min_height} пикселей'
        super().__init__(message=message, field='file')


class UnsupportedFormatError(FileServerError):
    error_code = 'file_unsupported_format'

    def __init__(self):
        message = 'Unsupported file format'
        super().__init__(message=message, field='file')
