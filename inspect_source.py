# -*- coding: utf-8 -*-
"""KBO 공식 + 네이버 모바일에서 스코어보드 데이터 존재 여부를 직접 확인."""
import re, datetime as dt, requests
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)","Referer":"https://www.koreabaseball.com/"}
KST=dt.timezone(dt.timedelta(hours=9))

def get(u,**kw):
    try:
        r=requests.get(u,headers=UA,timeout=20,**kw); return r.status_code,r.text
    except Exception as e: return "ERR",str(e)
def post(u,data):
    try:
        r=requests.post(u,headers=UA,timeout=20,data=data); return r.status_code,r.text
    except Exception as e: return "ERR",str(e)

def main():
    d="2026-07-19"; dd="20260719"
    # ── 1) KBO 공식: 날짜별 스코어보드 (ASP.NET, 서버 렌더) ──
    print("== KBO 공식 스코어보드 ==")
    u=f"https://www.koreabaseball.com/Schedule/ScoreBoard.aspx"
    code,html=get(u)
    print(f"[{code}] {u}  길이:{len(html) if isinstance(html,str) else '?'}")
    if isinstance(html,str):
        # 팀명/점수/이닝 흔적이 HTML에 박혀 있는지
        for kw in ["삼성","롯데","LG","이닝","스코어","tblScore","broadcast"]:
            if kw in html: print("   포함:",kw)
        # ASP.NET 폼 필드 확인 (POST로 날짜 바꿀 때 필요)
        for f in ["__VIEWSTATE","__EVENTVALIDATION","ddlYear","ddlMonth"]:
            print("   폼필드",f,":", "있음" if f in html else "없음")

    # ── 2) KBO 리뷰/문자중계 페이지 (경기별 상세) ──
    print("\n== KBO 경기 리뷰 페이지 ==")
    for u in [f"https://www.koreabaseball.com/Game/LiveText.aspx?leagueId=1&seriesId=0&gameId={dd}HTSK02026&gyear=2026",
              f"https://www.koreabaseball.com/Game/BoxScore.aspx?leagueId=1&seriesId=0&gameId={dd}HTSK02026&gyear=2026"]:
        code,html=get(u)
        has=[kw for kw in ["삼성","KIA","SSG","이닝","승리투수","결승타","tbl"] if isinstance(html,str) and kw in html]
        print(f"[{code}] {u.split('/')[-1][:40]}  길이:{len(html) if isinstance(html,str) else '?'}  포함:{has}")

    # ── 3) 네이버 모바일 API (게이트웨이 아닌 다른 호스트) ──
    print("\n== 네이버 대체 호스트 ==")
    gid="20260719HTSK02026"
    for u in [f"https://sports.news.naver.com/gameCenter/gameRecord.nhn?category=kbo&gameId={gid}",
              f"https://api-gw.sports.naver.com/sports/games/{gid}/record/basic",
              f"https://sports.news.naver.com/ajax/kbaseball/game/{gid}/scoreboard"]:
        code,html=get(u)
        print(f"[{code}] {u.split('naver.com')[-1][:55]}  길이:{len(html) if isinstance(html,str) else '?'}")

if __name__=="__main__": main()
