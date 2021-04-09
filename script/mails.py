import pandas as pd

mails = pd.read_csv('../clientes.csv', sep=";", nrows=5)  
print(mails.head())

col1 = mails[['NOME_CLIENTE', 'E_MAIL']]
print(col1)

col2 = mails[['NOME_CLIENTE', 'NFE_E_MAIL']]
col2 = col2.rename(columns={"NFE_E_MAIL": "E_MAIL"})
print(col2)

col = pd.concat([col1, col2], ignore_index=True)
print(col)

# print('sort_values')
# col = col.sort_values(['NOME_CLIENTE', 'E_MAIL'])
# print(col)

print('drop_duplicates')
col = col.drop_duplicates(subset =None, keep = 'first')
print(col)

col = col.reset_index()
print(col)

col["E_MAIL"] = col["E_MAIL"].str.split(",")
print(col)

col = col.apply( pd.Series.explode )
print(col)

col["E_MAIL"] = col["E_MAIL"].str.strip()
print(col)

print('drop_duplicates')
col = col.drop_duplicates(subset =None, keep = 'first')
print(col)

col = col.reset_index()
print(col)

col["E_MAIL"] = col["E_MAIL"].str.split(";")
print(col)

col = col.apply( pd.Series.explode )
print(col)

col["E_MAIL"] = col["E_MAIL"].str.strip()
print(col)

print('drop_duplicates')
col = col.drop_duplicates(subset =None, keep = 'first')
print(col)




# # col = col.set_index(['NOME_CLIENTE'])
# # print(col)

# col = col.stack()
# print(col)

# col = col.str.split(',', expand=True)
# print(col)

# col = col.stack()
# print(col)

# col = col.unstack(-2)
# print(col)

# col = col.reset_index(-1, drop=True)
# print(col)

# col = col.reset_index()
# print(col)




# (col.set_index(['NOME_CLIENTE'])
#    .stack()
#    .str.split(',', expand=True)
#    .stack()
#    .unstack(-2)
#    .reset_index(-1, drop=True)
#    .reset_index()
# )
