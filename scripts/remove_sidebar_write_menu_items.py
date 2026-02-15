#!/usr/bin/env python3
"""Check/delete sidebar "ウンコードを書く" menu items in a single HTML file.

Targets:
- <li class="nav-header">ウンコードを書く</li>
- <li data-url_match="/register"><a class="register-link" ...>投稿する</a></li>

Usage:
- check <file>: verify both targets exist exactly once
- delete <file>: remove both targets only when each exists exactly once

Exit codes:
- 0: success
- 1: missing target(s)
- 2: ambiguous target(s) (2+ matches)
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


def load_html(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def save_html(path: Path, html: str) -> None:
    path.write_text(html, encoding="utf-8")


def find_write_header(soup: BeautifulSoup) -> list[Tag]:
    matches: list[Tag] = []
    for li in soup.select("li.nav-header"):
        if not isinstance(li, Tag):
            continue
        if li.get_text(" ", strip=True) == "ウンコードを書く":
            matches.append(li)
    return matches


def find_register_item(soup: BeautifulSoup) -> list[Tag]:
    matches: list[Tag] = []
    for li in soup.select('li[data-url_match="/register"]'):
        if not isinstance(li, Tag) or li.name != "li":
            continue

        anchor = li.select_one("a.register-link")
        if not isinstance(anchor, Tag):
            continue

        if anchor.get_text(" ", strip=True) == "投稿する":
            matches.append(li)

    return matches


def find_targets(soup: BeautifulSoup) -> dict[str, list[Tag]]:
    return {
        "write_header": find_write_header(soup),
        "register_item": find_register_item(soup),
    }


def summarize(found: dict[str, list[Tag]]) -> tuple[int, int]:
    missing = 0
    ambiguous = 0
    for tags in found.values():
        count = len(tags)
        if count == 0:
            missing += 1
        elif count > 1:
            ambiguous += 1
    return missing, ambiguous


def run_check(file_path: Path) -> int:
    try:
        soup = BeautifulSoup(load_html(file_path), "html.parser")
        found = find_targets(soup)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: check failed: {exc}", file=sys.stderr)
        return EXIT_ERROR

    counts = ", ".join(f"{name}={len(tags)}" for name, tags in found.items())
    print(f"CHECK {file_path}: {counts}")

    missing, ambiguous = summarize(found)
    if ambiguous > 0:
        return EXIT_AMBIGUOUS
    if missing > 0:
        return EXIT_NOT_FOUND
    return EXIT_OK


def run_delete(file_path: Path) -> int:
    try:
        soup = BeautifulSoup(load_html(file_path), "html.parser")
        found = find_targets(soup)

        missing, ambiguous = summarize(found)
        counts = ", ".join(f"{name}={len(tags)}" for name, tags in found.items())

        if ambiguous > 0:
            print(f"DELETE {file_path}: aborted ({counts})")
            return EXIT_AMBIGUOUS
        if missing > 0:
            print(f"DELETE {file_path}: skipped ({counts})")
            return EXIT_NOT_FOUND

        found["write_header"][0].decompose()
        found["register_item"][0].decompose()

        save_html(file_path, str(soup))
        print(f"DELETE {file_path}: removed 2 items")
        return EXIT_OK
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: delete failed: {exc}", file=sys.stderr)
        return EXIT_ERROR


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check/delete sidebar write-menu items in a single HTML file"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_check = subparsers.add_parser("check", help="check if both targets exist")
    parser_check.add_argument("file", type=Path, help="target HTML file path")

    parser_delete = subparsers.add_parser(
        "delete", help="delete both targets when each exists exactly once"
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
