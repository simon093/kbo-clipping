# -*- coding: utf-8 -*-
"""
run.py  — 매일 실행되는 오케스트레이터
  1) KBO 데이터 + 뉴스/여론 수집
  2) 리포트 데이터 조립
  3) HTML 렌더 → clippings/YYYY-MM-DD.html 저장
  4) 아카이브 index.html 재생성 (상단 '지난 클리핑' 바 + 전체 목록)
"""
import os
import sys
import glob
import datetime as dt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from render_html import render          # noqa: E402
from collect_kbo import fetch_kbo       # noqa: E402
from collect_news import fetch_news     # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(__file__), "clippings")
KST = dt.timezone(dt.timedelta(hours=9))
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


def _kst_now():
    return dt.datetime.now(KST)


def _label(d):
    return f"{d.strftime('%m.%d')} ({WEEKDAYS[d.weekday()]})"


def build_summary(kbo, hot):
    """상단 '오늘의 핵심' 4줄 자동 생성."""
    bullets = []
    # 핫이슈 1건
    if hot:
        bullets.append(hot[0]["title"])
    # 가장 점수차 큰 경기 / 이변
    games = kbo.get("games", [])
    for g in games:
        for t in g.get("tags", []):
            if t.get("k") in ("이변", "대기록"):
                bullets.append(t["v"])
                break
        if len(bullets) >= 3:
            break
    if not bullets:
        bullets.append("어제 경기 결과 업데이트")
    return bullets[:4]


def build_index():
    """clippings/ 안의 날짜 파일들로 아카이브 index.html 생성."""
    files = sorted(glob.glob(os.path.join(OUT_DIR, "20*-*-*.html")), reverse=True)
    rows = []
    for f in files:
        name = os.path.basename(f)
        date_str = name.replace(".html", "")
        try:
            d = dt.datetime.strptime(date_str, "%Y-%m-%d")
            rows.append(f'<li><a href="{name}">{d.strftime("%Y.%m.%d")} ({WEEKDAYS[d.weekday()]})</a></li>')
        except ValueError:
            continue
    latest = os.path.basename(files[0]) if files else "#"
    html = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KBO 데일리 클리핑 · 아카이브</title>
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css">
<style>body{{font-family:'Pretendard',system-ui,sans-serif;background:#F4F5F8;color:#14224A;margin:0;}}
header{{background:#14224A;color:#fff;padding:24px 20px;}}h1{{font-size:22px;font-weight:800;}}
.sub{{color:#A9B3D0;font-size:13px;margin-top:4px;}}
.wrap{{max-width:720px;margin:24px auto;padding:0 20px;}}
.latest{{display:inline-block;background:#FF5A4D;color:#fff;font-weight:700;padding:10px 18px;border-radius:8px;margin-bottom:20px;}}
ul{{list-style:none;padding:0;}}li{{border-bottom:1px solid #E5E7EE;}}
li a{{display:block;padding:13px 6px;color:#14224A;font-weight:600;text-decoration:none;}}
li a:hover{{background:#fff;}}</style></head><body>
<header><h1>KBO 데일리 클리핑 · 아카이브</h1><div class="sub">운영팀 모니터링 리포트 전체 보관함</div></header>
<div class="wrap"><a class="latest" href="{latest}">▶ 오늘자 리포트 열기</a>
<ul>{''.join(rows)}</ul></div></body></html>"""
    open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8").write(html)


def build_archive_bar(today):
    """상단 '지난 클리핑' 바에 최근 6일치 링크."""
    files = sorted(glob.glob(os.path.join(OUT_DIR, "20*-*-*.html")), reverse=True)
    dates = []
    for f in files[:6]:
        name = os.path.basename(f)
        try:
            d = dt.datetime.strptime(name.replace(".html", ""), "%Y-%m-%d")
            dates.append({"label": _label(d), "href": name, "on": (name == f"{today:%Y-%m-%d}.html")})
        except ValueError:
            continue
    if not any(x["on"] for x in dates):  # 오늘 파일이 아직 목록에 없으면 맨 앞에
        dates.insert(0, {"label": _label(today), "href": f"{today:%Y-%m-%d}.html", "on": True})
    return dates[:6]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    now = _kst_now()
    today = now.date()
    today_dt = dt.datetime.combine(today, dt.time())

    print("수집 시작:", now.strftime("%Y-%m-%d %H:%M KST"))
    kbo = fetch_kbo()
    try:
        hot, ops, buzz = fetch_news()
    except Exception as ex:
        print("[news] 수집 실패:", ex)
        hot, ops, buzz = [], [], []

    # 오늘 파일을 먼저 쓴 뒤 아카이브 바를 만들면 오늘 날짜가 포함됨
    out_path = os.path.join(OUT_DIR, f"{today:%Y-%m-%d}.html")
    open(out_path, "w", encoding="utf-8").write("")  # placeholder

    data = {
        "date_label": now.strftime("%Y. %m. %d") + f" ({WEEKDAYS[today.weekday()]})",
        "collected_time": now.strftime("%H:%M"),
        "publish_time": "09:00",
        "is_sample": (os.environ.get("KBO_MODE", "sample") != "live"),
        "games_date": kbo.get("games_date", "어제"),
        "standings_date": kbo.get("standings_date", ""),
        "archive_dates": build_archive_bar(today_dt),
        "summary": build_summary(kbo, hot),
        "games": kbo["games"],
        "standings": kbo["standings"],
        "hot_issues": hot,
        "ops_issues": ops,
        "buzz": buzz or [{"topic": "데이터 수집 중", "pct": 50}],
        "attendance": kbo["attendance"],
    }
    html = render(data)
    open(out_path, "w", encoding="utf-8").write(html)
    build_index()
    print(f"완료 → {out_path}  ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
