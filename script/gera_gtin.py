from gtin import GTIN


country = 789
company = 96188
product = 7251
quant = 127

for incr in range(quant):
    numero_gtin = '{}{}{}'.format(country, company, product+incr)
    print(str(GTIN(raw=numero_gtin)))
