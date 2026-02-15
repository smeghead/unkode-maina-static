#!/usr/bin/env python3
"""Check/convert sidebar search menu link href to local /search.html in one HTML file.

Target example:
<li data-url_match="/search"><a href="https://unkode-mania.net/search"><i class="icon-search"></i>サイト内検索</a></li>

Conversion:
- href -> /search.html

Usage:
- check <file>: report how many target links are found and how many need update
- convert <file>: rewrite target href(s) to /search.html in-place

Exit codes:
- 0: success
- 3: processing error (read/write/parse failure)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Tag

EXIT_OK = 0
EXIT_ERROR = 3

TARGET_LI_SELECTOR = 'li[data-url_match="/search"]'
TARGET_HREF = "/search.html"


def load_html(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def save_html(path: Path, html: str) -> None:
    path.write_text(html, encoding="utf-8")


def find_target_links(soup: BeautifulSoup) -> list[Tag]:
    links: list[Tag] = []
    for li in soup.select(TARGET_LI_SELECTOR):
        if not isinstance(li, Tag):
            continue

        anchor = li.find("a", href=True)
        if not isinstance(anchor, Tag):
            continue

        links.append(anchor)

    return links


def run_check(file_path: Path) -> int:
    try:
        soup = BeautifulSoup(load_html(file_path), "html.parser")
        links = find_target_links(soup)
        needs_update = sum(1 for a in links if a.get("href") != TARGET_HREF)
        print(
            f"CHECK {file_path}: target_links={len(links)}, needs_update={needs_update}"
        )
        return EXIT_OK
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: check failed: {exc}", file=sys.stderr)
        return EXIT_ERROR


def run_convert(file_path: Path) -> int:
    try:
        soup = BeautifulSoup(load_html(file_path), "html.parser")
        links = find_target_links(soup)

        converted = 0
        for anchor in links:
            if anchor.get("href") != TARGET_HREF:
                anchor["href"] = TARGET_HREF
                converted += 1

        save_html(file_path, str(soup))
        print(f"CONVERT {file_path}: converted_links={converted}, target_links={len(links)}")
        return EXIT_OK
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: convert failed: {exc}", file=sys.stderr)
        return EXIT_ERROR


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check/convert sidebar search menu href to /search.html in one HTML file"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_check = subparsers.add_parser("check", help="report target and update counts")
    parser_check.add_argument("file", type=Path, help="target HTML file path")

    parser_convert = subparsers.add_parser("convert", help="convert target href(s) in-place")
    parser_convert.add_argument("file", type=Path, help="target HTML file path")

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
    if args.command == "convert":
        return run_convert(file_path)

    print("ERROR: unknown command", file=sys.stderr)
    return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
