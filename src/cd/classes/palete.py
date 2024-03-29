from pprint import pprint

from o2.functions.check_digit import mod1110_modchar_o
from utils.classes.numbers import BaseConversion
from utils.functions.strings import only_digits


class Plt():

    _PLT_SALT = 765432
    _PLT_PREFIX_DEFAULTS = {
        "PLT": 1,
        "CALHA": 2,
        "FANTAS": 3,
    }
    _PLT_PREFIX = "PLT"
    _PLT_PREFIX_NUM_LEN = {
        "PLT": 4,
        "CALHA": 2,
        "FANTAS": 1,
    }

    def __init__(self, code=None) -> None:
        self.code = code

    def split(self, code=None):
        if not code:
            code = self.code
        prefix_list = []
        for char in code:
            if char.isalpha():
                prefix_list.append(char)
            else:
                break
        prefix = ''.join(prefix_list)
        hash = code[-1] if code[-1].isalpha() else ''
        len_code = len(code)
        len_prefix = len(prefix)
        len_hash = len(hash)
        if len_code <= len_prefix + len_hash:
            raise ValueError("Valid formats: A*9* or A*9*A")
        strnum = code[len_prefix:len_code-len_hash]
        return prefix, strnum, hash


    def verify(self, code=None):
        if not code:
            code = self.code
        return code == self.hashed(code)


    def hashed(self, code):
        return self.unhashed(code) + self.hash(code)


    def unhashed(self, code):
        prefix, strnum, _ = self.split(code)
        return ''.join([prefix, strnum])


    def next(self, code=None):
        if not code:
            code = self.code
        prefix, strnum, _ = self.split(code)
        next_num = int(strnum) + 1 
        return self.mount(next_num, prefix, len(strnum))


    def mount(self, num, prefix=_PLT_PREFIX, num_len=None):
        """
        Obs.: Se for passado um prefix que não consta no
        _PLT_PREFIX_NUM_LEN, também deve ser informado um num_len
        """
        strnum = only_digits(str(num))
        if not num_len:
            num_len = self._PLT_PREFIX_NUM_LEN[prefix]
        len_strnum = len(strnum)
        if len_strnum > num_len:
            prefix = prefix[:num_len-len_strnum]
        strnum = strnum.zfill(num_len)
        return self.hashed(''.join([prefix, strnum]))

    def prefix_to_int(self, prefix):
        bc = BaseConversion('A')
        return bc.str_to_number(prefix)

    def hash(self, code):
        prefix, strnum, _ = self.split(code)
        prefix_val = self._PLT_PREFIX_DEFAULTS.get(
            prefix,
            self.prefix_to_int(prefix),
        )
        num = int(strnum)
        num_salt = (num + self._PLT_SALT) * (prefix_val % 100)
        strnum_salt = str(num_salt)
        return mod1110_modchar_o(strnum_salt)
