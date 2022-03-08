#!/bin/bash
for f in "$@" ; do [ $# -gt 1 ] && echo "==> $f" && prefix="$f"$'\t' || prefix=; unzip -Z1 "$f" "*.class" | cut -d. -f1 | tr / . | sed -r -e 's~^~'"$prefrix"'~;'; done
