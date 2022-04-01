#!/bin/bash

[ -e .env ] && \
eval "$( sed -s -r -e ':a s~^[^ =]\ ([^ =]+)~\1~; ta; s~ *= *~=~; s~^([a-zA-Z0-9_]+)=~export \1=~; s~^([^=]+)=([^=]+)$~\1="\2"~; ' ./.env; )"
: ${PYTHON:=python3}
eval "python=( $PYTHON )"

command "${python[@]}" ./main54.py

