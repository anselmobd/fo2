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
