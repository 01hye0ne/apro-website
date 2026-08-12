#!/usr/bin/env python3
"""사업영역 세부 페이지 A-1 버전 생성기

    python _gen-a1.py          # business-*-a1.html 4개를 다시 만든다
    python _gen-a1.py --check   # 다시 만들지 않고, 지금 파일이 최신인지만 알려준다

business-*.html(A)이 원본이고 business-*-a1.html(A-1)은 전부 여기서 나온다.
A 파일을 고친 뒤 이 스크립트를 돌리면 A-1 에 그대로 반영된다 — A-1 파일을 직접
고치면 다음 실행 때 덮어써지니, 수정은 항상 A 파일에서 한다.

2026-08-12 부터 두 갈래는 디자인이 완전히 같다 — 그때까지 남아 있던 차이(A-1 의
카드 묶음 상자와 하단 플로팅 알약 탭 바)를 A 쪽으로 통일했고, 갈래를 만들던
.v-a1 규칙도 business-layout.css 와 각 페이지 <style> 에서 걷어냈다.
그래서 이 스크립트가 하는 일은 아래 두 가지 기계적인 치환뿐이다.

  1. <title>…</title>  → …(A-1) 붙임               브라우저 탭에서 두 갈래 구분
  2. 페이지 링크        → -a1 끼리 잇기              A-1 안에서 돌아다니면 A-1 만 나온다

CSS 분기 스위치(<body class="v-a1">)는 A1_BODY 에 적힌 페이지에만 붙인다. 지금은
회사소개 한 곳뿐이고 그마저 아직 쓰는 규칙이 없다 — 나중에 그 페이지를 다른
레이아웃으로 나눌 때 바로 쓰라고 자리만 잡아 둔 것이다. 세부 페이지에 다시 붙이면
안 된다 : 페이지 <style> 에 body:not(.v-a1) 로 시작하는 상단 고정 바 규칙이
그대로 남아 있어(특정도를 건드리지 않으려고 접두사만 두었다) 붙이는 순간 A-1 만
그 규칙을 잃는다.

CSS·JS 는 A/A-1 이 한 벌(business-layout.css / .js)을 그대로 함께 쓴다. 고칠 게
레이아웃·동작이면 그 두 파일만 고치면 되고 이 스크립트를 돌릴 필요도 없다.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent

# A-1 짝이 있는 페이지. 이 이름들의 링크를 A-1 안에서 -a1 로 바꿔 준다.
# 페이지 이름이 바뀌면 이 목록만 고치면 된다.
PAGES = ['business-smart', 'business-energy', 'business-ai', 'business-semicon',
         'business', 'company', 'network', 'index']

# 실제로 A-1 을 생성할 페이지
#
# index.html(홈)도 여기 들어와 있다 — 한동안은 A/A-1 을 손으로 따로 관리했다(히어로 밑단
# 탭 띠와 Business 장이 갈래마다 달랐다). 지금은 홈 디자인을 하나로 합쳤으므로(히어로는
# A-1 의 유리 탭 띠, 나머지는 A 의 정적 4타일) 두 갈래가 링크와 타이틀만 다르다 →
# 다른 페이지와 똑같이 이 스크립트가 낸다. 홈을 고칠 때도 index.html 만 고치면 된다.
#
# business.html(사업영역 허브)도 A-1 이 필요하다 — 디자인은 A/A-1 이 같지만, 이 페이지가
# 세부 페이지 4개와 홈을 하드링크하는데 모든 페이지의 GNB "사업영역"이 여기로 들어온다.
# 한 벌만 두면 A-1 에서 GNB 를 누른 순간 세부 A 로 새어 버린다.
# 이 페이지는 <style> 을 자체적으로 갖고 있어 세부 페이지와 CSS 를 공유하지 않는다 →
# 스타일을 고칠 때도 business.html 을 고치고 이 스크립트를 돌리면 된다.
#
# company.html(회사소개)도 같은 이유로 들어와 있다 — 모든 페이지의 GNB "회사소개"와
# 메가메뉴·전체메뉴의 "에이프로 소개"가 여기로 모이고, 이 페이지도 세부 페이지 4개와
# 홈을 되짚어 링크한다. 한 벌만 두면 A-1 에서 회사소개를 한 번 누르는 순간 그 뒤로는
# 전부 A 갈래가 된다. 디자인은 A/A-1 이 같고 링크만 갈라진다는 점도 business.html 과 같다.
#
# network.html(글로벌 네트워크)도 마찬가지다 — 홈에 있던 Global Network 장이 페이지로
# 나온 것이고, 회사 정보 메뉴·푸터·전체메뉴가 모두 여기로 모인다. 디자인은 A/A-1 이
# 같고 링크만 갈라진다.
SOURCES = ['business-smart.html', 'business-energy.html',
           'business-ai.html', 'business-semicon.html',
           'business.html', 'company.html', 'network.html', 'index.html']

# body 에 CSS 분기 스위치(class="v-a1")를 달 페이지.
#
# 회사소개만 들어 있다 — 이 페이지를 나중에 A/A-1 다른 레이아웃으로 나눌 예정이라
# 스위치 자리를 미리 잡아 둔 것이고, 지금은 그 클래스를 보는 규칙이 한 줄도 없어
# 붙어 있어도 화면은 A 와 똑같다. 갈래를 만들 때 company.html <style> 에
# .v-a1 규칙을 더하면 그때부터 갈라진다.
#
# ⚠ 세부 페이지(business-*)를 여기 넣으면 안 된다 — 그 페이지 <style> 에는
#   body:not(.v-a1) 로 시작하는 상단 고정 바 규칙이 남아 있어서(특정도를 지키려고
#   접두사만 둔 것) 클래스를 붙이는 순간 A-1 만 그 규칙을 통째로 잃는다.
A1_BODY = {'company.html'}


def build(src_text, want_body=False):
    """A 페이지 HTML 문자열 → A-1 페이지 HTML 문자열

    치환 대상(<body>, <title>, href)은 모두 한 줄 안에서 끝나므로 문자열에 CRLF 가
    섞여 있어도 그대로 통과한다 — 원본의 줄바꿈을 건드리지 않는 것이 중요하다.
    (bytes 로 읽고 쓰는 이유: 파일마다 줄바꿈이 달라서, 텍스트 모드로 오가면
     A-1 파일 전체가 바뀐 것으로 보여 diff 가 쓸모없어진다)
    """
    out, n_body = src_text, 0
    if want_body:
        out, n_body = re.subn(r'<body>', '<body class="v-a1">', out, count=1)
    out, n_title = re.subn(r'(<title>[^<]*)</title>',
                           lambda m: m.group(1) + ' (A-1)</title>', out, count=1)
    n_link = 0
    for page in PAGES:
        out, k = re.subn(r'href="%s\.html"' % re.escape(page),
                         'href="%s-a1.html"' % page, out)
        n_link += k
    return out, (n_body, n_title, n_link)


def main():
    check = '--check' in sys.argv
    stale = []

    for name in SOURCES:
        src = HERE / name
        dst = HERE / name.replace('.html', '-a1.html')
        if not src.exists():
            print('  !! 원본 없음: %s' % name)
            continue

        want_body = name in A1_BODY
        text, (n_body, n_title, n_link) = build(src.read_bytes().decode('utf-8'), want_body)

        # 원본에 <body> 나 <title> 이 없으면 조용히 잘못된 파일을 뱉는 게 최악이다
        if not n_title or (want_body and not n_body):
            print('  !! %s : body=%d title=%d — 마크업이 예상과 다르다' % (name, n_body, n_title))
            continue

        blob = text.encode('utf-8')
        same = dst.exists() and dst.read_bytes() == blob
        if check:
            if not same:
                stale.append(dst.name)
            print('  %-26s %s' % (dst.name, '최신' if same else '★ 오래됨 (다시 만들어야 함)'))
        else:
            dst.write_bytes(blob)
            print('  %-26s %s  (링크 %d곳)'
                  % (dst.name, '변화 없음' if same else '갱신', n_link))

    if check and stale:
        print('\n오래된 파일 %d개 — python _gen-a1.py 로 다시 만드세요' % len(stale))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
