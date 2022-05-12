from pprint import pprint


def muda_senha_usuario(cursor, empresa, usuario, senha):
    try:
        sql = f"""
            UPDATE HDOC_030 u -- usuários
            SET
               u.SENHA = {senha}
            WHERE u.EMPRESA = '{empresa}'
              AND u.USUARIO = '{usuario}'
        """
        cursor.execute(sql)
        return True
    except Exception:
        return False
