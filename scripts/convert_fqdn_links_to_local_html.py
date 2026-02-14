#!/usr/bin/env python3
"""Check/convert unkode-mania FQDN links to local .html paths in one HTML file.

Examples:
- https://unkode-mania.net/about      -> /about.html
- https://unkode-mania.net/lang/C     -> /lang/C.html
- https://unkode-mania.net/view/abcd  -> /view/abcd.html

Notes:
- 0 matches is not an error.
- 2+ matches is not an error.

Usage:
- check  <file>: report how many links are convertible
- convert <file>: rewrite convertible links in-place

Exit codes:
- 0: success
- 3: processing error (read/write/parse failure)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup, Tag

EXIT_OK = 0
EXIT_ERROR = 3

TARGET_HOSTS = {"unkode-mania.net", "www.unkode-mania.net"}

TOP_LEVEL_ROUTES = {
    "/",
    "/index",
    "/about",
    "/hot",
    "/legend",
    "/new",
    "/new_comments",
    "/ranking",
}

LANG_ROUTE_RE = re.compile(r"^/lang/[^/]+$")
VIEW_ROUTE_RE = re.compile(r"^/view/[A-Za-z0-9]+$")


def load_html(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def save_html(path: Path, html: str) -> None:
    path.write_text(html, encoding="utf-8")


def to_local_html_href(href: str) -> str | None:
    parts = urlsplit(href)
    if parts.scheme not in {"http", "https"}:
        return None

    host = parts.netloc.lower()
    if host not in TARGET_HOSTS:
        return None

    path = parts.path or "/"

    if path == "/":
        local_path = "/index.html"
    elif path in TOP_LEVEL_ROUTES:
        local_path = "/index.html" if path == "/index" else f"{path}.html"
    elif LANG_ROUTE_RE.match(path):
        local_path = f"{path}.html"
    elif VIEW_ROUTE_RE.match(path):
        local_path = f"{path}.html"
    else:
        return None

    return urlunsplit(("", "", local_path, parts.query, parts.fragment))


def find_convertible_links(soup: BeautifulSoup) -> list[tuple[Tag, str, str]]:
    matches: list[tuple[Tag, str, str]] = []
    for anchor in soup.find_all("a", href=True):
        if not isinstance(anchor, Tag):
            continue

        old_href = anchor.get("href")
        if not isinstance(old_href, str):
            continue

        new_href = to_local_html_href(old_href)
        if new_href is None:
            continue

        if old_href != new_href:
            matches.append((anchor, old_href, new_href))

    return matches


def run_check(file_path: Path) -> int:
    try:
        soup = BeautifulSoup(load_html(file_path), "html.parser")
        matches = find_convertible_links(soup)
        print(f"CHECK {file_path}: convertible_links={len(matches)}")
        return EXIT_OK
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: check failed: {exc}", file=sys.stderr)
        return EXIT_ERROR


def run_convert(file_path: Path) -> int:
    try:
        soup = BeautifulSoup(load_html(file_path), "html.parser")
        matches = find_convertible_links(soup)

        for anchor, _old_href, new_href in matches:
            anchor["href"] = new_href

        save_html(file_path, str(soup))
        print(f"CONVERT {file_path}: converted_links={len(matches)}")
        return EXIT_OK
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: convert failed: {exc}", file=sys.stderr)
        return EXIT_ERROR


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check/convert unkode-mania FQDN links to local .html paths in one HTML file"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_check = subparsers.add_parser("check", help="report convertible link count")
    parser_check.add_argument("file", type=Path, help="target HTML file path")

    parser_convert = subparsers.add_parser("convert", help="convert links in-place")
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
