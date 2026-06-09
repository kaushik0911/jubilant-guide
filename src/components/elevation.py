from src.cache import AppCache


class ElevationCache(AppCache):
    def __init__(self):
        super().__init__()


class Elevation:

    @staticmethod
    def get_elevation(coords): ...
