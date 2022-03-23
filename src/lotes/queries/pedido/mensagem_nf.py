from pprint import pprint

from utils.functions.models import rows_to_dict_list


def cria_mens_nf(cursor, codigo, mensagem):
    sql = f"""
        INSERT INTO SYSTEXTIL.OBRF_874
        (COD_MENSAGEM, TIP_MENSAGEM, IND_LOCAL, MSG_INFORMAR, DES_MENSAGEM1, DES_MENSAGEM2, DES_MENSAGEM3, DES_MENSAGEM4, DES_MENSAGEM5, DES_MENSAGEM6, DES_MENSAGEM7, DES_MENSAGEM8, DES_MENSAGEM9, DES_MENSAGEM10, MSG_DEFAULT, PERTENCE_REG_1921)
        VALUES({codigo}, 'C', 'D', 'S', 'TEEEEEEEESTEEEEEEE - PED. TUSSOR:', ' - PEDIDO DO CLIENTE:', ' - CONTAR VENCIMENTO A PARTIR DE 25/03/2022.', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'N', 'N');
    """
    cursor.execute(sql)


def apaga_mens_nf(cursor, codigo, mensagem):
    sql = f"""
        DELETE FROM SYSTEXTIL.OBRF_874
        (COD_MENSAGEM, TIP_MENSAGEM, IND_LOCAL, MSG_INFORMAR, DES_MENSAGEM1, DES_MENSAGEM2, DES_MENSAGEM3, DES_MENSAGEM4, DES_MENSAGEM5, DES_MENSAGEM6, DES_MENSAGEM7, DES_MENSAGEM8, DES_MENSAGEM9, DES_MENSAGEM10, MSG_DEFAULT, PERTENCE_REG_1921)
        VALUES({codigo}, 'C', 'D', 'S', ' - PED. TUSSOR:', ' - PEDIDO DO CLIENTE:', ' - CONTAR VENCIMENTO A PARTIR DE 25/03/2022.', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'N', 'N');
    """
    cursor.execute(sql)
