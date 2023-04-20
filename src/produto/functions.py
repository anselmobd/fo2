from pprint import pprint

from utils.functions.strings import (
    clean_split_digits_alphas,
)


def papg_modelo(papg):
    modelo = ''.join(filter(str.isdigit, papg))
    return modelo.lstrip('0')


def item_str(nivel, ref, tam, cor):
    return f'{nivel}.{ref}.{tam}.{cor}'


def fill_ref(ref):
    if ref:
        parts = clean_split_digits_alphas(ref)
        if len(parts) not in (1, 2, 3):
            raise ValueError('Must have 1 to 3 all digits or all alphas parts')
        digits_len = 5
        digits_idx = 0
        digits_count = 0
        for idx, part in enumerate(parts):
            if part.isdigit():
                digits_idx = idx
                digits_idx += 1
            else:
                digits_len -= len(part)
        if digits_count != 1:
            raise ValueError('Must have 1 part all digits')
        parts[digits_idx] = parts[digits_idx].zfill(digits_len)
        ref = ''.join(parts)
    return ref
