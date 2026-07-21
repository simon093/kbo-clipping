# -*- coding: utf-8 -*-
"""소스 응답 구조를 한 겹 더 깊이 출력한다."""
import json, datetime as dt, requests

UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://m.sports.naver.com/"}
KST = dt.timezone(dt.timedelta(hours=9))
YDAY = (dt.datetime.now(KST) - dt.timedelta(days=1)).strftime("%Y-%m-%d")

def dump(label, obj, n=1200):
    print(f"\n----- {label} -----")
    print(json.dumps(obj, ensure_ascii=False, indent=2)[:n])

def main():
    print("=" * 60)
    print(f"KBO 소스 점검(2) · 대상 {YDAY}")
    print("=" * 60)
    url = ("https://api-gw.sports.naver.com/schedule/games"
           f"?fields=basic&upperCategoryId=kbaseball&categoryId=kbo"
           f"&fromDate={YDAY}&toDate={YDAY}&size=20")
    r = requests.get(url, headers=UA, timeout=15)
    print("HTTP:", r.status_code)
    data = r.json()
    result = data.get("result", {})
    print("\nresult 안의 키들:", list(result.keys()))
    # result 안을 통째로 살짝 출력 (진짜 구조 확인용)
    dump("result 내용 미리보기", result, 2000)

if __name__ == "__main__":
    main()
