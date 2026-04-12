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
    """최근 N일간 전송된 모든 URL을 제외한 항목만 반환한다.

    - 보관 기간(DEDUP_RETENTION_DAYS) 내의 URL은 절대 반복하지 않음
    - 보관 기간이 지난 URL은 new로 취급해 재전송 가능
    """
    sent = load_sent()
    sent_urls = {e["url"] for e in sent}  # 최근 N일 내 모든 URL
    return [item for item in items if item["url"] not in sent_urls]


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
