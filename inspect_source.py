# -*- coding: utf-8 -*-
"""
inspect_source.py
데이터 소스(네이버 스포츠)의 실제 응답 구조를 한 번 출력한다.
이 스크립트를 실행한 뒤, 아래 ===== 마커 사이에 찍히는 내용을 그대로 복사해서
Claude에게 붙여주면, collect_kbo.py의 필드 매핑을 정확히 맞춰줄 수 있다.

실행법(둘 중 편한 것):
  · 로컬:   pip install requests && python inspect_source.py
  · GitHub: Actions 탭 → "소스 점검(inspect)" → Run workflow → 끝난 로그 열기
"""
import json
import datetime as dt
import requests

UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://m.sports.naver.com/"}
KST = dt.timezone(dt.timedelta(hours=9))
YDAY = (dt.datetime.now(KST) - dt.timedelta(days=1)).strftime("%Y-%m-%d")


def show(title, obj, depth=0):
    print(f"\n----- {title} -----")
    if isinstance(obj, dict):
        for k, v in obj.items():
            t = type(v).__name__
            preview = v if not isinstance(v, (dict, list)) else f"<{t}, len={len(v)}>"
            print(f"  {k}: {preview}")
    else:
        print(json.dumps(obj, ensure_ascii=False)[:800])


def main():
    print("=" * 60)
    print(f"KBO 소스 점검 · 대상 날짜 {YDAY}")
    print("=" * 60)

    # 1) 경기 일정/스코어
    sched_url = ("https://api-gw.sports.naver.com/schedule/games"
                 f"?fields=basic&upperCategoryId=kbaseball&categoryId=kbo"
                 f"&fromDate={YDAY}&toDate={YDAY}&size=20")
    print(f"\n[1] 스케줄 요청:\n    {sched_url}")
    try:
        r = requests.get(sched_url, headers=UA, timeout=15)
        print("    HTTP 상태:", r.status_code)
        data = r.json()
        show("스케줄 최상위 키", data)
        result = data.get("result", data)
        games = (result.get("games") if isinstance(result, dict) else None) or []
        print(f"\n    경기 수: {len(games)}")
        if games:
            show("[중요] 경기 1개의 키 = 여기를 Claude에게", games[0])
            gid = games[0].get("gameId") or games[0].get("gameCode") or games[0].get("id")
            print("\n    첫 경기 gameId 후보:", gid)
            # 2) 개별 경기 박스스코어(이닝별/승패/결승타)
            if gid:
                rec_url = f"https://api-gw.sports.naver.com/sports/games/{gid}/record"
                print(f"\n[2] 박스스코어 요청:\n    {rec_url}")
                r2 = requests.get(rec_url, headers=UA, timeout=15)
                print("    HTTP 상태:", r2.status_code)
                rec = r2.json().get("result", r2.json())
                show("[중요] 박스스코어 키 = 여기도 Claude에게", rec)
    except Exception as ex:
        print("    실패:", repr(ex))
        print("    → 이 메시지를 그대로 Claude에게 보내주세요. 다른 소스로 바꿀게요.")

    print("\n" + "=" * 60)
    print("위 내용을 통째로 복사해서 Claude에게 붙여주세요.")
    print("=" * 60)


if __name__ == "__main__":
    main()
