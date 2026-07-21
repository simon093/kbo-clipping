# -*- coding: utf-8 -*-
"""경기가 있는 날짜를 찾아 실제 경기/박스스코어 구조를 출력한다."""
import json, datetime as dt, requests

UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://m.sports.naver.com/"}
KST = dt.timezone(dt.timedelta(hours=9))

def get(url):
    return requests.get(url, headers=UA, timeout=15).json()

def main():
    print("=" * 60)
    # 최근 7일을 훑어서 경기가 있는 첫 날을 찾는다
    base = dt.datetime.now(KST)
    found = None
    for i in range(1, 8):
        d = (base - dt.timedelta(days=i)).strftime("%Y-%m-%d")
        url = ("https://api-gw.sports.naver.com/schedule/games"
               f"?fields=basic&upperCategoryId=kbaseball&categoryId=kbo"
               f"&fromDate={d}&toDate={d}&size=20")
        games = get(url).get("result", {}).get("games", [])
        print(f"{d}: 경기 {len(games)}개")
        if games and not found:
            found = (d, games)
    if not found:
        print("최근 7일간 경기를 못 찾음 — 이 내용 그대로 붙여주세요.")
        return
    d, games = found
    print(f"\n★ 경기 있는 날: {d}")
    g = games[0]
    print("\n----- [중요] 경기 1개의 키 -----")
    print(json.dumps(g, ensure_ascii=False, indent=2)[:1800])
    gid = g.get("gameId") or g.get("gameCode") or g.get("id")
    print("\ngameId 후보:", gid)
    if gid:
        rec = get(f"https://api-gw.sports.naver.com/sports/games/{gid}/record").get("result", {})
        print("\n----- [중요] 박스스코어 키 -----")
        print("최상위 키:", list(rec.keys()))
        print(json.dumps(rec, ensure_ascii=False, indent=2)[:1800])

if __name__ == "__main__":
    main()
