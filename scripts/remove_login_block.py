#!/usr/bin/env python3
"""Remove login button block (`div.btn-group.pull-right`) from a single HTML file.

This script provides two modes for one file at a time:
- check: verify the number of target blocks in the file
- delete: remove the target block only when exactly one block is found

Exit codes:
- 0: success
- 1: target not found (0 matches)
- 2: ambiguous (2+ matches)
- 3: processing error (read/write/parse failure)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Tag

EXIT_OK = 0
EXIT_NOT_FOUND = 1
EXIT_AMBIGUOUS = 2
EXIT_ERROR = 3

TARGET_SELECTOR = "div.btn-group.pull-right"


def load_html(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def save_html(path: Path, html: str) -> None:
    path.write_text(html, encoding="utf-8")


def is_login_block(tag: Tag) -> bool:
    # Safety guard: treat only blocks that actually include auth link/text.
    auth_link = tag.select_one('a[href*="/auth"]')
    has_signin_text = "Twitterでサインイン" in tag.get_text(" ", strip=True)
    return auth_link is not None or has_signin_text


def find_targets(soup: BeautifulSoup) -> list[Tag]:
    candidates = soup.select(TARGET_SELECTOR)
    return [tag for tag in candidates if isinstance(tag, Tag) and is_login_block(tag)]


def run_check(file_path: Path) -> int:
    try:
        html = load_html(file_path)
        soup = BeautifulSoup(html, "html.parser")
        targets = find_targets(soup)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: check failed: {exc}", file=sys.stderr)
        return EXIT_ERROR

    count = len(targets)
    print(f"CHECK {file_path}: matches={count}")

    if count == 1:
        return EXIT_OK
    if count == 0:
        return EXIT_NOT_FOUND
    return EXIT_AMBIGUOUS


def run_delete(file_path: Path) -> int:
    try:
        html = load_html(file_path)
        soup = BeautifulSoup(html, "html.parser")
        targets = find_targets(soup)

        count = len(targets)
        if count == 0:
            print(f"DELETE {file_path}: skipped (matches=0)")
            return EXIT_NOT_FOUND
        if count > 1:
            print(f"DELETE {file_path}: aborted (matches={count})")
            return EXIT_AMBIGUOUS

        targets[0].decompose()
        save_html(file_path, str(soup))
        print(f"DELETE {file_path}: removed 1 block")
        return EXIT_OK
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: delete failed: {exc}", file=sys.stderr)
        return EXIT_ERROR


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check/delete login button block in a single HTML file"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_check = subparsers.add_parser("check", help="check if exactly one target exists")
    parser_check.add_argument("file", type=Path, help="target HTML file path")

    parser_delete = subparsers.add_parser(
        "delete", help="delete target only when exactly one exists"
    )
    parser_delete.add_argument("file", type=Path, help="target HTML file path")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    file_path: Path = args.file
    if not file_path.exists() or not file_path.is_file():
        print(f"ERROR: file not found: {file_path}", file=sys.stderr)
        return EXIT_ERROR

    if args.command == "check":
        return run_check(file_path)
    if args.command == "delete":
        return run_delete(file_path)

    print("ERROR: unknown command", file=sys.stderr)
    return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
