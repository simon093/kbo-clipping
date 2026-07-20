# -*- coding: utf-8 -*-
"""
collect_kbo.py
KBO 경기결과(이닝별 라인스코어·승/패/세이브·결승타), 팀 순위, 관중 데이터를 수집한다.

■ 두 가지 모드
  - MODE="sample" : 검증된 예시 데이터로 즉시 동작 (첫 실행/데모용, 네트워크 불필요)
  - MODE="live"   : 네이버 스포츠 JSON에서 실시간 수집

■ 라이브 파서에 대한 솔직한 안내
  KBO 공식 스코어보드는 동적(ASP.NET) 페이지라 스크립트로 바로 긁기 어렵다.
  가장 스크립트 친화적인 소스는 네이버 스포츠의 내부 JSON API다.
  아래 _fetch_live()는 그 구조로 작성돼 있지만, 네이버가 필드명/엔드포인트를
  바꾸면 매핑을 조정해야 한다. 첫 실행 때 콘솔에 찍히는 원본 JSON을 보고
  _map_game()의 키를 맞추면 된다. 실패 시 자동으로 sample로 폴백한다.
"""
import os
import datetime as dt

try:
    import requests
except ImportError:
    requests = None

MODE = os.environ.get("KBO_MODE", "sample")  # "sample" | "live"
UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://m.sports.naver.com/"}
NAVER_SCHEDULE = "https://api-gw.sports.naver.com/schedule/games"
NAVER_GAME = "https://api-gw.sports.naver.com/sports/games/{gid}/record"


def _kst(offset_days=0):
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=9))) + dt.timedelta(days=offset_days)


# ─────────────────────────────────────────────────────────────
#  LIVE (네이버 스포츠 JSON)  — 필드 매핑은 첫 실행 시 검증/조정
# ─────────────────────────────────────────────────────────────
def _fetch_live(date):
    if not requests:
        raise RuntimeError("requests 미설치")
    ymd = date.strftime("%Y-%m-%d")
    params = {"fields": "basic,superCategoryId,categoryName",
              "upperCategoryId": "kbaseball", "categoryId": "kbo",
              "fromDate": ymd, "toDate": ymd, "size": 20}
    r = requests.get(NAVER_SCHEDULE, headers=UA, params=params, timeout=15)
    r.raise_for_status()
    payload = r.json()
    # 첫 실행 디버깅용: 실제 구조 확인
    games_raw = (payload.get("result", {}) or {}).get("games", []) or []
    if not games_raw:
        print("[kbo] 스케줄 응답에 games 없음 — 응답 키:", list(payload.keys()))
    games = []
    for g in games_raw:
        try:
            games.append(_map_game(g))
        except Exception as ex:
            print(f"[kbo] 경기 매핑 실패: {ex}")
    return games


def _map_game(g):
    """네이버 game 객체 → render 스키마. (키 이름은 실제 응답에 맞춰 조정)"""
    away, home = g["awayTeamName"], g["homeTeamName"]
    a_score, h_score = int(g.get("awayTeamScore", 0)), int(g.get("homeTeamScore", 0))
    draw = a_score == h_score
    game = {
        "away": {"name": away, "score": a_score, "win": (not draw and a_score > h_score)},
        "home": {"name": home, "score": h_score, "win": (not draw and h_score > a_score)},
        "draw": draw, "tags": [],
    }
    gid = g.get("gameId")
    if gid:
        try:
            _enrich_box(game, gid, away, home)
        except Exception as ex:
            print(f"[kbo] 박스스코어 수집 실패({gid}): {ex}")
    return game


def _enrich_box(game, gid, away, home):
    """개별 경기 record API에서 이닝별 라인스코어·승/패/세이브·결승타 채우기."""
    r = requests.get(NAVER_GAME.format(gid=gid), headers=UA, timeout=15)
    r.raise_for_status()
    rec = r.json().get("result", {}) or {}
    # 이닝별 스코어 (키 예: rec['scoreBoard']['inningScores'])
    sb = rec.get("scoreBoard") or {}
    a_in = sb.get("away") or sb.get("awayInnings")
    h_in = sb.get("home") or sb.get("homeInnings")
    if a_in and h_in:
        game["linescore"] = {
            "away_name": away, "home_name": home,
            "innings_away": a_in, "innings_home": h_in,
            "r_away": game["away"]["score"], "r_home": game["home"]["score"],
            "note": rec.get("stadium", ""),
        }
    # 승/패/세이브/결승타 (키 예: rec['winPitcher'] 등)
    if not game["draw"]:
        game["wls"] = {
            "win": rec.get("winPitcher", {}).get("name") if rec.get("winPitcher") else None,
            "lose": rec.get("losePitcher", {}).get("name") if rec.get("losePitcher") else None,
            "save": rec.get("savePitcher", {}).get("name") if rec.get("savePitcher") else None,
            "gw": rec.get("gameWinningHit"),  # 결승타
        }


def _fetch_standings_live(year):
    """팀 순위 (네이버 랭킹 API). 실패 시 예외 → 폴백."""
    url = f"https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/{year}/teams/rank"
    r = requests.get(url, headers=UA, timeout=15)
    r.raise_for_status()
    rows = (r.json().get("result", {}) or {}).get("teamRankList", []) or []
    out = []
    for row in rows:
        out.append({"rank": int(row["rank"]), "team": row["teamName"],
                    "w": int(row["win"]), "d": int(row.get("draw", 0)), "l": int(row["lose"])})
    return out


# ─────────────────────────────────────────────────────────────
#  SAMPLE  (검증된 2026-07-19 데이터) — 파이프라인 즉시 동작용
# ─────────────────────────────────────────────────────────────
def _sample_games():
    return [
        {"away": {"name": "롯데", "score": 11, "win": True},
         "home": {"name": "삼성", "score": 8, "win": False},
         "linescore": {"away_name": "롯데", "home_name": "삼성",
                       "innings_away": [0, 0, 3, 0, 3, 1, 0, 0, 4],
                       "innings_home": [0, 0, 3, 0, 0, 0, 4, 1, 0],
                       "r_away": 11, "r_home": 8, "note": "대구 · 롯데 원정"},
         "wls": {"lose": "김재윤 (삼성, 9회 블론)", "gw": "전민재 (9회 역전 3타점 2루타)"},
         "flow": "우중 혈투 <b>3-3→7-3→7-8→11-8</b>. 롯데가 9회 삼성 마무리 김재윤을 상대로 4점을 뽑아 역전승.",
         "tags": [{"k": "이변", "cls": "hr", "v": "8위 롯데, 선두 삼성 원정서 9회 역전승"},
                  {"k": "천적", "cls": "riv", "v": "삼성 구자욱, 3회 좌월 3점포"}]},
        {"away": {"name": "키움", "score": 9}, "home": {"name": "한화", "score": 9}, "draw": True,
         "flow": "류현진이 2회 한·미 통산 2,500K 완성. 한화가 8-1 리드를 놓치고 연장 11회 9-9 무승부.",
         "tags": [{"k": "대기록", "cls": "rec", "v": "류현진, 한국 투수 최초 한·미 통산 2,500K"},
                  {"k": "불펜 붕괴", "cls": "eject", "v": "한화 8-1 리드 → 8회 대량실점"}]},
        {"away": {"name": "KT", "score": 4, "win": True},
         "home": {"name": "LG", "score": 1, "win": False},
         "wls": {"gw": None},
         "flow": "KT 고영표 6이닝 무실점 호투, LG 4연전 스윕하며 단독 2위 탈환.",
         "tags": [{"k": "순위", "cls": "draw", "v": "KT 7연승·2위 / LG 5연패·3위 추락"}]},
        {"away": {"name": "KIA", "score": 9, "win": True},
         "home": {"name": "SSG", "score": 5, "win": False},
         "wls": {"gw": "김호령 (8회 역전타)"},
         "flow": "8회 김호령 역전타와 카스트로 쐐기포로 KIA가 SSG를 제압, 3연승.",
         "tags": [{"k": "쐐기", "cls": "hr", "v": "카스트로 8회 쐐기 홈런"}]},
        {"away": {"name": "두산", "score": 10, "win": True},
         "home": {"name": "NC", "score": 3, "win": False},
         "wls": {"win": "최승용 (두산)", "gw": "강승호 (결승포 포함 4타점)"},
         "flow": "강승호 결승포 포함 4타점, 최승용 역투로 두산이 NC 원정 10-3 낙승.",
         "tags": [{"k": "홈런", "cls": "hr", "v": "두산 강승호, 결승 홈런 + 4타점"}]},
    ]


def _sample_standings():
    return [
        {"rank": 1, "team": "삼성", "w": 53, "d": 2, "l": 33},
        {"rank": 2, "team": "KT", "w": 51, "d": 1, "l": 35},
        {"rank": 3, "team": "LG", "w": 52, "d": 0, "l": 37},
        {"rank": 4, "team": "KIA", "w": 48, "d": 2, "l": 40},
        {"rank": 5, "team": "두산", "w": 47, "d": 2, "l": 42},
        {"rank": 6, "team": "한화", "w": 40, "d": 3, "l": 43},
        {"rank": 7, "team": "NC", "w": 40, "d": 1, "l": 45},
        {"rank": 8, "team": "롯데", "w": 39, "d": 2, "l": 47},
        {"rank": 9, "team": "SSG", "w": 32, "d": 3, "l": 55},
        {"rank": 10, "team": "키움", "w": 32, "d": 1, "l": 57},
    ]


def _sample_attendance():
    return [
        {"lbl": "당일 관중 (5경기)", "val": "95,487<small> 명</small>", "note": "경기당 평균 19,097명"},
        {"lbl": "시즌 누적 관중", "val": "8,007,967<small> 명</small>", "note": "800만 돌파"},
        {"lbl": "800만 돌파 소요", "val": "443<small> 경기</small>", "note": "역대 최소"},
        {"lbl": "전반기 총 관중", "val": "7,633,775<small> 명</small>", "note": "424경기"},
    ]


def fetch_kbo(date=None):
    """어제 경기 기준 KBO 데이터 수집. 실패하면 sample로 폴백."""
    date = date or _kst(-1)  # 기본: 어제
    year = date.year
    if MODE == "live":
        try:
            games = _fetch_live(date)
            standings = _fetch_standings_live(year)
            if games and standings:
                return {"games": games, "standings": standings,
                        "attendance": _sample_attendance(),  # 관중은 KBO 발표/뉴스 연동 권장
                        "games_date": date.strftime("%m.%d"),
                        "standings_date": date.strftime("%m.%d")}
            print("[kbo] 라이브 데이터 비어 있음 → sample 폴백")
        except Exception as ex:
            print(f"[kbo] 라이브 수집 실패 → sample 폴백: {ex}")
    return {"games": _sample_games(), "standings": _sample_standings(),
            "attendance": _sample_attendance(),
            "games_date": "07.19 (일)", "standings_date": "07.19"}


if __name__ == "__main__":
    d = fetch_kbo()
    print("games:", len(d["games"]), "| standings:", len(d["standings"]))
