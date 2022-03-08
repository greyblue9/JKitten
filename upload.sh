#/bin/bash 
origdir="$( pwd )"
for f in "$@"; do
  cd "$origdir"
  f="$( realpath "$f" )"
  fn="${f##*/}"
  dir="${f: 0:${#f}-${#fn}}"; dir="${dir%%/}"
  echo "==> $f"
  cd "$dir" || continue
  host=ftp.pinproject.com
  rpath="./public_html/$fn"
  curl -kv \
    --ftp-method nocwd \
    --quote "cwd ${rpath%/*}" \
    -T "$fn" \
    "ftp://$USERNAME:$PASSWORD@$host/$rpath" \
    ; echo "[ $? ] $f" >&2;
done
​
