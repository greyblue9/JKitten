#!/usr/local/bin/mksh-static-printf

[ -e .env ] && PATH="$PWD:$PATH" builtin command . .env
exec rlwrapi java -Xverify:none  -cp "./lib/Ab.jar:./lib/deps.jar:./lib/jackson-core-2.2.3.jar" Main "$@"

