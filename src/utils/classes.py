import copy
from subprocess import Popen, PIPE

from django.template import Template, Context


class SingletonMeta(type):
    '''
        Singleton pattern requires for GetUser class
    '''
    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kwargs)
        return cls.instance


class SingletonBaseMeta(metaclass=SingletonMeta):
    pass


class NotLoggedInUserException(Exception):
    '''
    '''
    def __init__(self, val='No users have been logged in'):
        self.val = val
        super(NotLoggedInUser, self).__init__()

    def __str__(self):
        return self.val


class LoggedInUser(SingletonBaseMeta):

    user = None

    def set_user(self, request):
        if request.user.is_authenticated():
            self.user = request.user

    @property
    def current_user(self):
        '''
            Return current user or raise Exception
        '''
        if self.user is None:
            raise NotLoggedInUserException()
        return self.user

    @property
    def have_user(self):
        return user is not None


class TermalPrint:
    _termal_print_controls = {
        'soh_': b'\x01',
        'stx_': b'\x02',
        'ctr_': b'\x0d',
        'esc_': b'\x1b',
    }

    def __init__(self):
        self._print_started = False
        self.lp()
        self.printer()

    def __del__(self):
        if self._print_started:
            self.printer_end()

    def lp(self, lp='/usr/bin/lp'):
        self._lp = copy.copy(lp)

    def printer(self, p='SuporteTI_SuporteTI'):
        self._p = copy.copy(p)

    def template(self, t, limpa):
        tt = copy.copy(t)
        if limpa:
            for l in limpa:
                tt = tt.replace(l, '')
        self._template = Template(tt)

    def context(self, c):
        cc = copy.copy(c)
        cc.update(self._termal_print_controls)
        self._context = Context(cc)

    def render(self):
        commands = self._template.render(self._context)
        return commands.encode('utf-8')

    def printer_init(self):
        self._lpr = Popen([self._lp, "-d"+self._p, "-"], stdin=PIPE)
        self._print_started = True

    def printer_end(self):
        self._lpr.stdin.close()
        self._lpr.wait()

    def printer_send(self):
        self._lpr.stdin.write(self.render())

    def printer_send1(self):
        self.printer_init()
        try:
            self.printer_send()
        finally:
            self.printer_end()
