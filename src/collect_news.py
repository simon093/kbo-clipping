# -*- coding: utf-8 -*-
"""
collect_news.py
Google News RSS로 KBO 뉴스/이슈/여론을 수집한다. (API 키 불필요, 무료)
- 핫이슈: 최근 24시간 KBO 일반 뉴스
- 운영 모니터링: 중계/판정/관중/제도/사건 등 운영 키워드별 최근 7일 뉴스
- 여론·화제성: 최근 뉴스에서 토픽 언급량을 세어 랭킹 (사용자 선택: '뉴스 언급량 기반')
"""
import datetime as dt
import urllib.parse
import re

try:
    import requests
except ImportError:
    requests = None
try:
    import feedparser
except ImportError:
    feedparser = None

UA = {"User-Agent": "Mozilla/5.0 (compatible; kbo-clipping/1.0)"}

def _rss(query, when="1d"):
    """구글 뉴스 RSS 검색. when: '1d','7d' 등 (구글 when: 연산자)."""
    q = f"{query} when:{when}"
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": q, "hl": "ko", "gl": "KR", "ceid": "KR:ko"})
    if not (requests and feedparser):
        return []
    try:
        r = requests.get(url, headers=UA, timeout=15)
        feed = feedparser.parse(r.content)
        out = []
        for e in feed.entries:
            title = re.sub(r"\s*-\s*[^-]+$", "", e.title).strip()  # 끝의 " - 매체명" 제거
            source = getattr(getattr(e, "source", None), "title", "") or ""
            out.append({"title": e.title, "clean_title": title, "url": e.link,
                        "source": source, "published": getattr(e, "published", "")})
        return out
    except Exception as ex:
        print(f"[news] RSS 실패 ({query}): {ex}")
        return []


# 운영 모니터링: (카테고리, css클래스, 검색어) — 운영팀이 챙겨야 할 리그 운영 이슈
OPS_QUERIES = [
    ("중계 사고",   "incident", "KBO 중계 중단 OR 송출 OR 비디오판독"),
    ("중계·미디어", "media",    "KBO 중계권 OR 티빙 OR 유료중계"),
    ("판정·ABS",    "judge",    "KBO ABS OR 심판 OR 판정 논란"),
    ("흥행·마케팅", "biz",      "KBO 관중 OR 마케팅 OR 흥행 OR 암표"),
    ("제도·운영",   "rule",     "KBO 엔트리 OR 규정 OR 제도 OR 일정"),
    ("사건·사고",   "incident", "KBO 사건 OR 논란 OR 징계 OR 벤치클리어링"),
]

HOT_QUERIES = [
    ("기록·달성", "record", "KBO 대기록 OR 신기록 OR 달성"),
    ("이슈",      "game",   "KBO 프로야구"),
]

TEAMS = ["삼성", "KT", "LG", "KIA", "두산", "한화", "NC", "롯데", "SSG", "키움"]


def _today():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=9)))  # KST


def fetch_news():
    """핫이슈, 운영 이슈, 여론 버즈를 수집해 render 스키마로 반환."""
    today = _today()
    hot, ops, seen = [], [], set()

    for cat, cls, q in HOT_QUERIES:
        for e in _rss(q, "1d")[:6]:
            if e["url"] in seen:
                continue
            seen.add(e["url"])
            hot.append({"cat": cat, "cat_cls": cls, "when": today.strftime("%m.%d"),
                        "title": e["clean_title"], "desc": "", "src_name": e["source"] or "뉴스",
                        "src_url": e["url"]})
        if len(hot) >= 4:
            break
    hot = hot[:4]

    for cat, cls, q in OPS_QUERIES:
        items = _rss(q, "7d")
        if not items:
            continue
        e = items[0]
        if e["url"] in seen:
            e = items[1] if len(items) > 1 else e
        seen.add(e["url"])
        # 중계 사고/사건은 '핫'하게 표시
        hot_flag = cls == "incident"
        ops.append({"cat": cat, "cat_cls": cls,
                    "when": "지속" if not hot_flag else today.strftime("%m.%d"),
                    "hot": hot_flag, "title": e["clean_title"], "desc": "",
                    "src_name": e["source"] or "뉴스", "src_url": e["url"]})
    ops = ops[:5]

    # ── 여론·화제성: 최근 24시간 뉴스 제목에서 토픽 언급량 집계 ──
    corpus = _rss("KBO", "1d") + _rss("프로야구", "1d")
    titles = " ".join(x["clean_title"] for x in corpus)
    counts = {}
    for t in TEAMS:
        c = titles.count(t)
        if c:
            counts[t] = c
    # 핫 키워드도 토픽 후보로
    for kw in ["대기록", "관중", "중계", "부상", "역전", "홈런", "논란"]:
        c = titles.count(kw)
        if c:
            counts[kw] = c
    ranked = sorted(counts.items(), key=lambda x: -x[1])[:4]
    top = ranked[0][1] if ranked else 1
    buzz = [{"topic": k, "pct": max(30, int(v / top * 100))} for k, v in ranked]

    return hot, ops, buzz


if __name__ == "__main__":
    h, o, b = fetch_news()
    print("HOT:", len(h), "| OPS:", len(o), "| BUZZ:", b)
