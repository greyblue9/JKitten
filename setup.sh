#!/bin/bash

[ -e venv/bin/python ] || {
	python3 -m venv venv
}

disnake_installed=0
bs4_installed=0

venv/bin/python -c "import disnake" 2>/dev/null &&  disnake_installed=1
venv/bin/python -c "import bs4" 2>/dev/null  && bs4_installed=1
echo "disnake_installed = $disnake_installed" 1>&2
echo "bs4_installed = $bs4_installed" 1>&2

if (( ! disnake_installed || !  bs4_installed )); then
	echo "Installing requirements..."
    rm -rf -- venv
    echo Creating venv...
    python3 -m venv venv 
    echo Installing...
    venv/bin/python -m pip install --pre wheel
	venv/bin/python -m pip install -r requirements.txt
    
	venv/bin/python -c "import disnake" 2>/dev/null &&  disnake_installed=1
	venv/bin/python -c "import bs4" 2>/dev/null  && bs4_installed=1
	echo "disnake_instaled = $disnake_installed" 1>&2
	echo "bs4_instaled = $bs4_installed" 1>&2
    if ! (( disnake_installed && bs4_installed )); then
        rm -rf -- venv
        exit 255
    fi
    venv/bin/python -m spacy download en_core_web_md
fi

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

