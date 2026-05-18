from diskcache import Cache


class AppCache:
    def __init__(self, cache_dir: str = "cache"):
        self.cache = Cache(cache_dir)

    def get(self, key: str):
        return self.cache.get(key)

    def set(self, key: str, value):
        self.cache[key] = value

    def clear(self):
        self.cache.clear()
