#!/usr/bin/env python3
"""Repair common unescaped quote issues in generated JSON string values."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path


KEY_VALUE_PREFIX = re.compile(r'^(\s*"[^"]+"\s*:\s*)"(.*)$')
ARRAY_VALUE_PREFIX = re.compile(r'^(\s*)"(.*)$')
STRING_SUFFIX = re.compile(r'"(\s*,?\s*)$')


def is_ascii_alnum(char: str) -> bool:
    return char.isascii() and char.isalnum()


def should_convert_punctuation(text: str, index: int) -> bool:
    char = text[index]
    prev_char = text[index - 1] if index > 0 else ""
    next_char = text[index + 1] if index + 1 < len(text) else ""

    if char == ",":
        return not (prev_char.isdigit() and next_char.isdigit())
    if char == ":":
        if prev_char.isdigit() and next_char.isdigit():
            return False
        if next_char in "/\\":
            return False
        if is_ascii_alnum(prev_char) and (is_ascii_alnum(next_char) or next_char in "._-"):
            return False
    return True


def replace_inner_quotes(text: str) -> tuple[str, int]:
    changed = 0
    punctuation_replacements = {
        ",": "，",
        ":": "：",
        ";": "；",
        "?": "？",
        "!": "！",
        "(": "（",
        ")": "）",
    }

    output: list[str] = []
    ascii_double_quote_index = 0
    ascii_single_quote_index = 0
    escaped = False
    for index, char in enumerate(text):
        if char == "\\" and not escaped:
            escaped = True
            output.append(char)
            continue
        if char == '"' and not escaped:
            output.append("“" if ascii_double_quote_index % 2 == 0 else "”")
            ascii_double_quote_index += 1
            changed += 1
        elif char == "'" and not escaped:
            output.append("‘" if ascii_single_quote_index % 2 == 0 else "’")
            ascii_single_quote_index += 1
            changed += 1
        elif char in punctuation_replacements and should_convert_punctuation(text, index):
            output.append(punctuation_replacements[char])
            changed += 1
        else:
            output.append(char)
        escaped = False
    return "".join(output), changed


def repair_line(line: str) -> tuple[str, int]:
    match = KEY_VALUE_PREFIX.match(line) or ARRAY_VALUE_PREFIX.match(line)
    if not match:
        return line, 0

    prefix, rest = match.groups()
    suffix_match = STRING_SUFFIX.search(rest)
    if not suffix_match:
        return line, 0

    suffix = suffix_match.group(1)
    content = rest[: suffix_match.start()]
    repaired, changed = replace_inner_quotes(content)
    if not changed:
        return line, 0
    return f'{prefix}"{repaired}"{suffix}', changed


def repair_text(text: str) -> tuple[str, int]:
    lines = text.splitlines(keepends=True)
    repaired_lines = []
    changed = 0
    for line in lines:
        ending = ""
        body = line
        if line.endswith("\r\n"):
            body = line[:-2]
            ending = "\r\n"
        elif line.endswith("\n"):
            body = line[:-1]
            ending = "\n"
        repaired, line_changed = repair_line(body)
        repaired_lines.append(repaired + ending)
        changed += line_changed
    return "".join(repaired_lines), changed


def validate_json(text: str, path: Path) -> None:
    try:
        json.loads(text)
    except json.JSONDecodeError as error:
        raise SystemExit(
            f"{path}: JSON still invalid at line {error.lineno}, col {error.colno}: {error.msg}"
        ) from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path, help="JSON file to inspect or repair")
    parser.add_argument("--write", action="store_true", help="Write repairs back to the file")
    parser.add_argument("--no-backup", action="store_true", help="Do not create a .bak file when writing")
    args = parser.parse_args()

    original = args.json_file.read_text(encoding="utf-8")
    repaired, changed = repair_text(original)
    validate_json(repaired, args.json_file)

    if not args.write:
        print(f"{args.json_file}: JSON valid after repair scan; replacements={changed}; dry-run")
        return 0

    if repaired == original:
        print(f"{args.json_file}: no changes needed")
        return 0

    if not args.no_backup:
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup = args.json_file.with_suffix(args.json_file.suffix + f".{stamp}.bak")
        shutil.copy2(args.json_file, backup)
        print(f"backup: {backup}")

    args.json_file.write_text(repaired, encoding="utf-8")
    print(f"{args.json_file}: repaired replacements={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
