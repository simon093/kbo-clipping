# -*- coding: utf-8 -*-
"""박스스코어(이닝별/승패/결승타)를 주는 엔드포인트를 탐색한다."""
import json, datetime as dt, requests

UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://m.sports.naver.com/"}
KST = dt.timezone(dt.timedelta(hours=9))

def get(url):
    r = requests.get(url, headers=UA, timeout=15)
    return r.status_code, (r.json() if "json" in r.headers.get("content-type","") else {})

def main():
    base = dt.datetime.now(KST)
    gid = None
    for i in range(1, 9):
        d = (base - dt.timedelta(days=i)).strftime("%Y-%m-%d")
        u = ("https://api-gw.sports.naver.com/schedule/games"
             f"?fields=basic&upperCategoryId=kbaseball&categoryId=kbo&fromDate={d}&toDate={d}&size=20")
        _, j = get(u)
        gs = j.get("result", {}).get("games", [])
        if gs:
            gid = gs[0]["gameId"]; print("테스트 gameId:", gid, "(", d, ")"); break
    if not gid:
        print("경기 못 찾음"); return

    # 후보 엔드포인트들을 하나씩 찔러본다
    cands = [
        f"https://api-gw.sports.naver.com/sports/games/{gid}/preview",
        f"https://api-gw.sports.naver.com/sports/games/{gid}/relay",
        f"https://api-gw.sports.naver.com/sports/games/{gid}/result",
        f"https://api-gw.sports.naver.com/sports/games/{gid}/scoreboard",
        f"https://api-gw.sports.naver.com/sports/games/{gid}/boxscore",
        f"https://api-gw.sports.naver.com/games/{gid}/basicRecord",
    ]
    for u in cands:
        try:
            code, j = get(u)
            keys = list(j.get("result", j).keys()) if isinstance(j, dict) else "non-dict"
            print(f"\n[{code}] {u.split('/')[-1]}  키: {keys}")
        except Exception as e:
            print(f"\n[ERR] {u.split('/')[-1]}: {e}")

if __name__ == "__main__":
    main()
