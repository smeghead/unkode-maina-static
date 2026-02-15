#!/usr/bin/env python3
"""Check/insert "全て" menu item after Cobol menu item in a single HTML file.

Anchor target (position reference):
- <li data-url_match="/lang/Cobol$">...</li>
  (child link/href/text can vary)

Inserted item:
- <li data-url_match="/lang/All$"><a href="/lang/All.html"><i class="icon-list-alt"></i>全て</a></li>

Usage:
- check <file>: verify insertion precondition in one file
- insert <file>: insert item only when exactly one Cobol exists and All does not exist

Exit codes:
- 0: success (insertable/inserted)
- 1: not insertable (missing Cobol or already has All)
- 2: ambiguous (2+ Cobol or 2+ All)
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

COBOL_SELECTOR = 'li[data-url_match="/lang/Cobol$"]'
ALL_SELECTOR = 'li[data-url_match="/lang/All$"]'


def load_html(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def save_html(path: Path, html: str) -> None:
    path.write_text(html, encoding="utf-8")


def find_cobol_items(soup: BeautifulSoup) -> list[Tag]:
    return [tag for tag in soup.select(COBOL_SELECTOR) if isinstance(tag, Tag) and tag.name == "li"]


def find_all_items(soup: BeautifulSoup) -> list[Tag]:
    return [tag for tag in soup.select(ALL_SELECTOR) if isinstance(tag, Tag) and tag.name == "li"]


def build_all_item(soup: BeautifulSoup) -> Tag:
    li = soup.new_tag("li", attrs={"data-url_match": "/lang/All$"})
    a = soup.new_tag("a", href="/lang/All.html")
    icon = soup.new_tag("i", attrs={"class": "icon-list-alt"})
    a.append(icon)
    a.append("全て")
    li.append(a)
    return li


def evaluate(cobol_count: int, all_count: int) -> int:
    if cobol_count > 1 or all_count > 1:
        return EXIT_AMBIGUOUS
    if cobol_count == 1 and all_count == 0:
        return EXIT_OK
    return EXIT_NOT_FOUND


def run_check(file_path: Path) -> int:
    try:
        soup = BeautifulSoup(load_html(file_path), "html.parser")
        cobol_items = find_cobol_items(soup)
        all_items = find_all_items(soup)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: check failed: {exc}", file=sys.stderr)
        return EXIT_ERROR

    cobol_count = len(cobol_items)
    all_count = len(all_items)
    print(f"CHECK {file_path}: cobol={cobol_count}, all={all_count}")
    return evaluate(cobol_count, all_count)


def run_insert(file_path: Path) -> int:
    try:
        soup = BeautifulSoup(load_html(file_path), "html.parser")
        cobol_items = find_cobol_items(soup)
        all_items = find_all_items(soup)

        cobol_count = len(cobol_items)
        all_count = len(all_items)
        state = evaluate(cobol_count, all_count)

        if state == EXIT_AMBIGUOUS:
            print(
                f"INSERT {file_path}: aborted (cobol={cobol_count}, all={all_count})"
            )
            return EXIT_AMBIGUOUS
        if state == EXIT_NOT_FOUND:
            print(
                f"INSERT {file_path}: skipped (cobol={cobol_count}, all={all_count})"
            )
            return EXIT_NOT_FOUND

        cobol = cobol_items[0]
        new_item = build_all_item(soup)
        cobol.insert_after(new_item)

        save_html(file_path, str(soup))
        print(f"INSERT {file_path}: inserted 1 item")
        return EXIT_OK
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: insert failed: {exc}", file=sys.stderr)
        return EXIT_ERROR


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check/insert All menu item after Cobol menu item in a single HTML file"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_check = subparsers.add_parser("check", help="check if insertion is possible")
    parser_check.add_argument("file", type=Path, help="target HTML file path")

    parser_insert = subparsers.add_parser("insert", help="insert menu item in-place")
    parser_insert.add_argument("file", type=Path, help="target HTML file path")

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
    if args.command == "insert":
        return run_insert(file_path)

    print("ERROR: unknown command", file=sys.stderr)
    return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
