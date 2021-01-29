from pprint import pprint


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



