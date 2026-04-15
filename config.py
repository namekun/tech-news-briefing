import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML이 필요합니다: pip install pyyaml")
    sys.exit(1)

# 프로젝트 경로
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
SENT_FILE = DATA_DIR / "sent.json"

# 중복 체크 보관 기간 (일)
DEDUP_RETENTION_DAYS = 7

# 소스 URL
GEEKNEWS_URL = "https://news.hada.io"
HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
GITHUB_TRENDING_URL = "https://github.com/trending?since=daily"

# HN에서 가져올 항목 수
HN_FETCH_COUNT = 50

# ── config.local.yaml 로드 ──────────────────────────────────
_CONFIG_FILE = BASE_DIR / "config.local.yaml"

if not _CONFIG_FILE.exists():
    print(f"[ERROR] 설정 파일이 없습니다: {_CONFIG_FILE.name}")
    print("       먼저 설정을 완료하세요: python setup.py")
    sys.exit(1)

with open(_CONFIG_FILE, "r", encoding="utf-8") as _f:
    _cfg = yaml.safe_load(_f) or {}

_llm = _cfg.get("llm", {})
LLM_PROVIDER  = _llm.get("provider", "lmstudio")
LLM_URL       = _llm.get("url", "http://127.0.0.1:1234/v1")
LLM_API_KEY   = _llm.get("api_key", "")
LLM_MODEL     = _llm.get("model", "gemma-4-e4b-it")

KEYWORDS = _cfg.get("keywords", [
    "Java", "Spring", "Kotlin", "JVM",
    "Elasticsearch", "Lucene", "OpenSearch",
    "AI", "LLM", "Claude", "GPT", "ML",
    "Kafka", "Redis", "PostgreSQL", "MySQL",
    "Kubernetes", "Docker", "DevOps",
    "Backend", "microservice",
])

# ── 요약 프롬프트 (고정) ────────────────────────────────────
SUMMARY_SYSTEM_PROMPT = """당신은 기술 뉴스 요약 전문가입니다.
주어진 뉴스 항목을 한국어로 간결하게 요약하고, 관련도를 엄격하게 평가해주세요.
기술 용어는 영어 그대로 사용하세요.

대상 독자: 백엔드 개발자

관련도 기준:
🔥 높음 — 업무에 직접 적용 가능
⭐ 보통 — 간접적으로 유용하거나 개발 생산성 향상
💡 참고 — 직접 관련 없지만 흥미로운 뉴스

세 등급을 골고루 사용하세요. 한 등급에 몰리지 마세요."""

SUMMARY_USER_PROMPT = """다음 뉴스 항목을 요약해주세요:

제목: {title}
URL: {url}
{description}

다음 형식으로 응답해주세요 (다른 말 없이 이 형식만):
요약: (한 줄 한국어 요약)
관련도: (🔥 높음 / ⭐ 보통 / 💡 참고 중 하나. 기준을 엄격히 적용)"""
