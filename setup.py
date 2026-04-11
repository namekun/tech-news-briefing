#!/usr/bin/env python3
"""테크 뉴스 브리핑 설정 마법사"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML이 필요합니다: pip install pyyaml")
    sys.exit(1)

CONFIG_FILE = Path(__file__).parent / "config.local.yaml"
EXAMPLE_FILE = Path(__file__).parent / "config.example.yaml"

PROVIDERS = {
    "1": ("lmstudio",   "LM Studio (로컬)",       "http://127.0.0.1:1234/v1",        False),
    "2": ("ollama",     "Ollama (로컬)",           "http://127.0.0.1:11434/v1",       False),
    "3": ("openai",     "OpenAI",                  "https://api.openai.com/v1",       True),
    "4": ("anthropic",  "Anthropic (Claude)",      "",                                True),
    "5": ("openrouter", "OpenRouter (Claude/GPT/Gemini 등)", "https://openrouter.ai/api/v1", True),
    "6": ("custom",     "직접 입력 (OpenAI 호환)", "",                                True),
}

DEFAULT_MODELS = {
    "lmstudio":   "gemma-4-e4b-it",
    "ollama":     "gemma3:4b",
    "openai":     "gpt-4o-mini",
    "anthropic":  "claude-haiku-4-5-20251001",
    "openrouter": "anthropic/claude-haiku-4-5",
    "custom":     "",
}

DEFAULT_KEYWORDS = [
    "Java", "Spring", "Kotlin", "JVM",
    "Elasticsearch", "Lucene", "OpenSearch",
    "AI", "LLM", "Claude", "GPT", "ML",
    "Kafka", "Redis", "PostgreSQL", "MySQL",
    "Kubernetes", "Docker", "DevOps",
    "Backend", "microservice",
]


def prompt(msg, default=""):
    """입력 프롬프트. 엔터 시 기본값 반환."""
    if default:
        val = input(f"  {msg} [{default}]: ").strip()
        return val if val else default
    else:
        return input(f"  {msg}: ").strip()


def main():
    print("\n🗞️  Tech News Briefing Setup")
    print("─" * 40)

    # 기존 설정 로드
    existing = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            existing = yaml.safe_load(f) or {}
        print(f"  기존 설정 발견: {CONFIG_FILE.name} (엔터로 유지)\n")

    config = {}

    # ── [1/2] LLM 설정 ──────────────────────────────────
    print("[1/2] LLM 제공자 선택\n")
    for key, (_, label, _, _) in PROVIDERS.items():
        print(f"  {key}. {label}")
    print()

    existing_provider = existing.get("llm", {}).get("provider", "")
    existing_num = next((k for k, (p, *_) in PROVIDERS.items() if p == existing_provider), "1")
    choice = prompt("선택", existing_num)
    if choice not in PROVIDERS:
        print("  잘못된 선택. 1로 설정합니다.")
        choice = "1"

    provider_id, provider_label, default_url, needs_key = PROVIDERS[choice]
    default_model = DEFAULT_MODELS[provider_id]
    ex_llm = existing.get("llm", {})

    print(f"\n  ✔ {provider_label} 선택됨\n")

    if provider_id in ("lmstudio", "ollama"):
        url = prompt("API URL", ex_llm.get("url", default_url))
        api_key = ""
    elif provider_id == "anthropic":
        url = ""
        api_key = prompt("Anthropic API Key", ex_llm.get("api_key", ""))
    elif provider_id == "custom":
        url = prompt("API URL (OpenAI 호환)", ex_llm.get("url", ""))
        api_key = prompt("API Key (없으면 엔터)", ex_llm.get("api_key", ""))
    else:
        url = default_url
        api_key = prompt(f"{provider_label} API Key", ex_llm.get("api_key", ""))

    model = prompt("모델명", ex_llm.get("model", default_model))

    config["llm"] = {
        "provider": provider_id,
        "url": url,
        "api_key": api_key,
        "model": model,
    }

    # ── [2/2] 키워드 설정 ───────────────────────────────
    print("\n[2/2] 관심 키워드 (쉼표 구분, 엔터로 기본값 사용)\n")
    ex_keywords = existing.get("keywords", DEFAULT_KEYWORDS)
    kw_default = ", ".join(ex_keywords)
    kw_input = prompt("키워드", kw_default)
    keywords = [k.strip() for k in kw_input.split(",") if k.strip()]
    config["keywords"] = keywords

    # ── 저장 ────────────────────────────────────────────
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"\n✅ 설정 저장 완료: {CONFIG_FILE.name}")
    print(f"   실행: python main.py\n")


if __name__ == "__main__":
    main()
