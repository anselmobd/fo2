from pprint import pprint
import fdb

con = fdb.connect(
    dsn='192.168.1.98/3050:/dados/db/f1/f1.cdb',
    user='sysdba',
    password='1firebir'
)

# help(con.database_info)

bytesInUse = con.database_info(fdb.isc_info_current_memory, 'i')
pprint(bytesInUse)

# buf = con.database_info(fdb.isc_info_db_id, 'i')

print(con.db_info(fdb.isc_info_user_names))

cur = con.cursor()
sql = """
    SELECT FIRST 10000
      c.C_CGC CNPJ
    , c.C_RSOC CLIENTE
    FROM DIS_CLI c
    WHERE c.C_RSOC CONTAINING 'RENNER'
    ORDER BY
      c.C_CGC
"""

cur.execute(sql)
for row in cur:
    pprint(row)
