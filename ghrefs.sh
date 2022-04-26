#!/usr/local/bin/mksh-static-printf
  
user="$1"
shift
if [ "x${user#*/}" != "x$user" ]; then
  proj="${user#*/}"
  user="${user%/*}"
else
  proj="$1"
  shift
fi
[ $# -ge 4 ] && ref="$1" && shift
[ $# -ge 3 ] && language="$1" && shift
ref="HEAD"
[ $# -ge 2 ] && blob_path="$1" && shift
[ $# -ge 1 ] && q="$1" && shift
blob_path_esc="${blob_path//\//%2F}"
code_nav_context="BLOB_VIEW"
if [ "x${blob_path##*.}" != py ]; then
  : ${language:=C}
else
  : ${language:=Python}
fi
: ${row:=1} ${col:=1}

curl \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0' \
  -H 'Accept: text/html' \
  -H "Referer: https://github.com/$user/$proj/blob/HEAD/$blob_path" \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H "Cookie: _octo=GH1.1.823628375.1617955053; logged_in=yes; _device_id=2cf285ed41ecf16748081feaa8643e4c; tz=America%2FNew_York; ${ github_cookies | sed -r -e ":a s!/!%2F!g; s!;([^ ])!%3B\1!g; ta; s!=!%DA!g; s!\ }!%26!g; " }" \
  "$@" \
  "https://github.com/${user}/${proj}/find-references?backend=ALPHA_FUZZY&blob_path=${blob_path_esc}&code_nav_context=${code_nav_context}&col=${col}&language=${language}&q=${q}&ref=${ref}&row=${row}" \
