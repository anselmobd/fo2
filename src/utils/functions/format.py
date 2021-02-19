from pprint import pprint


def format_cnpj(cnpj9, cnpj4=None, cnpj2=None):
    try:
        if isinstance(cnpj9, str):
            cnpj9 = int(cnpj9)
        if cnpj4:
            if isinstance(cnpj4, str):
                cnpj4 = int(cnpj4)
        if cnpj2:
            if isinstance(cnpj2, str):
                cnpj2 = int(cnpj2)
        if cnpj4 and cnpj2:
            return f"{cnpj9:08d}/{cnpj4:04d}-{cnpj2:02d}"
        else:
            cnpj = f"{cnpj9:014d}"
            return f"{cnpj[:8]}/{cnpj[8:12]}-{cnpj[12:14]}"
    except Exception:
        return ""
