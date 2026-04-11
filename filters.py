import re
from config import KEYWORDS


def matches_keywords(item):
    """항목의 제목이나 설명이 키워드와 매칭되는지 확인한다."""
    text = f"{item.get('title', '')} {item.get('description', '')}".lower()
    for keyword in KEYWORDS:
        if keyword.lower() in text:
            return True
    return False


def filter_items(items):
    """키워드에 매칭되는 항목만 반환한다."""
    return [item for item in items if matches_keywords(item)]
