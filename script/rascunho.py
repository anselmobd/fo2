from pprint import pprint
from inventario import *

ora = Oracle()
ora.connect()

sql = """
   SELECT
     u.USUARIO
   FROM HDOC_030 u
   WHERE u.CODIGO_USUARIO = :codigo
"""

data, fields = ora.execute(sql, codigo=99101)
pprint(data)
pprint(fields)

for f in fields:
    print(f)

pprint(set(fields))
pprint(list(fields))
