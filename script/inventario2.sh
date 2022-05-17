#!/bin/bash

# $1 : i = inventário; k = k200; 2 = 0200
# $2 : ano do mês seguinte a virada de mês
# $3 : mês seguinte a virada de mês
# $4 : arquivo a ser gerado

script/inventario2.py p $1 $2 $3 2 -c $5   >  $4 
script/inventario2.py p $1 $2 $3 9 -c $6 -p >> $4
script/inventario.py f $1 $2 $3 1 -p >> $4

# gera inventário 2018
# script/inventario.sh i 2019 1 ../2018_inventario.csv

# gera bloco K200 de 01/2019
# script/inventario.sh k 2019 2 ../2019-01_K200.txt

# gera bloco 0200 de 01/2019
# script/inventario.sh 2 2019 2 ../2019-01_0200.txt
