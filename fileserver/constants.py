class Sections:
    ALBUM_COVERS = 'album_covers'
    IMAGES = 'images'
    TRACKS = 'tracks'

    allowed_sections = (ALBUM_COVERS, IMAGES, TRACKS)

    @classmethod
    def contains(cls, section: str) -> bool:
        return section in cls.allowed_sections
