from pprint import pprint

from o2.functions.check_digit import strnum_mod1110_digits


class Plt():

    _PLT_HASH_ALPHA = "ABCDEFGHIJKLMNPQRSTUVWXYZ"
    _PLT_LEN_HASH_ALPHA = len(_PLT_HASH_ALPHA)
    _PLT_SALT = 765432
    _PLT_PREFIX = "PLT"
    _PLT_NUM_LEN = 4

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
        str_num = code[len_prefix:len_code-len_hash]
        return prefix, str_num, hash


    def verify(self, str_num):
        return str_num == self.hashed(str_num)


    def hashed(self, code):
        return self.unhashed(code) + self.hash(code)


    def unhashed(self, code):
        prefix, str_num, _ = self.split(code)
        return ''.join([prefix, str_num])


    def next(self, code=None):
        if not code:
            code = self.code
        prefix, str_num, _ = self.split(code)
        next_num = int(str_num) + 1 
        return self.mount(next_num, prefix, len(str_num))


    def mount(self, num, prefix=_PLT_PREFIX, num_len=_PLT_NUM_LEN):
        str_num = str(num)
        len_str_num = len(str_num)
        if len_str_num > num_len:
            prefix = prefix[:num_len-len_str_num]
        str_num = str_num.zfill(num_len)
        return self.hashed(''.join([prefix, str_num]))


    def hash(self, code):
        _, str_num, _ = self.split(code)
        num = int(str_num)
        num_salt = num + self._PLT_SALT
        str_num_salt = str(num_salt)
        hash_digits = strnum_mod1110_digits(str_num_salt, ndigits=2)
        hash_int = int(hash_digits)
        hash = self._PLT_HASH_ALPHA[hash_int%self._PLT_LEN_HASH_ALPHA]
        return hash
