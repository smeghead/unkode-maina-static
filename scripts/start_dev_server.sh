#!/usr/bin/bash
script_dir="$(dirname "$0")"
python3 -m http.server 8000 --directory $script_dir/../docs