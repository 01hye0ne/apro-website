#!/usr/bin/env python3
"""시안 C 생성기

    python _gen-c.py          # *-c.html 을 다시 만든다 (index-c.html 은 빼고)
    python _gen-c.py --check   # 다시 만들지 않고, 지금 파일이 최신인지만 알려준다

시안 C (2026-09-28) = A 와 A-1 을 합친 시안.
  1. 전체 시스템  : A-1  — 머리 바 · 격자 · 글자 사다리 · 페이지 짜임 모두 A-1
  2. 메가메뉴 방식 : A    — 한 장짜리 화면 폭 판, 대분류 밑에 하위 메뉴 열 (gnb-c.css / gnb-c.js)
  3. 페이지       : 홈만 섞는다 — 히어로 · News 는 A, Business · Who we are 는 A-1.
                    나머지 장은 전부 A-1

그래서 홈을 뺀 C 는 A-1 의 복제다. 원본은 *-a1.html 이고 *-c.html 은 전부 여기서 나온다 —
C 파일을 직접 고치면 다음 실행 때 덮어써진다. A-1 을 고친 뒤 이 스크립트를 돌리면 C 에
그대로 넘어간다.

⚠ index-c.html(홈)은 여기 없다 — A 의 히어로 · News 와 A-1 의 Business · Who we are 를
  손으로 이어 붙인 장이라 손으로 고친다. 머리 바 · 메가 판 · 전체메뉴 · 푸터는 아래
  build() 가 다른 장에 넣는 것과 같은 벌이므로, 그 껍데기를 고칠 일이 생기면 홈도 함께 고친다.

하는 일 (A-1 → C)
  1. <title> 끝의 (A-1) → (C)
  2. 페이지 링크 X-a1.html → X-c.html        C 안에서 돌아다니면 C 만 나온다
  3. A-1 메가 판(#mega-biz … #mega-cmm) + 흐림막(#sfScrim) → C 메가 판 한 장(#cMega)
  4. gnb-c.css · margin-c.css(좌우 여백 A 사다리) · type-c.css(줄높이 빈칸)를 </head> 앞에, gnb-c.js 를 </body> 앞에 붙인다

A-1 의 머리 바 마크업(li[data-mega])과 판 스크립트는 건드리지 않는다 — 가리키던 판이
없어져 그 스크립트는 조용히 지나가고, 같은 묶음 안의 언어 선택은 그대로 동작한다.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent

# 손으로 고치는 C — 생성하지 않는다
HAND = {'index-a1.html'}

# C 메가 판 — 열 순서는 머리 바의 대분류 순서(사업영역 · 회사정보 · 투자정보 · 지속가능경영 · 커뮤니티)와 같아야 한다
MEGA_COLS = [
    [('business-smart-c.html', '스마트 제조'), ('business-energy-c.html', '에너지 인프라'),
     ('business-ai-c.html', '인공지능 플랫폼'), ('business-semicon-c.html', '화합물 전력 반도체')],
    [('company-c.html', '회사 소개'), ('network-c.html', '글로벌 네트워크'), ('locations-c.html', '사업장소재')],
    [('ir-finance-c.html', '재무정보'), ('ir-disclosure-c.html', '공시정보'), ('ir-stock-c.html', '주식정보')],
    [('esg-environment-c.html', '환경'), ('esg-social-c.html', '사회'), ('esg-governance-c.html', '지배구조'),
     ('esg-report-c.html', '내/외부 신고채널'), ('esg-board-c.html', 'ESG 게시판')],
    [('community-notice-c.html', '공지사항'), ('community-press-c.html', '보도자료')],
]


def mega_html(current=None):
    """C 메가 판. current 가 주어지면 그 장 링크에 aria-current 를 단다"""
    out = ['<!-- 메가 판 — 시안 C 는 A 의 방식: 한 장이 화면 폭으로 열리고, 하위 메뉴가 제 대분류 밑에 선다 (gnb-c.css) -->',
           '<div class="c-mega" id="cMega" aria-hidden="true" aria-label="전체 메뉴">',
           '  <div class="c-cols">']
    for col in MEGA_COLS:
        links = ''.join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == current else '', t)
                        for h, t in col)
        out.append('    <div class="c-col">%s</div>' % links)
    out += ['  </div>', '</div>']
    return '\n'.join(out)


MEGA_RE = re.compile(r'[ \t]*<div class="sf-mega.*?<div class="sf-scrim" id="sfScrim" aria-hidden="true"></div>',
                     re.S)


def c_name(a1_name):
    return a1_name[:-len('-a1.html')] + '-c.html'


def build(src, name):
    nl = '\r\n' if '\r\n' in src else '\n'     # 원본 줄바꿈을 따른다(작업 트리는 CRLF)
    s = src
    s = re.sub(r'\(A-1\)</title>', '(C)</title>', s, count=1)
    s = s.replace('-a1.html', '-c.html')
    if 'class="sf-gnb' in s:
        s, n = MEGA_RE.subn(lambda m: mega_html(name).replace('\n', nl), s, count=1)
        if n != 1:
            raise SystemExit('%s: A-1 메가 판 묶음을 찾지 못했다' % name)
        s = s.replace('</head>', '<link rel="stylesheet" href="gnb-c.css" />' + nl
                      + '<link rel="stylesheet" href="margin-c.css" />' + nl
                      + '<link rel="stylesheet" href="type-c.css" />' + nl + '</head>', 1)
        s = s.replace('</body>', '<script src="gnb-c.js"></script>' + nl + '</body>', 1)
    return s


def main():
    check = '--check' in sys.argv
    stale = []
    for p in sorted(HERE.glob('*-a1.html')):
        if p.name in HAND:
            continue
        name = c_name(p.name)
        out = build(p.read_bytes().decode('utf-8'), name).encode('utf-8')
        dst = HERE / name
        cur = dst.read_bytes() if dst.exists() else None
        if cur == out:
            continue
        stale.append(name)
        if not check:
            dst.write_bytes(out)
    if check:
        print('최신이 아님: ' + ', '.join(stale) if stale else '모두 최신')
        sys.exit(1 if stale else 0)
    print('다시 만든 장 %d개%s' % (len(stale), (': ' + ', '.join(stale)) if stale else ''))


if __name__ == '__main__':
    main()
