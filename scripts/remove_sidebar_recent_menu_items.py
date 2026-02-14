#!/usr/bin/env python3
"""Check/delete sidebar menu items (hot/new/new_comments) in a single HTML file.

Targets:
- 人気ウンコード: <li data-url_match="/hot"><a href="hot.html">...
- 新着ウンコード: <li data-url_match="/new$"><a href="new.html">...
- 新着コメント: <li data-url_match="/new_comments"><a href="new_comments.html">...

Usage:
- check: verify each target exists exactly once
- delete: remove all three targets only when each exists exactly once

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

TARGETS: tuple[tuple[str, str, str], ...] = (
    ("hot", 'li[data-url_match="/hot"]', "人気ウンコード"),
    ("new", 'li[data-url_match="/new$"]', "新着ウンコード"),
    (
        "new_comments",
        'li[data-url_match="/new_comments"]',
        "新着コメント",
    ),
)


def load_html(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def save_html(path: Path, html: str) -> None:
    path.write_text(html, encoding="utf-8")


def find_target_items(soup: BeautifulSoup) -> dict[str, list[Tag]]:
    found: dict[str, list[Tag]] = {}
    for name, li_selector, expected_link_text in TARGETS:
        lis: list[Tag] = []
        for li in soup.select(li_selector):
            if not isinstance(li, Tag) or li.name != "li":
                continue

            anchor = li.find("a", href=True)
            if not isinstance(anchor, Tag):
                continue

            link_text = anchor.get_text(" ", strip=True)
            if link_text == expected_link_text:
                lis.append(li)

        found[name] = lis
    return found


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
        found = find_target_items(soup)
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
        found = find_target_items(soup)

        missing, ambiguous = summarize(found)
        counts = ", ".join(f"{name}={len(tags)}" for name, tags in found.items())

        if ambiguous > 0:
            print(f"DELETE {file_path}: aborted ({counts})")
            return EXIT_AMBIGUOUS
        if missing > 0:
            print(f"DELETE {file_path}: skipped ({counts})")
            return EXIT_NOT_FOUND

        for tags in found.values():
            tags[0].decompose()

        save_html(file_path, str(soup))
        print(f"DELETE {file_path}: removed 3 items")
        return EXIT_OK
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: delete failed: {exc}", file=sys.stderr)
        return EXIT_ERROR


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check/delete sidebar menu items: hot/new/new_comments in a single HTML file"
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_check = subparsers.add_parser("check", help="check if all three targets exist")
    parser_check.add_argument("file", type=Path, help="target HTML file path")

    parser_delete = subparsers.add_parser(
        "delete", help="delete all three targets when each exists exactly once"
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
