from pprint import pprint


def format_cnpj(cnpj9, cnpj4=None, cnpj2=None, tamanho=14):
    try:
        if isinstance(cnpj9, dict):
            cnpj4 = cnpj9[[k for k in cnpj9 if "CNPJ" in k.upper() and "4" in k][0]]
            cnpj2 = cnpj9[[k for k in cnpj9 if "CNPJ" in k.upper() and "2" in k][0]]
            cnpj9 = cnpj9[[k for k in cnpj9 if "CNPJ" in k.upper() and "9" in k][0]]
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
                return f"{cnpj9:08d}/{cnpj4:04d}-{cnpj2:02d}"
            else:
                return f"{cnpj9:09d}/{cnpj4:04d}-{cnpj2:02d}"
        else:
            if tamanho == 14:
                cnpj = f"{cnpj9:014d}"
                return f"{cnpj[:8]}/{cnpj[8:12]}-{cnpj[12:14]}"
            else:
                cnpj = f"{cnpj9:015d}"
                return f"{cnpj[:9]}/{cnpj[9:13]}-{cnpj[13:15]}"
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
