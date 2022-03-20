#!/bin/bash

[ -e .env ] && PATH="$PWD:$PATH" builtin command . .env
exec java -Xverify:none  -cp "./lib/Ab.jar:./lib/deps.jar:./lib/" Main "$@"

