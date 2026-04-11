import json
from datetime import datetime, timedelta
from config import SENT_FILE, DEDUP_RETENTION_DAYS


def load_sent():
    """sent.json에서 기존 전송 목록을 불러온다."""
    if not SENT_FILE.exists():
        return []
    with open(SENT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_sent(entries):
    """sent.json에 전송 목록을 저장한다."""
    SENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def remove_old_entries(entries):
    """보관 기간이 지난 항목을 제거한다."""
    cutoff = (datetime.now() - timedelta(days=DEDUP_RETENTION_DAYS)).strftime("%Y-%m-%d")
    return [e for e in entries if e.get("date", "") >= cutoff]


def deduplicate(items):
    """오늘 이미 전송된 URL을 제외한 항목만 반환한다.

    dedup 키: (date, url) 조합.
    - 같은 날짜 + 같은 URL → 중복 (재전송 방지)
    - 다른 날짜 + 같은 URL → 허용 (날짜가 바뀌면 재전송 가능)
    - 오늘 실패 후 재실행 시: save 성공 전엔 sent 미등록이므로 재처리됨
    """
    sent = load_sent()
    today = datetime.now().strftime("%Y-%m-%d")
    sent_keys = {(e["date"], e["url"]) for e in sent}
    return [item for item in items if (today, item["url"]) not in sent_keys]


def mark_as_sent(items):
    """새로 전송된 항목을 sent.json에 추가하고, 오래된 항목을 정리한다."""
    sent = load_sent()
    today = datetime.now().strftime("%Y-%m-%d")

    for item in items:
        sent.append({
            "url": item["url"],
            "title": item["title"],
            "date": today,
        })

    sent = remove_old_entries(sent)
    save_sent(sent)
