#!/usr/bin/env python3
"""아침 브리핑 자동화 - 날씨, 캘린더, 옷 추천"""

import sys
import subprocess
import requests
import json
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from morning_config import (
    OUTPUT_DIR, WEATHER_LAT, WEATHER_LON, WEATHER_URL,
    MCLI_PATH, CALENDAR_ACCOUNTS,
    WARDROBE_FILE, OUTFIT_LOG_FILE,
    LM_STUDIO_URL, LM_STUDIO_MODEL,
    COMMUTE_MORNING, COMMUTE_EVENING,
    OUTFIT_SYSTEM_PROMPT, OUTFIT_RULES,
)


def fetch_weather():
    """Open-Meteo API에서 서울 날씨를 가져온다."""
    print("  날씨 조회 중...")
    params = {
        "latitude": WEATHER_LAT,
        "longitude": WEATHER_LON,
        "hourly": "temperature_2m,precipitation_probability,precipitation,weathercode,windspeed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
        "timezone": "Asia/Seoul",
        "forecast_days": 1,
    }
    resp = requests.get(WEATHER_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    hourly = data.get("hourly", {})
    daily = data.get("daily", {})

    # 출퇴근 시간 기온 추출
    temps = hourly.get("temperature_2m", [])
    precip_prob = hourly.get("precipitation_probability", [])

    morning_temps = temps[COMMUTE_MORNING[0]:COMMUTE_MORNING[1] + 1] if len(temps) > COMMUTE_MORNING[1] else []
    evening_temps = temps[COMMUTE_EVENING[0]:COMMUTE_EVENING[1] + 1] if len(temps) > COMMUTE_EVENING[1] else []

    morning_precip = precip_prob[COMMUTE_MORNING[0]:COMMUTE_MORNING[1] + 1] if len(precip_prob) > COMMUTE_MORNING[1] else []
    evening_precip = precip_prob[COMMUTE_EVENING[0]:COMMUTE_EVENING[1] + 1] if len(precip_prob) > COMMUTE_EVENING[1] else []

    weather_code = daily.get("weathercode", [0])[0]
    weather_desc = decode_weather(weather_code)

    return {
        "daily_max": daily.get("temperature_2m_max", [0])[0],
        "daily_min": daily.get("temperature_2m_min", [0])[0],
        "daily_precip": daily.get("precipitation_sum", [0])[0],
        "morning_temp_range": f"{min(morning_temps):.0f}~{max(morning_temps):.0f}" if morning_temps else "N/A",
        "evening_temp_range": f"{min(evening_temps):.0f}~{max(evening_temps):.0f}" if evening_temps else "N/A",
        "morning_precip_max": max(morning_precip) if morning_precip else 0,
        "evening_precip_max": max(evening_precip) if evening_precip else 0,
        "weather_desc": weather_desc,
        "hourly_temps": temps,
        "commute_morning_avg": sum(morning_temps) / len(morning_temps) if morning_temps else 0,
        "commute_evening_avg": sum(evening_temps) / len(evening_temps) if evening_temps else 0,
    }


def decode_weather(code):
    """WMO 날씨 코드를 한국어로 변환한다."""
    mapping = {
        0: "맑음", 1: "대체로 맑음", 2: "약간 흐림", 3: "흐림",
        45: "안개", 48: "짙은 안개",
        51: "이슬비", 53: "이슬비", 55: "강한 이슬비",
        61: "약한 비", 63: "비", 65: "강한 비",
        71: "약한 눈", 73: "눈", 75: "강한 눈",
        80: "소나기", 81: "소나기", 82: "강한 소나기",
        95: "뇌우", 96: "우박 뇌우", 99: "강한 우박 뇌우",
    }
    return mapping.get(code, f"코드 {code}")


def fetch_calendar():
    """mcli로 캘린더 일정을 가져온다."""
    print("  캘린더 조회 중...")
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    results = {}

    # 오늘~내일 일정 (계정별)
    for account in CALENDAR_ACCOUNTS:
        try:
            cmd = [MCLI_PATH, "agenda", today, tomorrow] + account["args"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            results[account["name"]] = result.stdout.strip() if result.stdout.strip() else "(일정 없음)"
        except Exception as e:
            results[account["name"]] = f"(조회 실패: {e})"

    # 다음 주 미리보기
    try:
        cmd = [MCLI_PATH, "agenda", today, next_week]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        results["next_week"] = result.stdout.strip() if result.stdout.strip() else "(일정 없음)"
    except Exception as e:
        results["next_week"] = f"(조회 실패: {e})"

    return results


def recommend_outfit(weather):
    """날씨와 옷장 정보를 기반으로 LLM에게 옷 추천을 받는다."""
    print("  옷 추천 생성 중...")

    wardrobe = WARDROBE_FILE.read_text(encoding="utf-8") if WARDROBE_FILE.exists() else "(옷장 파일 없음)"
    outfit_log = OUTFIT_LOG_FILE.read_text(encoding="utf-8") if OUTFIT_LOG_FILE.exists() else "(로그 없음)"

    user_prompt = f"""오늘 날씨 정보:
- 날씨: {weather['weather_desc']}
- 출근 시간(8-9시) 기온: {weather['morning_temp_range']}°C
- 퇴근 시간(18-19시) 기온: {weather['evening_temp_range']}°C
- 일일 최저/최고: {weather['daily_min']}°C / {weather['daily_max']}°C
- 강수량: {weather['daily_precip']}mm
- 출근 강수확률: {weather['morning_precip_max']}%, 퇴근 강수확률: {weather['evening_precip_max']}%

{OUTFIT_RULES}

## 옷장 목록
{wardrobe}

## 최근 코디 로그 (겹치지 않게)
{outfit_log}

위 정보를 바탕으로 오늘 코디 1가지를 추천해주세요.
형식: 아우터 + 이너 + 하의 + 신발 (각 아이템 이유 간단히)"""

    try:
        resp = requests.post(
            f"{LM_STUDIO_URL}/chat/completions",
            json={
                "model": LM_STUDIO_MODEL,
                "messages": [
                    {"role": "system", "content": OUTFIT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.5,
                "max_tokens": 4096,
                "stream": False,
            },
            timeout=600,
        )
        resp.raise_for_status()
        msg = resp.json()["choices"][0]["message"]
        content = msg.get("content", "").strip()
        if not content:
            content = msg.get("reasoning_content", "").strip()
        return content if content else "(추천 생성 실패)"
    except Exception as e:
        return f"(추천 생성 실패: {e})"


def format_morning_briefing(weather, calendar, outfit):
    """아침 브리핑을 마크다운으로 포맷한다."""
    today = datetime.now().strftime("%Y-%m-%d (%a)")
    lines = [f"# ☀️ 아침 브리핑 - {today}\n"]

    # 날씨
    rain_warning = ""
    if weather["daily_precip"] > 0 or weather["morning_precip_max"] > 30 or weather["evening_precip_max"] > 30:
        rain_warning = " ☔ 우산 챙기세요!"

    lines.append("## 🌤️ 서울 날씨\n")
    lines.append(f"- 날씨: **{weather['weather_desc']}**{rain_warning}")
    lines.append(f"- 출근(8-9시): **{weather['morning_temp_range']}°C** (강수확률 {weather['morning_precip_max']}%)")
    lines.append(f"- 퇴근(18-19시): **{weather['evening_temp_range']}°C** (강수확률 {weather['evening_precip_max']}%)")
    lines.append(f"- 일일: {weather['daily_min']}°C ~ {weather['daily_max']}°C")

    # 캘린더
    lines.append("\n## 📅 오늘 일정\n")
    for account in CALENDAR_ACCOUNTS:
        name = account["name"]
        lines.append(f"**[{name}]**")
        lines.append(calendar.get(name, "(없음)"))
        lines.append("")

    lines.append("**[다음 주 미리보기]**")
    lines.append(calendar.get("next_week", "(없음)"))

    # 옷 추천
    lines.append("\n## 👔 오늘의 코디 추천\n")
    lines.append(outfit)

    # 푸터
    now = datetime.now().strftime("%Y-%m-%d %H:%M KST")
    lines.append(f"\n---\n*Generated at {now}*\n")

    return "\n".join(lines)


def main():
    print("☀️ 아침 브리핑 시작\n")

    # 1. 날씨
    print("[1/3] 날씨 조회")
    try:
        weather = fetch_weather()
        print(f"  {weather['weather_desc']}, 출근 {weather['morning_temp_range']}°C")
    except Exception as e:
        print(f"  [ERROR] 날씨 조회 실패: {e}")
        weather = {
            "daily_max": "?", "daily_min": "?", "daily_precip": 0,
            "morning_temp_range": "?", "evening_temp_range": "?",
            "morning_precip_max": 0, "evening_precip_max": 0,
            "weather_desc": "조회 실패", "hourly_temps": [],
            "commute_morning_avg": 0, "commute_evening_avg": 0,
        }

    # 2. 캘린더
    print("[2/3] 캘린더 조회")
    try:
        calendar = fetch_calendar()
    except Exception as e:
        print(f"  [ERROR] 캘린더 조회 실패: {e}")
        calendar = {}

    # 3. 옷 추천
    print("[3/3] 옷 추천")
    outfit = recommend_outfit(weather)

    # 포맷 및 저장
    print("\n브리핑 생성 중...")
    content = format_morning_briefing(weather, calendar, outfit)

    today = datetime.now().strftime("%Y-%m-%d")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"morning-{today}.md"
    path.write_text(content, encoding="utf-8")

    print(f"  브리핑 저장: {path}")
    print("\n✅ 아침 브리핑 완료!")


if __name__ == "__main__":
    main()
