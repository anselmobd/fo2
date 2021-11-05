#!/bin/bash

if [ $# -ge 1 ] ; then
  DE=$1
  PARA=$1
fi

if [ $# -ge 2 ] ; then
  PARA=$2
fi

sleep 0.5

if [ $# -ge 1 ] ; then
  rm ${PARA}.pdf
  dot -Tpdf ${DE}.dot -o${PARA}.pdf
  if [ -e ${PARA}.pdf ] ; then
    evince -s ${PARA}.pdf
  fi
fi
