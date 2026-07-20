# KBO 데일리 클리핑

KBO 운영팀 모니터링용 뉴스 클리핑 시스템. 매일 아침 자동으로
**경기 결과(이닝별 라인스코어·승/패/세이브·결승타) · 팀 순위 · 핫이슈 · 운영 모니터링 · 여론 · 관중**을
한 장의 HTML 대시보드로 만들어 GitHub Pages에 올리고, 날짜별로 아카이빙한다.

---

## 폴더 구조

```
kbo-clipping/
├─ run.py                        # 매일 실행되는 오케스트레이터
├─ requirements.txt
├─ src/
│  ├─ collect_kbo.py             # 경기·순위·관중 수집 (live 네이버 / sample 폴백)
│  ├─ collect_news.py            # 뉴스·운영이슈·여론 (Google News RSS, 키 불필요)
│  └─ render_html.py             # 데이터 → HTML (디자인 시스템 고정)
├─ clippings/                    # 산출물: index.html + YYYY-MM-DD.html (자동 누적)
└─ .github/workflows/
   └─ daily-clipping.yml         # 매일 08:50 KST 자동 실행
```

## 빠른 시작 (로컬 테스트)

```bash
pip install -r requirements.txt
python run.py
# → clippings/2026-07-20.html 생성. 브라우저로 열어 확인.
```

`KBO_MODE` 미설정 시 **sample 모드**로 즉시 동작한다(검증된 예시 데이터).
네트워크 없이도 리포트 형태가 그대로 나온다.

## GitHub에 올려 완전 자동화하기

1. 이 폴더를 GitHub 저장소로 push (`main` 브랜치).
2. 저장소 **Settings → Pages** → Source를 `Deploy from a branch`,
   Branch를 `main` / 폴더를 `/clippings` 로 지정.
   → `https://<사용자>.github.io/<저장소>/` 에서 최신 리포트가 열린다.
3. **Settings → Actions → General → Workflow permissions** 를
   `Read and write permissions` 로 설정 (봇이 아카이브를 커밋할 수 있게).
4. 끝. 매일 08:50 KST에 워크플로우가 돌아 리포트를 만들고 커밋한다.
   `Actions` 탭에서 **Run workflow** 로 즉시 테스트도 가능.

> Pages는 공개 저장소에서 무료. 비공개로 쓰려면 GitHub Pro가 필요하다.

## sample → live 전환 (실데이터 수집 켜기)

기본은 sample이다. 실데이터로 바꾸려면 저장소 **Settings → Secrets and variables
→ Actions → Variables** 에 `KBO_MODE = live` 를 추가한다.

`src/collect_kbo.py` 의 라이브 파서는 **네이버 스포츠 JSON**을 사용한다.
네이버가 필드명/엔드포인트를 바꾸면 매핑을 조정해야 한다:

- 첫 live 실행 때 콘솔(Actions 로그)에 응답 구조가 찍힌다.
- `_map_game()` / `_enrich_box()` / `_fetch_standings_live()` 의 키 이름을
  실제 응답에 맞춰 수정한다.
- 라이브 수집이 실패하면 자동으로 sample로 폴백하므로 리포트가 끊기지는 않는다.

관중 수치는 KBO 공식 발표/뉴스에 의존하므로, 정확도가 필요하면 해당 부분을
`collect_news.py` 쪽 뉴스 파싱과 연동해 갱신하는 것을 권장한다.

## 여론·화제성 소스

선택하신 대로 **뉴스 언급량 기반**이다(`collect_news.py`).
최근 24시간 KBO 뉴스 제목에서 팀명·핫 키워드 언급 빈도를 세어 랭킹을 만든다.
무료·안정적이며, 나중에 네이버 검색량 트렌드나 SNS 소스로 바꾸려면
`fetch_news()` 의 여론 집계 블록만 교체하면 된다.

## 커스터마이즈

- **디자인**: `render_html.py` 상단 `CSS`. navy #14224A / Pretendard / coral·blue 고정.
- **운영 모니터링 키워드**: `collect_news.py` 의 `OPS_QUERIES`.
- **배포 시각**: 워크플로우 `cron` (UTC 기준. 08:50 KST = `50 23 * * *`).
- **경기 상세 태그**: `render_html.py` 의 `.k.*` 클래스(부상/천적/홈런/퇴장/무 등).
  벤치클리어링·퇴장도 데이터에 넣으면 자동으로 색 태그가 붙는다.

## 알아둘 점

- 라인스코어·승/패/세이브·결승타는 live 모드에서 KBO 박스스코어(네이버 경유)로
  **전 경기 자동**으로 채워진다. sample 모드에서는 검증된 예시(2026-07-19)만 완전하다.
- GitHub Actions cron은 부하에 따라 몇 분 늦을 수 있다. 09:00 배포 기준 08:50에
  잡아둔 이유다. 더 촉박하면 cron을 앞당기면 된다.
