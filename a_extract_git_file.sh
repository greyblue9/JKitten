#!/bin/bash

IFS=$'\n'; revs=($( git rev-list --all --objects | grep -e "commands/Chat" -e ' $'  | sed -r -e '\~ $~{ h; d;}; s~^[^ ]+ ~~; G; s~^(.*)\n(.*) ~\2:\1~g;' ));

IFS=$'\n'; revs=($( git rev-list --all --objects | grep -e "commands/Chat" -e ' $'  | sed -r -e '\~ $~{ h; d;}; G; s~^(.*)\n([^ ]*)[\t\n ]*([^ ]+)~\2\3:\1~g; ' ));
# eg. "b64daacf0935fe56646ede0429227fded8971e5a:0c89f344cea3266f610d273fd18dba7c53d15437 commands/Chat.py"

mkdir -p blobs

for ln in "${revs[@]}"; do
  ln="${ln%% }"
  tree="${ln%%:*}"
  rest="${ln: ${#tree}+1}"
  sha="${rest%% *}"
  name="${rest: ${#sha}+1}"
  ext="${name##*.}"
  [ "x$ext" = "x$name" ] && ext="" || ext=".${ext}"
  echo "# Tree: $tree / SHA: $sha / Name: $name"
  outf="blobs/${tree}_${sha}${ext}"
  echo "writing [$outf] ..."
  git --no-pager show "$tree:$name" > "$outf"
done

