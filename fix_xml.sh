#!/usr/bin/env zsh
for f in **/*.aiml; do xmllint "$f" >/dev/null 2>&1 && continue;  xmllint --recover  "$f" > t  && cp -vf -- "t" "$f" && touch "$f"; done

