#!/bin/sh

set -- $( ps -aux | tr -s " " " " | cut -d" " -f 2 | grep -vEe $$ -e "^[0-9]{1,2}" -e $PPID -e 1 -w -e PID );
echo $# $@
kill -9 $@


