from pprint import pprint


__all__ = ['get_defa']


def get_defa(ite, idx, defa=None):
    return next(iter(ite[idx:idx+1]), defa)
