# -*- coding: utf-8 -*-
"""
render_html.py
데이터 dict 하나를 받아서, 승인된 샘플과 동일한 디자인의 KBO 데일리 클리핑 HTML을 만든다.
수집 로직과 완전히 분리돼 있어서, 데이터 구조만 맞으면 어떤 소스에서 와도 렌더링된다.
"""
from html import escape

# ── 디자인 시스템 (샘플과 동일: navy #14224A / Pretendard / coral·blue 액센트) ──
CSS = """
:root{--navy:#14224A;--navy-2:#1E3163;--coral:#FF5A4D;--blue:#3B6EF6;--bg:#F4F5F8;--card:#FFFFFF;--line:#E5E7EE;--ink:#14224A;--muted:#6B7280;--win:#1E9E6A;--draw:#8A8F9C;--amber:#C4841D;--purple:#6C4BD8;--red:#C0392B;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Pretendard',-apple-system,BlinkMacSystemFont,system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.5;-webkit-font-smoothing:antialiased;}
a{color:inherit;text-decoration:none;}
.wrap{max-width:1120px;margin:22px auto 0;padding:0 20px 64px;}
header{background:var(--navy);color:#fff;padding:24px 0 20px;}
.header-inner{max-width:1120px;margin:0 auto;padding:0 20px;display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:12px;}
.brand{display:flex;align-items:center;gap:12px;}
.brand .dot{width:10px;height:34px;background:var(--coral);border-radius:2px;}
.brand h1{font-size:22px;font-weight:800;letter-spacing:-.02em;}
.brand .sub{font-size:12px;color:#A9B3D0;font-weight:500;margin-top:2px;}
.header-meta{text-align:right;font-size:12px;color:#A9B3D0;}
.header-meta .date{font-size:16px;font-weight:700;color:#fff;}
.header-meta .fresh{color:#7FE0B0;font-weight:600;}
.sample-tag{display:inline-block;background:rgba(255,90,77,.15);color:#FF8A80;border:1px solid rgba(255,90,77,.4);font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px;margin-top:6px;}
.archive{background:var(--navy-2);}
.archive-inner{max-width:1120px;margin:0 auto;padding:9px 20px;display:flex;align-items:center;gap:10px;overflow-x:auto;}
.archive-lbl{font-size:11px;font-weight:800;color:#A9B3D0;white-space:nowrap;letter-spacing:.03em;}
.archive a{font-size:12px;font-weight:600;color:#C8D0E8;background:rgba(255,255,255,.06);padding:4px 10px;border-radius:6px;white-space:nowrap;}
.archive a:hover{background:rgba(255,255,255,.14);}
.archive a.on{background:var(--coral);color:#fff;}
.summary{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 20px;margin-bottom:22px;display:flex;gap:22px;flex-wrap:wrap;}
.summary .lead{font-size:12px;font-weight:800;color:var(--coral);letter-spacing:.04em;align-self:center;white-space:nowrap;}
.summary ul{list-style:none;display:flex;gap:24px;flex-wrap:wrap;flex:1;}
.summary li{font-size:14px;font-weight:500;position:relative;padding-left:14px;}
.summary li::before{content:"";position:absolute;left:0;top:9px;width:5px;height:5px;border-radius:50%;background:var(--blue);}
.summary b{font-weight:800;}
section{margin-bottom:26px;}
.sec-head{display:flex;align-items:center;gap:9px;margin-bottom:12px;}
.sec-head .bar{width:4px;height:18px;background:var(--navy);border-radius:2px;}
.sec-head h2{font-size:16px;font-weight:800;letter-spacing:-.01em;}
.sec-head .tag{font-size:11px;color:var(--muted);font-weight:600;margin-left:auto;}
.grid{display:grid;grid-template-columns:1.15fr 1fr;gap:22px;}
@media (max-width:860px){.grid{grid-template-columns:1fr;}}
.games{display:flex;flex-direction:column;gap:8px;}
.game{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 16px;display:flex;align-items:center;gap:12px;cursor:pointer;transition:border-color .15s,box-shadow .15s;}
.game:hover{border-color:#C7CEDE;box-shadow:0 2px 8px rgba(20,34,74,.06);}
.game.expanded{border-color:var(--navy);border-bottom-left-radius:0;border-bottom-right-radius:0;}
.team{flex:1;display:flex;align-items:center;justify-content:space-between;}
.team .name{font-size:14px;font-weight:600;}
.team .score{font-size:20px;font-weight:800;font-variant-numeric:tabular-nums;min-width:28px;text-align:center;}
.vs{color:var(--muted);font-size:12px;font-weight:700;padding:0 4px;}
.win .name,.win .score{color:var(--navy);}
.lose .name,.lose .score{color:#A7ADBB;}
.badge{font-size:10px;font-weight:800;padding:2px 7px;border-radius:5px;color:#fff;flex-shrink:0;}
.badge.w{background:var(--win);}.badge.d{background:var(--draw);}
.chev{color:#B4BAC6;font-size:12px;font-weight:700;flex-shrink:0;transition:transform .18s;}
.game.expanded .chev{transform:rotate(180deg);color:var(--navy);}
.game-detail{display:none;background:#FBFBFD;border:1px solid var(--navy);border-top:none;border-radius:0 0 10px 10px;padding:14px 16px 15px;margin-top:-8px;}
.scorebox{background:#fff;border:1px solid var(--line);border-radius:8px;padding:10px 10px 4px;margin-bottom:11px;overflow-x:auto;}
table.linescore{border-collapse:collapse;font-size:12px;width:100%;min-width:340px;}
table.linescore th,table.linescore td{padding:5px 6px;text-align:center;font-variant-numeric:tabular-nums;}
table.linescore thead th{color:#A0A6B2;font-weight:700;font-size:10.5px;border-bottom:1px solid var(--line);}
table.linescore td.tm,table.linescore th.tm{text-align:left;font-weight:700;min-width:44px;color:var(--navy);}
table.linescore td.rr{font-weight:800;color:var(--navy);border-left:1px solid var(--line);}
table.linescore tr.awin td.rr{color:var(--coral);}
.ls-note{font-size:10.5px;color:#A0A6B2;padding:4px 2px 2px;}
.wls{display:flex;flex-wrap:wrap;gap:6px 14px;margin-bottom:11px;}
.wls-item{font-size:12.5px;display:flex;align-items:center;gap:6px;}
.wls-k{font-size:10px;font-weight:800;padding:2px 7px;border-radius:5px;white-space:nowrap;}
.wls-k.w{background:#EAF7F0;color:var(--win);}.wls-k.l{background:#FDECEC;color:var(--red);}
.wls-k.s{background:#EEF3FF;color:var(--blue);}.wls-k.gw{background:#FBF3E3;color:var(--amber);}
.wls-k.d{background:#F0F1F5;color:var(--navy);}
.wls-v{font-weight:600;color:#3A4256;}.wls-v.mute{color:#AEB4C0;font-weight:500;}
.gd-flow{font-size:13px;color:#3A4256;line-height:1.6;margin-bottom:10px;}
.gd-flow b{color:var(--navy);font-weight:700;}
.gd-label{font-size:11px;font-weight:800;color:var(--muted);letter-spacing:.03em;margin-bottom:6px;}
.gd-tags{display:flex;flex-direction:column;gap:6px;}
.gd-tag{display:flex;gap:8px;align-items:baseline;font-size:12.5px;line-height:1.5;}
.gd-tag .k{font-size:10px;font-weight:800;padding:2px 7px;border-radius:5px;flex-shrink:0;white-space:nowrap;}
.k.rec{background:#EAF7F0;color:var(--win);}.k.inj{background:#FFF0EE;color:var(--coral);}
.k.riv{background:#F3EEFC;color:var(--purple);}.k.hr{background:#FBF3E3;color:var(--amber);}
.k.eject{background:#FDECEC;color:var(--red);}.k.draw{background:#F0F1F5;color:var(--navy);}
.gd-tag .v{color:#3A4256;}
.stand{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;}
table.st{width:100%;border-collapse:collapse;font-size:13px;}
table.st thead th{background:#F0F2F7;color:var(--muted);font-weight:700;font-size:11px;text-align:center;padding:9px 6px;}
table.st thead th.tl{text-align:left;padding-left:16px;}
table.st tbody td{padding:8px 6px;text-align:center;border-top:1px solid var(--line);font-variant-numeric:tabular-nums;}
table.st tbody td.tl{text-align:left;padding-left:16px;font-weight:700;}
table.st tbody tr:nth-child(-n+3) td{background:#FBFBFD;}
.rank{font-weight:800;width:26px;}.rank.top{color:var(--coral);}
.issues{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden;}
.issue{padding:14px 16px;border-top:1px solid var(--line);}
.issue:first-child{border-top:none;}
.issue-top{display:flex;align-items:center;gap:8px;margin-bottom:6px;}
.cat{display:inline-block;font-size:10px;font-weight:800;padding:2px 8px;border-radius:5px;letter-spacing:.02em;white-space:nowrap;}
.cat.record{background:#EAF7F0;color:var(--win);}.cat.biz{background:#FFF0EE;color:var(--coral);}
.cat.media{background:#EEF3FF;color:var(--blue);}.cat.rule{background:#F0F1F5;color:var(--navy);}
.cat.judge{background:#F3EEFC;color:var(--purple);}.cat.game{background:#FBF3E3;color:var(--amber);}
.cat.incident{background:#FDECEC;color:var(--red);}
.issue .when{font-size:11px;color:#A0A6B2;font-weight:600;margin-left:auto;white-space:nowrap;}
.issue .when.hot{color:var(--coral);}
.issue h3{font-size:14px;font-weight:700;margin-bottom:4px;letter-spacing:-.01em;}
.issue p{font-size:13px;color:var(--muted);line-height:1.55;margin-bottom:7px;}
.src{display:inline-flex;align-items:center;gap:5px;font-size:12px;font-weight:600;color:var(--blue);}
.src:hover{text-decoration:underline;}
.src .out{color:#B4BAC6;font-weight:500;}
.buzz{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;}
.buzz-row{display:flex;align-items:center;gap:12px;padding:9px 0;border-top:1px solid var(--line);}
.buzz-row:first-child{border-top:none;padding-top:0;}
.buzz-rank{font-size:13px;font-weight:800;color:var(--coral);width:20px;}
.buzz-topic{flex:1;font-size:13px;font-weight:600;}
.buzz-bar-wrap{width:88px;height:6px;background:#EEF0F5;border-radius:4px;overflow:hidden;}
.buzz-bar{height:100%;background:var(--blue);border-radius:4px;}
.disclaimer{font-size:11px;color:#9AA0AC;background:#EEF0F5;border-radius:6px;padding:5px 9px;margin-top:8px;display:inline-block;}
.att{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;}
.att-card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;}
.att-card .lbl{font-size:12px;color:var(--muted);font-weight:600;margin-bottom:6px;}
.att-card .val{font-size:22px;font-weight:800;color:var(--navy);font-variant-numeric:tabular-nums;letter-spacing:-.01em;}
.att-card .val small{font-size:13px;font-weight:600;color:var(--muted);}
.att-card .note{font-size:11px;color:var(--coral);font-weight:700;margin-top:5px;}
footer{margin-top:40px;padding-top:18px;border-top:1px solid var(--line);font-size:11px;color:var(--muted);line-height:1.7;}
footer b{color:var(--ink);}
"""

TOGGLE_JS = """
<script>
document.querySelectorAll('.game').forEach(function(g){
  g.addEventListener('click',function(){
    var d=g.nextElementSibling;
    if(d&&d.classList.contains('game-detail')){
      var open=d.style.display==='block';
      d.style.display=open?'none':'block';
      g.classList.toggle('expanded',!open);
    }
  });
});
</script>
"""


def _e(s):
    return escape(str(s)) if s is not None else ""


def _linescore(ls):
    """이닝별 라인스코어 테이블. ls가 None이면 빈 문자열."""
    if not ls:
        return ""
    labels = ls.get("labels") or [str(i) for i in range(1, len(ls["innings_away"]) + 1)]
    head = "".join(f"<th>{_e(x)}</th>" for x in labels)
    away = "".join(f"<td>{_e(x)}</td>" for x in ls["innings_away"])
    home = "".join(f"<td>{_e(x)}</td>" for x in ls["innings_home"])
    note = f'<div class="ls-note">{_e(ls.get("note",""))}</div>' if ls.get("note") else ""
    return f"""<div class="scorebox"><table class="linescore">
<thead><tr><th class="tm"></th>{head}<th>R</th></tr></thead>
<tbody>
<tr class="awin"><td class="tm">{_e(ls['away_name'])}</td>{away}<td class="rr">{_e(ls['r_away'])}</td></tr>
<tr><td class="tm">{_e(ls['home_name'])}</td>{home}<td class="rr">{_e(ls['r_home'])}</td></tr>
</tbody></table>{note}</div>"""


def _wls(g):
    """승·패·세이브·결승타 스트립. 무승부면 해당 없음 표시."""
    if g.get("draw"):
        return ('<div class="wls"><div class="wls-item"><span class="wls-k d">무승부</span>'
                '<span class="wls-v mute">승·패·세이브·결승타 해당 없음</span></div></div>')
    w = g.get("wls", {}) or {}
    def item(k_cls, label, val):
        if val:
            return f'<div class="wls-item"><span class="wls-k {k_cls}">{label}</span><span class="wls-v">{_e(val)}</span></div>'
        return f'<div class="wls-item"><span class="wls-k {k_cls}">{label}</span><span class="wls-v mute">자동 연동</span></div>'
    parts = [item("w", "승", w.get("win")), item("l", "패", w.get("lose")),
             item("s", "세이브", w.get("save")), item("gw", "결승타", w.get("gw"))]
    return f'<div class="wls">{"".join(parts)}</div>'


def _game(g):
    aw, hm = g["away"], g["home"]
    a_cls = "win" if aw.get("win") else ("" if g.get("draw") else "lose")
    h_cls = "win" if hm.get("win") else ("" if g.get("draw") else "lose")
    if g.get("draw"):
        badge = '<span class="badge d">무</span>'
    else:
        wname = aw["name"] if aw.get("win") else hm["name"]
        badge = f'<span class="badge w">{_e(wname)}</span>'
    row = (f'<div class="game"><div class="team {a_cls}"><span class="name">{_e(aw["name"])}</span>'
           f'<span class="score">{_e(aw["score"])}</span></div><span class="vs">vs</span>'
           f'<div class="team {h_cls}"><span class="score">{_e(hm["score"])}</span>'
           f'<span class="name">{_e(hm["name"])}</span></div>{badge}<span class="chev">▾</span></div>')
    tags = "".join(
        f'<div class="gd-tag"><span class="k {t.get("cls","draw")}">{_e(t["k"])}</span>'
        f'<span class="v">{_e(t["v"])}</span></div>' for t in g.get("tags", []))
    tags_block = f'<div class="gd-label">특이사항</div><div class="gd-tags">{tags}</div>' if tags else ""
    flow = f'<div class="gd-flow">{g.get("flow","")}</div>' if g.get("flow") else ""
    detail = (f'<div class="game-detail">{_linescore(g.get("linescore"))}{_wls(g)}{flow}{tags_block}</div>')
    return row + detail


def _issue(it):
    hot = " hot" if it.get("hot") else ""
    src = ""
    if it.get("src_url"):
        out = it.get("src_tail", "· 기사 원문")
        src = (f'<a class="src" href="{_e(it["src_url"])}" target="_blank" rel="noopener">🔗 '
               f'{_e(it.get("src_name","원문"))} <span class="out">{_e(out)}</span></a>')
    return (f'<div class="issue"><div class="issue-top"><span class="cat {it.get("cat_cls","game")}">'
            f'{_e(it["cat"])}</span><span class="when{hot}">{_e(it["when"])}</span></div>'
            f'<h3>{_e(it["title"])}</h3><p>{_e(it["desc"])}</p>{src}</div>')


def _archive(dates):
    links = "".join(
        f'<a class="{"on" if d.get("on") else ""}" href="{_e(d["href"])}">{_e(d["label"])}</a>'
        for d in dates)
    return (f'<div class="archive"><div class="archive-inner"><span class="archive-lbl">📁 지난 클리핑</span>'
            f'{links}<a href="index.html">전체 보기 →</a></div></div>')


def render(d):
    sample = '<div class="sample-tag">SAMPLE · 형식 확인용</div>' if d.get("is_sample") else ""
    summary = "".join(f"<li>{s}</li>" for s in d.get("summary", []))
    games = "".join(_game(g) for g in d.get("games", []))
    standings = "".join(
        f'<tr><td class="rank{" top" if r["rank"]<=3 else ""}">{r["rank"]}</td>'
        f'<td class="tl">{_e(r["team"])}</td><td>{r["w"]}</td><td>{r["d"]}</td><td>{r["l"]}</td></tr>'
        for r in d.get("standings", []))
    hot = "".join(_issue(i) for i in d.get("hot_issues", []))
    ops = "".join(_issue(i) for i in d.get("ops_issues", []))
    buzz = "".join(
        f'<div class="buzz-row"><span class="buzz-rank">{n+1}</span>'
        f'<span class="buzz-topic">{_e(b["topic"])}</span>'
        f'<span class="buzz-bar-wrap"><span class="buzz-bar" style="width:{int(b["pct"])}%;"></span></span></div>'
        for n, b in enumerate(d.get("buzz", [])))
    att = "".join(
        f'<div class="att-card"><div class="lbl">{_e(a["lbl"])}</div>'
        f'<div class="val">{a["val"]}</div><div class="note">{_e(a.get("note",""))}</div></div>'
        for a in d.get("attendance", []))
    return f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KBO 데일리 클리핑 · {_e(d.get("date_label",""))}</title>
<link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css">
<style>{CSS}</style></head><body>
<header><div class="header-inner">
<div class="brand"><div class="dot"></div><div><h1>KBO 데일리 클리핑</h1>
<div class="sub">운영팀 모니터링 리포트 · 2026 신한 SOL KBO 리그</div></div></div>
<div class="header-meta"><div class="date">{_e(d.get("date_label",""))}</div>
<div><span class="fresh">최종 수집 {_e(d.get("collected_time","-"))}</span> · 배포 {_e(d.get("publish_time","09:00"))}</div>
{sample}</div></div></header>
{_archive(d.get("archive_dates", []))}
<div class="wrap">
<div class="summary"><div class="lead">오늘의 핵심</div><ul>{summary}</ul></div>
<div class="grid">
<section><div class="sec-head"><span class="bar"></span><h2>어제 경기 결과</h2>
<span class="tag">{_e(d.get("games_date","어제"))} · 카드 클릭 시 스코어보드 ▾</span></div>
<div class="games">{games}</div></section>
<section><div class="sec-head"><span class="bar"></span><h2>팀 순위</h2><span class="tag">{_e(d.get("standings_date",""))} 기준</span></div>
<div class="stand"><table class="st"><thead><tr><th>순위</th><th class="tl">팀</th><th>승</th><th>무</th><th>패</th></tr></thead>
<tbody>{standings}</tbody></table></div></section>
</div>
<div class="grid" style="align-items:start;">
<section style="margin-bottom:0;"><div class="sec-head"><span class="bar" style="background:var(--coral);"></span>
<h2>어제~오늘 핫이슈</h2><span class="tag">최근 24시간</span></div><div class="issues">{hot}</div></section>
<section style="margin-bottom:0;"><div class="sec-head"><span class="bar" style="background:var(--blue);"></span>
<h2>운영 모니터링</h2><span class="tag">매일 갱신 · 최근 7일</span></div><div class="issues">{ops}</div></section>
</div>
<div class="grid" style="align-items:start;margin-top:26px;">
<section style="margin-bottom:0;"><div class="sec-head"><span class="bar" style="background:var(--coral);"></span>
<h2>여론 · 화제성</h2><span class="tag">뉴스 언급량 기준</span></div>
<div class="buzz">{buzz}</div>
<span class="disclaimer">※ 최근 24시간 뉴스 언급량 기반 화제 토픽 (자동 집계)</span></section>
<section style="margin-bottom:0;"><div class="sec-head"><span class="bar"></span><h2>관중 · 흥행 지표</h2>
<span class="tag">{_e(d.get("standings_date",""))} 기준</span></div><div class="att">{att}</div></section>
</div>
<footer><b>KBO 데일리 클리핑</b> · 매일 {_e(d.get("publish_time","09:00"))} 자동 생성 · 데이터 출처: KBO 공식 기록 및 각 언론 보도.<br>
운영 모니터링은 최근 7일 이슈 갱신, 여론·화제성은 뉴스 언급량 자동 집계. 지난 리포트는 상단 아카이브에서 열람.</footer>
</div>{TOGGLE_JS}</body></html>"""
