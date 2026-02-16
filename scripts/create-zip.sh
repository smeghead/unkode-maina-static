#! /usr/bin/bash
set -euo pipefail
script_dir="$(cd "$(dirname "$0")" && pwd)"
archive_path="$script_dir/../docs.zip"

if [ -f "$archive_path" ]; then
	rm -f "$archive_path"
fi

(
  cd $script_dir/../docs && zip -r ../docs.zip .
)

