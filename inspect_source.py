# -*- coding: utf-8 -*-
"""KBO 공식 스코어보드 HTML 구조를 확인 (테이블/이닝 위치)."""
import re, requests
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)","Referer":"https://www.koreabaseball.com/"}

def main():
    u="https://www.koreabaseball.com/Schedule/ScoreBoard.aspx"
    html=requests.get(u,headers=UA,timeout=20).text
    print("길이:",len(html))

    # 1) 스코어보드 테이블(들) 위치 파악: class에 'score' 들어간 요소
    classes=set(re.findall(r'class="([^"]*[Ss]core[^"]*)"',html))
    print("\nscore 관련 class:",sorted(classes)[:20])

    # 2) 'tbl' 계열 테이블 class
    tbls=set(re.findall(r'class="(tbl[^"]*)"',html))
    print("tbl 계열 class:",sorted(tbls)[:20])

    # 3) 삼성이 나오는 첫 지점 주변 800자 (실제 마크업 모양 보기)
    i=html.find("삼성")
    if i>0:
        chunk=html[max(0,i-400):i+400]
        chunk=re.sub(r'\s+',' ',chunk)
        print("\n--- '삼성' 주변 마크업 ---\n",chunk)

    # 4) 이닝별 숫자가 담긴 테이블 흔적: <td> 안 한 자리 숫자 연속
    rows=re.findall(r'<tr[^>]*>.*?</tr>',html,re.S)
    print("\n<tr> 개수:",len(rows))
    # 점수판스러운 행(숫자 여러 개 든 tr) 2개만 샘플 출력
    cnt=0
    for r in rows:
        nums=re.findall(r'>(\d{1,2})<',r)
        if len(nums)>=9:
            clean=re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',r)).strip()
            print(f"\n[점수판 후보] 숫자{len(nums)}개:",clean[:200])
            cnt+=1
            if cnt>=3: break

if __name__=="__main__": main()
