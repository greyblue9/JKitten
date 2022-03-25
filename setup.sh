#!/bin/bash

[ -e venv/bin/python ] || {
	python3 -m venv venv
}
nextcord_installed=0
for d in venv/lib/python3.*; do 
	for sd in "$d/site-packages/nextcord-"*.*-info; do
		nextcord_installed=1
	done
done
echo "nextcord_instaled = $nextcord_installed" 1>&2

(( nextcord_installed )) || {
	echo "Installing requirements..."
	venv/bin/python -m pip install --upgrade --pre -r requirements.txt 
}

set -e
srcdate=$( find src -name "*.java" -exec stat -t -- {} + | cut -d" " -f12 | sort -n | tail -1; )
libdate=$( stat -t -- lib/Ab.jar | cut -d" " -f12 || echo 0; )
echo "srcdate=$srcdate libdate=$libdate"
if [ $libdate -le $srcdate ]; then
  echo "Build is out of date ($libdate) with source ($srcdate)" >&2
  bash ./build.sh || exit $?
else
  echo "Build is up-to-date ($libdate) with source ($srcdate)" >&2
fi || true

