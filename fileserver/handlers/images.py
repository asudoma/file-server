import asyncio
import io

import png
from PIL import Image

from core.exceptions import AlbumCoverMinSizeError
from core.storage import StorageBase
from fileserver.constants import Sections
from .core import FileHandler


class ImageHandlerBase(FileHandler):
    allowed_sections = [Sections.IMAGES, Sections.ALBUM_COVERS]

    def _get_extra_data(self):
        return {
            'original_size': {
                'width': self._get_image_width(),
                'height': self._get_image_height()
            }
        }

    def _get_image_width(self) -> int:
        raise NotImplementedError

    def _get_image_height(self) -> int:
        raise NotImplementedError

    def validate(self, section: str = None, **kwargs):
        super().validate()
        if section == Sections.ALBUM_COVERS:
            image_width = self.extra_data['original_size']['width']
            image_height = self.extra_data['original_size']['height']
            min_w = min_h = 3000
            if image_width < min_w or image_height < min_h:
                raise AlbumCoverMinSizeError(min_w, min_h)

    async def save(self, storage: StorageBase, path):

        loop = asyncio.get_event_loop()
        im = Image.open(self.file_stream)
        sizes = [('medium', (440, 440)), ('medium2x', (880, 880))]
        [loop.create_task(self.save_thumbnails(size, im.copy(), storage, path)) for size in sizes]

        self.file_stream.seek(0)
        return await storage.save(self.file_name, self.file_stream, path)

    async def save_thumbnails(self, size, image: Image, storage: StorageBase, path):
        size_name = size[0]
        size = size[1]
        image.thumbnail(size, )
        image.seek(0)
        with io.BytesIO() as output:
            image.save(output, self.DEFAULT_EXT)
            await storage.save(f'{self.clear_file_name}_thumb_{size_name}.{self.DEFAULT_EXT}', output.getvalue(), path)


class JpegHandler(ImageHandlerBase):
    DEFAULT_EXT = 'jpeg'
    image = None
    mime_types = ('image/jpeg', 'image/pjpeg')

    def after_init(self):
        self.image = Image.open(self.file_stream)

    def _get_image_width(self):
        return self.image.size[0]

    def _get_image_height(self):
        return self.image.size[1]


class PngHandler(ImageHandlerBase):
    DEFAULT_EXT = 'png'
    image = None
    mime_types = ('image/png',)

    def after_init(self):
        r = png.Reader(self.file_stream)
        self.image = r.read()

    def _get_image_width(self) -> int:
        return self.image[0]

    def _get_image_height(self) -> int:
        return self.image[1]
