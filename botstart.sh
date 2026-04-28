#!/bin/bash
~/.venv/bin/pip install yt-dlp --upgrade
cd ~/sgt-reamann
git pull
git submodule update --init --recursive
exec /home/reamann/.venv/bin/python -u /home/reamann/sgt-reamann/src/main.py
