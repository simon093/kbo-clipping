# -*- coding: utf-8 -*-
"""박스스코어 경로를 한 방에 광범위 탐색."""
import re, json, datetime as dt, requests
UA = {"User-Agent":"Mozilla/5.0","Referer":"https://m.sports.naver.com/"}
KST = dt.timezone(dt.timedelta(hours=9))
def jget(u):
    try:
        r=requests.get(u,headers=UA,timeout=15); ct=r.headers.get("content-type","")
        return r.status_code,(r.json() if "json" in ct else r.text)
    except Exception as e: return "ERR",str(e)
def main():
    base=dt.datetime.now(KST); gid=None
    for i in range(1,9):
        d=(base-dt.timedelta(days=i)).strftime("%Y-%m-%d")
        _,j=jget("https://api-gw.sports.naver.com/schedule/games"
                 f"?fields=basic&upperCategoryId=kbaseball&categoryId=kbo&fromDate={d}&toDate={d}&size=20")
        gs=j.get("result",{}).get("games",[]) if isinstance(j,dict) else []
        if gs: gid=gs[0]["gameId"]; print("gameId:",gid,"(",d,")"); break
    if not gid: print("경기 없음"); return
    paths=["record","relay","preview","result","scoreboard","boxscore","main","situation",
           "lineup","stats","record?fields=all","relay?inning=1"]
    hosts=[f"https://api-gw.sports.naver.com/sports/games/{gid}/",
           f"https://api-gw.sports.naver.com/sports/kbaseball/games/{gid}/",
           f"https://api-gw.sports.naver.com/games/{gid}/"]
    print("\n== API 후보 스캔 ==")
    for h in hosts:
        for p in paths:
            code,j=jget(h+p)
            if code==200 and isinstance(j,dict):
                keys=list(j.get("result",j).keys())
                if keys: print(f"[200 ★] {h+p}\n        키: {keys}")
    # 웹페이지에서 경로 힌트
    for page in [f"https://m.sports.naver.com/game/{gid}",
                 f"https://m.sports.naver.com/game/{gid}/record"]:
        code,html=jget(page)
        print(f"\n== 페이지 {page} (HTTP {code}) ==")
        if isinstance(html,str):
            hits=sorted(set(re.findall(r'/sports/games/[^"\']*', html))
                        | set(re.findall(r'"[a-zA-Z]+Record"', html))
                        | set(re.findall(r'scoreBoard|inning|winPitcher|homeStarter', html)))
            for x in hits[:30]: print("  ",x)
if __name__=="__main__": main()
