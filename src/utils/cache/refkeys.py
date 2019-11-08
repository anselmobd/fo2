import hashlib

from django.core.cache import cache

from utils.functions import fo2logger


def hash(ref):
    key_seasoned = 'keys_ref_SAUCE_{}'.format(ref)
    key_hash = 'keys_ref_{}'.format(
        hashlib.md5(key_seasoned.encode('utf-8')).hexdigest())
    return key_hash


def put(ref, keys, key_hash=None):
    if key_hash is None:
        key_hash = hash(ref)
    cache.set(key_hash, keys, timeout=60*60*9)


def dset(ref, dkeys, key_hash=None):
    if key_hash is None:
        key_hash = hash(ref)
    keys = '<|>'.join(dkeys)
    put(ref, keys, key_hash=key_hash)


def get(ref, key_hash=None):
    if key_hash is None:
        key_hash = hash(ref)
    return cache.get(key_hash)


def dget(ref, key_hash=None):
    if key_hash is None:
        key_hash = hash(ref)
    keys = get(key_hash, key_hash=key_hash)
    dkeys = []
    if keys is not None:
        dkeys = keys.split('<|>')
    return dkeys


def add(ref, key):
    fo2logger.info('add {} {}'.format(ref, key))
    key_hash = hash(ref)
    keys = get(ref, key_hash=key_hash)
    if keys is None:
        keys = key
    else:
        keys = '<|>'.join([keys, key])
    put(ref, keys, key_hash=key_hash)


def remove(ref, key):
    key_hash = hash(ref)
    dkeys = dget(ref, key_hash=key_hash)
    try:
        dkeys.remove(key)
    except ValueError:
        pass
    dset(ref, dkeys, key_hash=key_hash)


def delete(ref):
    fo2logger.info('delete {}'.format(ref))
    key_hash = hash(ref)
    cache.delete(key_hash)
