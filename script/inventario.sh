#!/bin/bash

script/inventario.py s $1 $2 $3 2    >  $4
script/inventario.py s $1 $2 $3 9 -p >> $4
script/inventario.py f $1 $2 $3 1 -p >> $4
