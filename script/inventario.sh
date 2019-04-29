#!/bin/bash

script/inventario.py s k $1 $2 2    >  $3
script/inventario.py s k $1 $2 9 -p >> $3
script/inventario.py f k $1 $2 1 -p >> $3

