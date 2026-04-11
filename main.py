#!/usr/bin/env python3
"""테크 뉴스 브리핑 자동화 - 크롤링, 필터링, LM Studio 요약, 마크다운 생성"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from collectors import geeknews, hackernews, github_trending
from filters import filter_items
from dedup import deduplicate, mark_as_sent
from summarizer import summarize_all
from formatter import format_briefing, save_briefing


def main():
    print("🗞️ 테크 뉴스 브리핑 시작\n")

    # 1. 크롤링
    print("[1/5] 뉴스 크롤링 중...")
    all_items = []

    for name, collector in [
        ("GeekNews", geeknews),
        ("Hacker News", hackernews),
        ("GitHub Trending", github_trending),
    ]:
        try:
            items = collector.fetch()
            print(f"  {name}: {len(items)}개 수집")
            all_items.extend(items)
        except Exception as e:
            print(f"  [ERROR] {name} 크롤링 실패: {e}")

    if not all_items:
        print("\n수집된 뉴스가 없습니다. 종료합니다.")
        return

    # 2. 키워드 필터링
    print(f"\n[2/5] 키워드 필터링 중... ({len(all_items)}개 → ", end="")
    filtered = filter_items(all_items)

    # 필터 결과가 없으면 관심 항목 상위 10개 선택
    if not filtered:
        print("매칭 없음, 상위 10개 선택)")
        filtered = all_items[:10]
    else:
        print(f"{len(filtered)}개)")

    # 3. 중복 제거
    print(f"[3/5] 중복 제거 중... ({len(filtered)}개 → ", end="")
    new_items = deduplicate(filtered)
    print(f"{len(new_items)}개)")

    if not new_items:
        print("\n새로운 뉴스가 없습니다. 종료합니다.")
        return

    # 4. LM Studio 요약
    print(f"\n[4/5] LM Studio 요약 중... ({len(new_items)}개)")
    summarized = summarize_all(new_items)

    # 5. 브리핑 생성 및 저장
    print("\n[5/5] 브리핑 생성 중...")
    content = format_briefing(summarized)
    path = save_briefing(content)

    # 파일 저장 성공 확인 후에만 sent 등록
    if path and path.exists():
        mark_as_sent(summarized)
        print(f"\n✅ 완료! {len(summarized)}개 항목 브리핑 생성됨")
        print(f"   파일: {path}")
    else:
        print("\n[ERROR] 브리핑 파일 저장 실패 — sent 등록 보류 (재실행 시 재처리됨)")


if __name__ == "__main__":
    main()
