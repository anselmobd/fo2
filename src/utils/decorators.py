import datetime
from functools import wraps, partial
from inspect import signature
from pprint import pprint

from django.core.cache import cache

from utils.cache import entkeys
from utils.functions import (
    fo2logger,
    my_make_key_cache,
)


def method_idle_on_none(old_method):
    '''
        Decorator: Só executa o método se algum argumento não for None
    '''

    def new_method(self, *args):
        for arg in args:
            if arg is not None:
                old_method(self, *args)
                break

    return new_method


def padrao_decorator(func=None, *, message=None):
    '''
        Padrão de decorator
    '''
    if func is None:
        return partial(padrao_decorator, message=message)

    @wraps(func)
    def wrapper(*args, **kwargs):
        if message is not None:
            print(message)

        result = func(*args, **kwargs)

        if message is not None:
            print(message)

        return result

    return wrapper


def caching_function(
        func=None, *,
        key_cache_fields=[],
        max_run_delay=20,
        minutes_key_variation=None):
    if func is None:
        return partial(
            caching_function,
            key_cache_fields=key_cache_fields,
            max_run_delay=max_run_delay,
            minutes_key_variation=minutes_key_variation,
        )

    @wraps(func)
    def wrapper(*args, **kwargs):
        if minutes_key_variation is not None:
            # nova key a cada x minutos
            now = datetime.datetime.now()
            key_variation = int(
                (now.hour * 60 + now.minute) / minutes_key_variation)

        my_make_key_cache_args = [func.__name__]

        sig = signature(func)
        func_params = list(sig.parameters.keys())
        for field in key_cache_fields:
            field_index = func_params.index(field)
            try:
                value = args[field_index]
            except IndexError:
                value = kwargs[field]
            my_make_key_cache_args.append(value)

        if minutes_key_variation is not None:
            my_make_key_cache_args.append(key_variation)

        key_cache = my_make_key_cache(*my_make_key_cache_args)

        fo2logger.info('antes do while')

        while True:
            fo2logger.info('dentro do while')
            calc_cache = cache.get(f"{key_cache}_calc_", "n")
            if calc_cache == 's':
                fo2logger.info('is _calc_ '+key_cache)
                time.sleep(0.2)
            else:
                fo2logger.info('not _calc_ '+key_cache)
                cached_result = cache.get(key_cache)
                if cached_result is None:
                    fo2logger.info('set _calc_ '+key_cache)
                    cache.set(
                        f"{key_cache}_calc_", "s",
                        timeout=entkeys._SECOND * max_run_delay)
                    break
                else:
                    fo2logger.info('cached '+key_cache)
                    return cached_result

        fo2logger.info('depois do while')

        cached_result = func(*args, **kwargs)

        cache.set(key_cache, cached_result)
        cache.set(f"{key_cache}_calc_", "n")
        fo2logger.info('calculated '+key_cache)

        return cached_result

    return wrapper
