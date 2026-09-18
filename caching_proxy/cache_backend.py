import hashlib
import diskcache

from caching_proxy import config

_cache: diskcache.Cache |None = None

def _get_cache() -> diskcache.Cache:
    global _cache
    if _cache is None:
        _cache = diskcache.Cache(config.CACHE_DIR)
    return _cache

def make_key(method: str, path:str, query: str, body: bytes) -> str:
    raw = f"{method}:{path}?{query}:".encode() + body
    return hashlib.sha256(raw).hexdigest()

def get(key: str):
    return _get_cache().get(key)

def set(key: str, value: bytes):
    _get_cache().set(key, value)

def clear():
    _get_cache().clear()