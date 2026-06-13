#!/usr/bin/env python3
"""Shared display helpers for bilingual labels and titles."""

from __future__ import annotations

import re


CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def is_mostly_cjk(text: str | None) -> bool:
    if not text:
        return False
    chars = [char for char in text.strip() if not char.isspace()]
    if not chars:
        return False
    cjk_count = sum(1 for char in chars if "\u4e00" <= char <= "\u9fff")
    return cjk_count / len(chars) > 0.5


def format_bilingual_title(zh: str | None, en: str | None) -> str:
    zh_text = (zh or "").strip()
    en_text = (en or "").strip()
    if not zh_text:
        return en_text
    if not en_text:
        return zh_text
    if zh_text == en_text:
        return zh_text
    if is_mostly_cjk(en_text):
        return zh_text
    return f"{zh_text} / {en_text}"


def normalize_bilingual_text(zh: str | None, en: str | None) -> str:
    zh_text = (zh or "").strip()
    en_text = (en or "").strip()
    if not en_text:
        return ""
    if zh_text and en_text == zh_text:
        return ""
    if is_mostly_cjk(en_text):
        return ""
    return en_text
