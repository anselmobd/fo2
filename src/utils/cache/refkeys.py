import hashlib

from django.core.cache import cache

from utils.functions import fo2logger


_SECOND = 1
_MINUTE = 60
_HOUR = _MINUTE*60
_DAY = _HOUR*24


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class NoEntityError(Error):
    """No entity nor entkey Exception."""

    def __init__(self, *args, **kwargs):
        if not (args or kwargs):
            args = ('Entity and entkey undefined!', )
        super().__init__(*args, **kwargs)


def hash(entity=None, entkey=None):
    if entkey is None:
        if entity is None:
            raise NoEntityError()
        entkey_seasoned = 'entkey_SAUCE_{}'.format(entity)
        entkey = 'entkey_{}'.format(
            hashlib.md5(entkey_seasoned.encode('utf-8')).hexdigest())
    return entkey


def put(keys, entity=None, entkey=None):
    entkey = hash(entity, entkey)
    cache.set(entkey, keys, timeout=60*60*9)


def dput(dkeys, entity=None, entkey=None):
    entkey = hash(entity, entkey)
    keys = '<|>'.join(dkeys)
    put(keys, entkey=entkey)


def get(entity=None, entkey=None):
    entkey = hash(entity, entkey)
    return cache.get(entkey)


def dget(entity=None, entkey=None):
    entkey = hash(entity, entkey)
    keys = get(entkey=entkey)
    dkeys = []
    if keys is not None:
        dkeys = keys.split('<|>')
    return dkeys


def add(key, entity=None, entkey=None):
    entkey = hash(entity, entkey)
    fo2logger.info('add {} {} {}'.format(key, entity, entkey))
    keys = get(entkey=entkey)
    if keys is None:
        keys = key
    else:
        keys = '<|>'.join([keys, key])
    put(keys, entkey=entkey)


def remove(key, entity=None, entkey=None):
    entkey = hash(entity, entkey)
    dkeys = dget(entkey=entkey)
    try:
        dkeys.remove(key)
    except ValueError:
        pass
    dput(dkeys, entkey=entkey)


def delete(entity=None, entkey=None):
    entkey = hash(entity, entkey)
    cache.delete(entkey)


def flush(entity=None, entkey=None):
    entkey = hash(entity, entkey)
    fo2logger.info('flush {} {}'.format(entity, entkey))
    dkeys = dget(entkey=entkey)
    for key in dkeys:
        cache.delete(key)
        fo2logger.info('deleted cache {}'.format(key))
    delete(entkey=entkey)
