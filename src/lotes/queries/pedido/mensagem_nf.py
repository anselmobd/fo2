from pprint import pprint

from o2.functions.text import split_size_by_char

__all__=['cria_mens_nf']


def cria_mens_nf(cursor, codigo, mensagem):
    if isinstance(mensagem, str):
        mensagem = (mensagem, )
    linhas = []
    for linha in map(str.strip, mensagem):
        while linha:
            before, linha = split_size_by_char(linha, 100)
            if before:
                linhas.append(before)
    linhas += [' ']*10
    
    apaga_mens_nf(cursor, codigo)

    sql = f"""
        INSERT INTO SYSTEXTIL.OBRF_874
        (COD_MENSAGEM, TIP_MENSAGEM, IND_LOCAL, MSG_INFORMAR, DES_MENSAGEM1, DES_MENSAGEM2, DES_MENSAGEM3, DES_MENSAGEM4, DES_MENSAGEM5, DES_MENSAGEM6, DES_MENSAGEM7, DES_MENSAGEM8, DES_MENSAGEM9, DES_MENSAGEM10, MSG_DEFAULT, PERTENCE_REG_1921)
        VALUES({codigo}, 'C', 'D', 'S', '{linhas[0]}', '{linhas[1]}', '{linhas[2]}', '{linhas[3]}', '{linhas[4]}', '{linhas[5]}', '{linhas[6]}', '{linhas[7]}', '{linhas[8]}', '{linhas[9]}', 'N', 'N')
    """
    cursor.execute(sql)


def apaga_mens_nf(cursor, codigo):
    sql = f"""
        DELETE FROM SYSTEXTIL.OBRF_874
        WHERE COD_MENSAGEM = {codigo}
    """
    cursor.execute(sql)
