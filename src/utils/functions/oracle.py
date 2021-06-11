import cx_Oracle
from pprint import pprint


__oracle_connections = {}


# https://stackoverflow.com/a/52651859/6131786
def isOpen(connectionObject):
    try:
        return connectionObject.ping() is None
    except:
        return False


def get_oracle_conn(**kwargs):
    conn, _ = get_oracle_conn_err(**kwargs)
    return conn


def get_oracle_conn_err(**kwargs):
    """Devolve um objeto de conexão com banco de dados
    oracle, se conseguir, e erro, se houver.

    Recebe uma dicionário com os parâmetros de conecção.
    """
    params = {k.upper(): v for k, v in kwargs.items()}
    try:
        engine = params['ENGINE'] if 'ENGINE' in params else ''

        if 'oracle' not in engine:
            return None, 'Engine não é  Oracle'

        host = params['HOST'] if 'HOST' in params else ''
        port = params['PORT'] if 'PORT' in params else '1521'
        name = params['NAME'] if 'NAME' in params else ''
        user = params['USER'] if 'USER' in params else ''
        password = params['PASSWORD'] if 'PASSWORD' in params else ''

        key = (host, port, name, user, password)

        if key in __oracle_connections:
            conn = __oracle_connections[key]
            if not isOpen(conn):
                print('apaga')
                del(__oracle_connections[key])

        if key not in __oracle_connections:
            print('connecta')
            if "/" in name:
                host_port, name = tuple(name.split("/"))
                if ":" in host_port:
                    host, port = tuple(host_port.split(":"))
                else:
                    host = host_port

            dsn_tns = cx_Oracle.makedsn(
                host,
                port,
                service_name=name,
            )

            conn = cx_Oracle.connect(
                user=user,
                password=password,
                dsn=dsn_tns
            )

            __oracle_connections[key] = conn

        return __oracle_connections[key], None

    except Exception as e:
        return None, e
