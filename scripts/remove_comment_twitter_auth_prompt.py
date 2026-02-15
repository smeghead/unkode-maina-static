#!/usr/bin/env python3
"""Check/delete comment Twitter-auth prompt blocks in a single HTML file.

Targets:
- <p>コメント投稿には、twitter認証が必要です。</p>
- <a class="btn btn-primary" href="https://unkode-mania.net/auth">Twitter認証</a>

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

from bs4 import BeautifulSoup, NavigableString, Tag

EXIT_OK = 0
EXIT_NOT_FOUND = 1
EXIT_AMBIGUOUS = 2
EXIT_ERROR = 3

COMMENT_AUTH_TEXT = "コメント投稿には、twitter認証が必要です。"
AUTH_BUTTON_TEXT = "Twitter認証"
AUTH_HREF = "https://unkode-mania.net/auth"


def load_html(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def save_html(path: Path, html: str) -> None:
    path.write_text(html, encoding="utf-8")


def is_twitter_auth_button(tag: Tag) -> bool:
    if tag.name != "a":
        return False

    if tag.get_text(" ", strip=True) != AUTH_BUTTON_TEXT:
        return False

    href = tag.get("href")
    if href != AUTH_HREF:
        return False

    classes = tag.get("class")
    if not isinstance(classes, list) or "btn" not in classes or "btn-primary" not in classes:
        return False

    return True


def next_non_whitespace_sibling(tag: Tag) -> Tag | None:
    sibling = tag.next_sibling
    while sibling is not None:
        if isinstance(sibling, NavigableString):
            if sibling.strip() == "":
                sibling = sibling.next_sibling
                continue
            return None
        if isinstance(sibling, Tag):
            return sibling
        sibling = sibling.next_sibling
    return None


def find_prompt_pairs(soup: BeautifulSoup) -> list[tuple[Tag, Tag]]:
    pairs: list[tuple[Tag, Tag]] = []
    for p in soup.find_all("p"):
        if not isinstance(p, Tag):
            continue
        if p.get_text(" ", strip=True) != COMMENT_AUTH_TEXT:
            continue

        next_tag = next_non_whitespace_sibling(p)
        if isinstance(next_tag, Tag) and is_twitter_auth_button(next_tag):
            pairs.append((p, next_tag))

    return pairs


def run_check(file_path: Path) -> int:
    try:
        soup = BeautifulSoup(load_html(file_path), "html.parser")
        pairs = find_prompt_pairs(soup)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: check failed: {exc}", file=sys.stderr)
        return EXIT_ERROR

    count = len(pairs)
    print(f"CHECK {file_path}: prompt_pair={count}")

    if count > 1:
        return EXIT_AMBIGUOUS
    if count == 0:
        return EXIT_NOT_FOUND
    return EXIT_OK


def run_delete(file_path: Path) -> int:
    try:
        soup = BeautifulSoup(load_html(file_path), "html.parser")
        pairs = find_prompt_pairs(soup)

        count = len(pairs)
        if count > 1:
            print(f"DELETE {file_path}: aborted (prompt_pair={count})")
            return EXIT_AMBIGUOUS
        if count == 0:
            print(f"DELETE {file_path}: skipped (prompt_pair=0)")
            return EXIT_NOT_FOUND

        paragraph, button = pairs[0]
        paragraph.decompose()
        button.decompose()

        save_html(file_path, str(soup))
        print(f"DELETE {file_path}: removed 1 prompt pair")
        return EXIT_OK
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: delete failed: {exc}", file=sys.stderr)
        return EXIT_ERROR


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check/delete comment Twitter-auth prompt blocks in a single HTML file"
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
