import re
from config import KEYWORDS


def matches_keywords(item):
    """항목의 제목이나 설명이 키워드와 매칭되는지 확인한다.

    단어 경계(\\b) 기준으로 검색해 substring 오매칭을 방지한다.
    예: 'AI' 키워드가 'Calvino: A Traveller'에 매칭되지 않음.
    """
    text = f"{item.get('title', '')} {item.get('description', '')}"
    for keyword in KEYWORDS:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def filter_items(items):
    """키워드에 매칭되는 항목만 반환한다."""
    return [item for item in items if matches_keywords(item)]
