#!/bin/bash

# $1 : ano do mês seguinte a virada de mês
# $2 : mês seguinte a virada de mês
# $3 : arquivo a ser gerado

script/inventario.sh k $1 $2 ${3}_k200.txt
script/inventario.sh 2 $1 $2 ${3}_0200.txt
script/sped_0200_k200.py $1 $2 ${3}_k200.txt ${3}_0200.txt > ${3}_sped.txt

# gera bloco K de 02/2019
# script/sped.sh 2019 3 ../2019-02
