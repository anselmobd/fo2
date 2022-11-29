from pprint import pprint


def format_cnpj(row, cnpj4=None, cnpj2=None, tamanho=14, sep=True, contain=None):
    try:
        barra = "/" if sep else ''
        menos = "-" if sep else ''
        if isinstance(row, dict):
            for k in row:
                ku = k.upper()
                parts = (contain.upper(), ) if contain else ('CNPJ', 'CGC')
                can_be = any(part in ku for part in parts)
                if can_be:
                    if "4" in k:
                        cnpj4 = row[k]
                    elif "2" in k:
                        cnpj2 = row[k]
                    elif "9" in k:
                        cnpj9 = row[k]
        else:
            cnpj9 = row
        if isinstance(cnpj9, str):
            cnpj9 = int(cnpj9)
        if cnpj4:
            if isinstance(cnpj4, str):
                cnpj4 = int(cnpj4)
        if cnpj2:
            if isinstance(cnpj2, str):
                cnpj2 = int(cnpj2)
        if cnpj4 and cnpj2:
            if tamanho == 14:
                return f"{cnpj9:08d}{barra}{cnpj4:04d}{menos}{cnpj2:02d}"
            else:
                return f"{cnpj9:09d}{barra}{cnpj4:04d}{menos}{cnpj2:02d}"
        else:
            if tamanho == 14:
                cnpj = f"{cnpj9:014d}"
                return f"{cnpj[:8]}{barra}{cnpj[8:12]}{menos}{cnpj[12:14]}"
            else:
                cnpj = f"{cnpj9:015d}"
                return f"{cnpj[:9]}{barra}{cnpj[9:13]}{menos}{cnpj[13:15]}"
    except Exception:
        return ""

def format_cpf(cpf9, cpf2=None):
    try:
        if isinstance(cpf9, str):
            cpf9 = int(cpf9)
        if cpf2:
            if isinstance(cpf2, str):
                cpf2 = int(cpf2)
        if cpf2:
            return f"{cpf9:09d}-{cpf2:02d}"
        else:
            cpf = f"{cpf9:011d}"
            return f"{cpf[:9]}-{cpf[9:11]}"
    except Exception:
        return ""
