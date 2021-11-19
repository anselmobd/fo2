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
  rm pdf/${PARA}.pdf
  dot -Tpdf ${DE}.dot -opdf/${PARA}.pdf
  pdfjam --outfile pdf/a4_${PARA}.pdf --paper a4paper pdf/${PARA}.pdf
  if [ -e pdf/${PARA}.pdf ] ; then
    evince -s pdf/a4_${PARA}.pdf
  fi
fi
