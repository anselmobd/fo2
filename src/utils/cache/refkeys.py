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


def hash(ref):
    key_seasoned = 'keys_ref_SAUCE_{}'.format(ref)
    key_hash = 'keys_ref_{}'.format(
        hashlib.md5(key_seasoned.encode('utf-8')).hexdigest())
    return key_hash


def put(keys, ref=None, key_hash=None):
    if key_hash is None:
        if ref is None:
            raise Error('ref and key_hash undefined')
        key_hash = hash(ref)
    cache.set(key_hash, keys, timeout=60*60*9)


def dput(dkeys, ref=None, key_hash=None):
    if key_hash is None:
        if ref is None:
            raise Error('ref and key_hash undefined')
        key_hash = hash(ref)
    keys = '<|>'.join(dkeys)
    put(keys, key_hash=key_hash)


def get(ref=None, key_hash=None):
    if key_hash is None:
        if ref is None:
            raise Error('ref and key_hash undefined')
        key_hash = hash(ref)
    return cache.get(key_hash)


def dget(ref=None, key_hash=None):
    if key_hash is None:
        if ref is None:
            raise Error('ref and key_hash undefined')
        key_hash = hash(ref)
    keys = get(key_hash=key_hash)
    dkeys = []
    if keys is not None:
        dkeys = keys.split('<|>')
    return dkeys


def add(key, ref=None, key_hash=None):
    if key_hash is None:
        if ref is None:
            raise Error('ref and key_hash undefined')
        key_hash = hash(ref)
    fo2logger.info('add {} {} {}'.format(key, ref, key_hash))
    keys = get(key_hash=key_hash)
    if keys is None:
        keys = key
    else:
        keys = '<|>'.join([keys, key])
    put(keys, key_hash=key_hash)


def remove(key, ref=None, key_hash=None):
    if key_hash is None:
        if ref is None:
            raise Error('ref and key_hash undefined')
        key_hash = hash(ref)
    dkeys = dget(key_hash=key_hash)
    try:
        dkeys.remove(key)
    except ValueError:
        pass
    dput(dkeys, key_hash=key_hash)


def delete(ref, key_hash=None):
    if key_hash is None:
        key_hash = hash(ref)
    cache.delete(key_hash)


def flush(ref):
    fo2logger.info('flush {}'.format(ref))
    key_hash = hash(ref)
    dkeys = dget(key_hash=key_hash)
    for key in dkeys:
        cache.delete(key)
        fo2logger.info('deleted cache {}'.format(key))
    delete(ref, key_hash=key_hash)
