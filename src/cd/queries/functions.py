from pprint import pprint

import lotes.models


def where_ende_disponivel(campo):
    filter_local = ""

    end_disp = list(lotes.models.EnderecoDisponivel.objects.filter(disponivel=True).values())
    if len(end_disp) != 0:
        filter_end = """--
            AND l.local ~ '^("""
        filter_sep = ""
        for regra in end_disp:
            filter_end += f"{filter_sep}{regra['inicio']}"
            filter_sep = "|"
        filter_local += filter_end + """).*'
        """

    end_indisp = list(lotes.models.EnderecoDisponivel.objects.filter(disponivel=False).values())
    if len(end_indisp) != 0:
        filter_end = """--
            AND l.local !~ '("""
        filter_sep = ""
        for regra in end_indisp:
            filter_end += f"{filter_sep}{regra['inicio']}"
            filter_sep = "|"
        filter_local += filter_end + """)'
        """
    return filter_local
