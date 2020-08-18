import os
import copy
import time
from subprocess import Popen, PIPE
import struct
from pprint import pprint

from django.template import Template, Context
from django.core.exceptions import ValidationError
from django.conf import settings


class SingletonMeta(type):
    '''
        Singleton pattern requires for LoggedInUser class
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
        super(NotLoggedInUserException, self).__init__()

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


class NotAcessoInternoException(Exception):
    def __init__(self, val='Não foi verificado se o acesso é interno'):
        self.val = val
        super(NotAcessoInternoException, self).__init__()

    def __str__(self):
        return self.val


class AcessoInterno(SingletonBaseMeta):

    interno = None

    def set_interno(self, interno):
        self.interno = interno

    @property
    def current_interno(self):
        '''
            Return interno if defined or raise Exception
        '''
        if self.interno is None:
            raise NotAcessoInternoException()
        return self.interno

    @property
    def have_interno(self):
        return interno is not None


class GitVersion(SingletonBaseMeta):

    git_version = None

    @property
    def version(self):
        '''
            Return current gitversion
        '''
        if self.git_version is None:
            git_dir = os.path.dirname(settings.BASE_DIR)
            print(git_dir)
            try:
                comm = 'git -C {} log -1 --pretty=format:"%h (%cd)" ' + \
                    '--date=format:"%d/%m/%Y"'
                comm = comm.format(git_dir)
                print(comm)
                # Date and hash ID
                head = subprocess.Popen(
                    comm, shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                self.git_version = head.stdout.readline().strip().decode()
            except Exception as e:
                self.git_version = 'desconhecida'
        return self.git_version


def rawbytes(s):
    """Convert a string to raw bytes without encoding"""
    outlist = []
    for cp in s:
        num = ord(cp)
        if num < 255:
            outlist.append(struct.pack('B', num))
        elif num < 65535:
            outlist.append(struct.pack('>H', num))
        else:
            b = (num & 0xFF0000) >> 16
            H = num & 0xFFFF
            outlist.append(struct.pack('>bH', b, H))
    return b''.join(outlist)


class TermalPrint:
    _termal_print_controls = {
        'soh_': b'\x01',
        'stx_': b'\x02',
        'ctr_': b'\x0d',
        'esc_': b'\x1b',
    }
    _mark_ini = b'[#[binary:'
    _mark_fim = b']#]'

    def __init__(self, p='SuporteTI_SuporteTI'):
        self._print_started = False
        self.lp()
        self.printer(p)

    def __del__(self):
        if self._print_started:
            self.printer_end()

    def lp(self, lp='/usr/bin/lp'):
        self._lp = copy.copy(lp)

    def printer(self, p):
        self._p = copy.copy(p)

    def template(self, t, limpa, strip_end_line=''):
        tt = copy.copy(t)

        if strip_end_line != '':
            tts = copy.copy(tt)
            for i in range(len(strip_end_line)-1):
                tts = tts.replace(strip_end_line[i], '')
            tts = tts.split(strip_end_line[-1])
            ttl = []
            for line in tts:
                ttl.append(line.strip())
            tt = strip_end_line.join(ttl)

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
        bcommands = commands.encode('cp850')

        pos_mark = bcommands.find(self._mark_ini)
        while pos_mark >= 0:
            pos_nome = pos_mark+len(self._mark_ini)
            len_name = bcommands[pos_nome:].find(self._mark_fim)
            name = bcommands[pos_nome:pos_nome+len_name].decode()
            bcommands = \
                bcommands[:pos_mark] + \
                self._context[name] + \
                bcommands[pos_mark+len(
                    self._mark_ini)+len_name+len(self._mark_fim):]
            pos_mark = bcommands.find(self._mark_ini)
            break

        return bcommands

    def printer_start(self):
        self._lpr = Popen([self._lp, "-d{}".format(self._p), "-"], stdin=PIPE)
        self._print_started = True

    def printer_end(self):
        self._lpr.stdin.close()
        self._lpr.wait()

    def printer_send(self):
        self._lpr.stdin.write(self.render())

    def printer_send1(self):
        self.printer_start()
        try:
            self.printer_send()
        finally:
            self.printer_end()


class Perf:
    def __init__(self, on=True, id=None):
        self.on() if on else self.off()
        self.id = id

    def on(self):
        self.active = True
        self.reset()

    def off(self):
        self.active = False

    def reset(self):
        if self.active:
            self.inicio = time.perf_counter()
            self.last = time.perf_counter()

    def prt(self, descr):
        if self.active:
            counter = time.perf_counter()
            print('{:6.3f} {:6.3f} {}{}'.format(
                counter - self.last,
                counter - self.inicio,
                self.id,
                descr,
            ))
            self.last = time.perf_counter()

    @property
    def id(self):
        try:
            return self._id
        except Exception:
            self._id = None
        return self._id

    @id.setter
    def id(self, value):
        self._id = '' if value is None else ''.join([value, ':'])


class LowerCaseValidator(object):
    def validate(self, password, user=None):
        if password != password.lower():
            raise ValidationError(
                "Sua senha não pode ter maiúsculas.",
                code='password_with_upper',
            )

    def get_help_text(self):
        return "Sua senha não pode ter maiúsculas."
