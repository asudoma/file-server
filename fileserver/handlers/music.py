from mutagen.id3 import ID3
from mutagen.id3._tags import ID3Header
from mutagen.mp3 import MP3

from fileserver.constants import Sections
from .core import FileHandler


class TrackHandlerBase(FileHandler):
    allowed_sections = [Sections.TRACKS]

    def _get_extra_data(self):
        return {
            'title': '',
            'music_authors': '',
            'text_authors': '',
            'lyrics': '',
            'original_artist_name': '',
            'duration': 0
        }


class Mp3Handler(TrackHandlerBase):
    mime_types = MP3._mimes
    DEFAULT_EXT = 'mp3'

    def after_init(self):
        self.file: MP3 = MP3(self.file_stream)

    def _get_extra_data(self):
        data = super()._get_extra_data()
        tags: ID3 = self.file.tags
        if tags is not None and tags.version in (ID3Header._V23, ID3Header._V24):
            data.update({
                'title': str(tags.get('TIT2', '')),
                'music_authors': str(tags.get('TCOM', '')),
                'lyrics_authors': str(tags.get('TEXT', '')),
                'lyrics': str(tags.get('USLT', '')),
                'original_artist_name': str(tags.get('TOPE', ''))
            })
        data['duration'] = round(self.file.info.length)
        return data


class WavHandler(TrackHandlerBase):
    mime_types = ('audio/x-wav',)
    DEFAULT_EXT = 'wav'

    def _get_extra_data(self):
        import wave
        import contextlib
        with contextlib.closing(wave.open(self.file_stream, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
        data = super()._get_extra_data()
        data.update({
            'duration': round(duration)
        })
        return data
