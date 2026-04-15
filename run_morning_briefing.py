#!/usr/bin/env python3
"""오전브리핑 래퍼 - mlx-lm 서버를 자동으로 시작/종료하고 브리핑을 실행한다."""

import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

MLX_PYTHON = str(Path.home() / ".mlx-env/bin/python3")
MODEL = "Jiunsong/supergemma4-26b-uncensored-mlx-4bit-v2"
PORT = 8080
BRIEFING_DIR = Path(__file__).parent

sys.path.insert(0, str(BRIEFING_DIR))


def wait_for_server(port, timeout=300):
    """서버가 준비될 때까지 대기한다. 실제 추론 요청으로 모델 로딩까지 확인한다."""
    warmup_url = f"http://127.0.0.1:{port}/v1/chat/completions"
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 1,
        "temperature": 0,
    }).encode("utf-8")

    deadline = time.time() + timeout
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        try:
            req = urllib.request.Request(
                warmup_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            # 첫 추론은 모델 로딩 포함이라 오래 걸릴 수 있음
            urllib.request.urlopen(req, timeout=min(60, deadline - time.time()))
            return True
        except urllib.error.HTTPError:
            # HTTP 에러(4xx/5xx)도 서버+모델이 살아있다는 뜻
            return True
        except Exception:
            elapsed = int(time.time() - (deadline - timeout))
            print(f"  대기 중... ({elapsed}s)", end="\r")
            time.sleep(5)

    return False


def main():
    print("🚀 mlx-lm 서버 시작 중...")
    server = subprocess.Popen(
        [
            MLX_PYTHON, "-m", "mlx_lm.server",
            "--model", MODEL,
            "--port", str(PORT),
            "--chat-template-args", '{"enable_thinking":false}',
            "--log-level", "WARNING",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        print("⏳ 서버 준비 대기 중...")
        if not wait_for_server(PORT):
            print("❌ 서버 시작 타임아웃")
            sys.exit(1)
        print("✅ 서버 준비 완료\n")

        print("☀️ 아침 브리핑 시작")
        import morning_briefing
        morning_briefing.main()

    finally:
        print("\n🛑 mlx-lm 서버 종료 중...")
        server.terminate()
        server.wait()
        print("✅ 서버 종료 완료")


if __name__ == "__main__":
    main()
