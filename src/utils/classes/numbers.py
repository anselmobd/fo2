from pprint import pprint


class BaseConversion():
    def __init__(self, spaces='0Aa', start=None, end=None, excludes=''):
        self.config()
        self.spaces = spaces
        self.start = start
        self.end = end
        self.excludes = excludes

    def config(self):
        # constants
        self._spaces_dict = {
            '0': "0123456789",
            'A': "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            'a': "abcdefghijklmnopqrstuvwxyz",
        }
        # parameters
        self._spaces = None
        self._start = None
        self._end = None
        self._excludes = None
        # properts
        self._full_space = None
        self._space = None

    @property
    def spaces(self):
        return self._spaces

    @spaces.setter
    def spaces(self, spaces):
        if self._spaces != spaces:
            self._spaces = spaces
            self._reset_space()

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        if self._start != start:
            self._start = start
            self._reset_space()

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end):
        if self._end != end:
            self._end = end
            self._reset_space()

    @property
    def excludes(self):
        return self._excludes

    @excludes.setter
    def excludes(self, excludes):
        if self._excludes != excludes:
            self._excludes = excludes
            self._reset_space()

    @property
    def space(self):
        if self._space is None:
            self._space = self.full_space[
                self.start:self.end].translate(
                    str.maketrans('', '', self.excludes))
        return self._space

    @property
    def full_space(self):
        if self._full_space is None:
            self._full_space = ''.join([
                self._spaces_dict[tipo]
                for tipo in self.spaces
            ])
        return self._full_space

    def _reset_space(self):
        self._space = None
        self._full_space = None

    def str_to_number(self, string, base_space=None, base_size=None):
        return self.digits_to_number(
            self.str_to_digits(string, base_space=base_space),
            base_space=base_space,
            base_size=base_size,
        )

    def number_to_str(self, number, base_space=None, base_size=None):
        return self.digits_to_str(
            self.number_to_digits(number, base_space=base_space, base_size=base_size),
            base_space=base_space,
        )

    def digits_to_str(self, digits, base_space=None):
        space = base_space if base_space else self.space
        return ''.join([space[i] for i in digits])

    def str_to_digits(self, string, base_space=None):
        space = base_space if base_space else self.space
        return [space.index(char) for char in string]

    def number_to_digits(self, number, base_space=None, base_size=None):
        if number == 0:
            return [0]
        space = base_space if base_space else self.space
        if base_size is None:
            base_size = len(space)
        digits = []
        while number:
            digits.append(int(number % base_size))
            number //= base_size
        return digits[::-1]

    def digits_to_number(self, digits, base_space=None, base_size=None):
        space = base_space if base_space else self.space
        if base_size is None:
            base_size = len(space)
        number = 0
        for digit in digits:
            number = number*base_size + digit
        return number
