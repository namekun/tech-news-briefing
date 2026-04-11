# 🗞️ Tech News Briefing

GeekNews, Hacker News, GitHub Trending에서 기술 뉴스를 수집하고, LLM으로 요약해 마크다운 브리핑을 생성합니다.

## 기능

- **멀티 소스 수집**: GeekNews, Hacker News, GitHub Trending
- **키워드 필터링**: 관심 기술 스택 기반 필터
- **LLM 요약**: 관심도(🔥⭐💡) 포함 한국어 요약
- **중복 제거**: 날짜+URL 기준, 7일 보관
- **멀티 프로바이더**: 로컬 LLM부터 클라우드 API까지 지원

## 지원 LLM 제공자

| 제공자 | 설명 |
|--------|------|
| LM Studio | 로컬 LLM (기본) |
| Ollama | 로컬 LLM |
| OpenAI | GPT 모델 |
| Anthropic | Claude 모델 |
| OpenRouter | Claude·GPT·Gemini 등 통합 |
| 직접 입력 | OpenAI 호환 API |

## 설치

```bash
git clone https://github.com/namekun/tech-news-briefing.git
cd tech-news-briefing

pip install -r requirements.txt

# Anthropic(Claude) 사용 시 추가 설치
# pip install anthropic
```

## 설정

```bash
python setup.py
```

인터랙티브 마법사가 실행되며 `config.local.yaml`을 생성합니다.

직접 편집하려면:
```bash
cp config.example.yaml config.local.yaml
# config.local.yaml 수정
```

## 실행

```bash
python main.py
```

브리핑 파일이 `output/briefing-YYYY-MM-DD.md`로 저장됩니다.

## 프로젝트 구조

```
tech-news-briefing/
├── setup.py              # 설정 마법사
├── main.py               # 메인 실행
├── config.py             # 설정 로더
├── config.example.yaml   # 설정 예시
├── collectors/           # 소스별 크롤러
│   ├── geeknews.py
│   ├── hackernews.py
│   └── github_trending.py
├── filters.py            # 키워드 필터
├── dedup.py              # 중복 제거
├── summarizer.py         # LLM 요약
├── formatter.py          # 마크다운 포맷
└── output/               # 생성된 브리핑 (gitignore)
```

## 출력 예시

```markdown
# 🗞️ 테크 뉴스 브리핑 - 2026-04-11

## GeekNews

- 🔥 **Elasticsearch 8.14 릴리즈**
  벡터 검색 성능 대폭 개선, HNSW 알고리즘 최적화 포함
  <https://...>

## 🔥 Hot OSS Today (GitHub Trending)

- ⭐ **spring-ai** (⭐1.2k · Java)
  Spring 생태계에서 AI 통합을 위한 공식 프레임워크
  <https://...>
```

## 라이선스

MIT
