import hashlib


def refkeys_hash(ref):
    key_seasoned = 'keys_ref_SAUCE_{}'.format(ref)
    key_hash = 'keys_ref_{}'.format(
        hashlib.md5(key_seasoned.encode('utf-8')).hexdigest())
    return key_hash


def refkeys_set(ref, keys, key_hash=None):
    if key_hash is None:
        key_hash = refkeys_hash(ref)
    cache.set(key_hash, keys, timeout=60*60*9)


def refkeys_dset(ref, dkeys, key_hash=None):
    if key_hash is None:
        key_hash = refkeys_hash(ref)
    keys = '<|>'.join(dkeys)
    refkeys_set(ref, keys, key_hash=key_hash)


def refkeys_get(ref, key_hash=None):
    if key_hash is None:
        key_hash = refkeys_hash(ref)
    return cache.get(key_hash)


def refkeys_dget(ref, key_hash=None):
    if key_hash is None:
        key_hash = refkeys_hash(ref)
    keys = refkeys_get(key_hash, key_hash=key_hash)
    dkeys = []
    if keys is not None:
        dkeys = keys.split('<|>')
    return dkeys


def refkeys_add(ref, key):
    key_hash = refkeys_hash(ref)
    keys = refkeys_get(ref, key_hash=key_hash)
    if keys is not None:
        keys = '<|>'.join([keys, key])
    refkeys_set(ref, keys, key_hash=key_hash)


def refkeys_remove(ref, key):
    key_hash = refkeys_hash(ref)
    dkeys = refkeys_dget(ref, key_hash=key_hash)
    try:
        dkeys.remove(key)
    except ValueError:
        pass
    refkeys_dset(ref, dkeys, key_hash=key_hash)


def refkeys_delete(ref):
    key_hash = refkeys_hash(ref)
    keys_ref = cache.delete(key_hash)
