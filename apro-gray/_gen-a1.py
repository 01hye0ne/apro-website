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

CSS 분기 스위치(<body class="v-a1">)는 A1_BODY 에 적힌 페이지에만 붙인다. 2026-09-10
부터 그 집합은 비어 있다 — 마지막 한 곳이던 회사소개를 A 로 되돌렸기 때문이다.
세부 페이지를 여기 넣으면 안 된다 : 페이지 <style> 에 body:not(.v-a1) 로 시작하는
상단 고정 바 규칙이 그대로 남아 있어(특정도를 건드리지 않으려고 접두사만 두었다)
붙이는 순간 A-1 만 그 규칙을 잃는다.

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
         'business', 'company', 'network', 'locations', 'index',
         # 투자정보 · 지속가능경영 · 커뮤니티 (content-layout.css 를 함께 쓰는 콘텐츠 페이지)
         'ir-finance', 'ir-disclosure', 'ir-stock', 'ir-policy',
         'esg-environment', 'esg-social', 'esg-governance', 'esg-report', 'esg-board',
         'community-notice', 'community-press']

# 실제로 A-1 을 생성할 페이지
#
# ⚠ index.html(홈)은 2026-09-14 부터 여기 없다 — A-1 홈을 Figma 991:15 와이어프레임
#   (배너 네 장 탭 · Business 카드 캐러셀 · Who we are · News 세 건)으로 새로 짰기
#   때문이다. 한동안 두 갈래가 링크와 타이틀만 달라 이 스크립트가 냈지만, 이제
#   index-a1.html 은 손으로 고치는 파일이고 A 를 고쳐도 A-1 로 넘어가지 않는다.
#   GNB · 메가 판 · 전체메뉴 · 푸터는 index.html 의 것을 그대로 옮겨 왔으므로 그
#   껍데기를 고칠 일이 생기면 두 장을 함께 고친다.
#   PAGES 에는 'index' 를 남겨 둔다: 다른 A-1 페이지의 로고·홈 링크가
#   index-a1.html 로 이어져야 하기 때문이다.
#
# business.html(사업영역 허브)도 A-1 이 필요하다 — 디자인은 A/A-1 이 같지만, 이 페이지가
# 세부 페이지 4개와 홈을 하드링크하는데 모든 페이지의 GNB "사업영역"이 여기로 들어온다.
# 한 벌만 두면 A-1 에서 GNB 를 누른 순간 세부 A 로 새어 버린다.
# 이 페이지는 <style> 을 자체적으로 갖고 있어 세부 페이지와 CSS 를 공유하지 않는다 →
# 스타일을 고칠 때도 business.html 을 고치고 이 스크립트를 돌리면 된다.
#
# ⚠ company.html(회사소개)도 2026-09-14 부터 여기 없다 — A-1 회사소개를 Figma 995:324
#   와이어프레임(노을 사옥 히어로 · Vision 2030 제목 · AAA 세 장 · A-PRO 문구)으로 새로
#   짰기 때문이다. company-a1.html 은 이제 손으로 고치는 파일이고, 머리 · 푸터 · 전체메뉴는
#   index-a1.html 과 같은 벌이다. PAGES 에는 'company' 를 남겨 둔다(다른 A-1 페이지의
#   회사소개 링크가 company-a1.html 로 와야 한다). 아래 단락은 그 전의 사정이다.
# company.html(회사소개)도 같은 이유로 들어와 있었다 — 모든 페이지의 GNB "회사소개"와
# 메가메뉴·전체메뉴의 "에이프로 소개"가 여기로 모이고, 이 페이지도 세부 페이지 4개와
# 홈을 되짚어 링크한다. 한 벌만 두면 A-1 에서 회사소개를 한 번 누르는 순간 그 뒤로는
# 전부 A 갈래가 된다. 디자인은 A/A-1 이 같고 링크만 갈라진다는 점도 business.html 과 같다.
#
# network.html(글로벌 네트워크)도 마찬가지다 — 홈에 있던 Global Network 장이 페이지로
# 나온 것이고, 회사 정보 메뉴·푸터·전체메뉴가 모두 여기로 모인다. 디자인은 A/A-1 이
# 같고 링크만 갈라진다.
#
# 2026-08-20 부터 나흘간 투자정보·지속가능경영·커뮤니티는 A 와 A-1 의 내용이 달랐다.
# A 는 기존 사이트(aproele.com)에서 옮겨 온 글, A-1 은 리뉴얼 프로젝트 DB 추출본
# (content-export)에서 옮겨 온 글이었고, 두 벌을 나란히 놓고 보려고 그 아홉 장을
# 이 SOURCES 에서 빼 두었다. 2026-08-24 그 비교가 끝나 A 쪽으로 합쳤다 —
# 이제 열여덟 장 모두 A 에서 나오고, A-1 은 타이틀과 링크만 다르다.
# A-1 쪽에만 있던 content-export 판 글은 이 커밋 직전 이력에 그대로 남아 있다.
#
# ⚠ business-smart.html 은 2026-09-09 부터 여기 없다 — 스마트 제조만 A / A-1 의
#   디자인이 갈라졌기 때문이다(A-1 = Figma 993:130 와이어프레임: GNB·탭 바·카드
#   캐러셀을 걷어내고 히어로+인트로+세로 인덱스 열한 장으로 새로 짰다. 마을과
#   푸터만 A 와 같다). 그래서 business-smart-a1.html 은 손으로 고치는 파일이고,
#   A 를 고쳐도 A-1 로 넘어가지 않는다 — 두 장을 따로 손봐야 한다.
#   PAGES 에는 그대로 남겨 둔다: 다른 A-1 페이지의 "스마트 제조" 링크가
#   business-smart-a1.html 로 이어져야 하기 때문이다(빼면 A 로 샌다).
#
# ⚠ business-ai.html 도 2026-09-09 부터 여기 없다 — 같은 이유다. 인공지능 플랫폼
#   A-1 을 스마트 제조 A-1 과 같은 레이아웃(Figma 994:321 와이어프레임)으로 새로
#   짰기 때문에 A 와 갈라졌다. business-ai-a1.html 도 손으로 고치는 파일이고,
#   PAGES 에는 남겨 두어 다른 A-1 페이지의 "인공지능 플랫폼" 링크가 그대로 온다.
#
# ⚠ business-semicon.html 도 2026-09-09 부터 여기 없다 — 역시 같은 이유다
#   (Figma 994:544 와이어프레임). 이제 A-1 을 손으로 고치는 페이지는 스마트 제조 ·
#   인공지능 플랫폼 · 화합물 전력 반도체 셋이고, 세 파일이 <style>·<script> 를
#   각자 갖고 있다(공용 파일로 뽑지 않았다) → 골격을 고칠 일이 생기면 셋을 함께
#   고쳐야 한다.
#
# ⚠ business-energy.html 도 2026-09-09 부터 여기 없다 — 마지막 하나였다
#   (Figma 994:141 와이어프레임). 이제 세부 페이지 넷이 모두 손으로 고치는 A-1 이고,
#   생성기가 만드는 건 허브(business)와 콘텐츠 페이지뿐이다(홈 · 회사소개는 2026-09-14 에 빠졌다 — 위 참고).
#   에너지 인프라 A-1 은 본문 골격까지 형제 셋과 다르다 — 붙박이가 [좌측 인덱스 +
#   가운데 헤더] 둘이고 나머지가 통째로 흐른다.
# ⚠ network.html(글로벌 네트워크)도 2026-09-14 부터 여기 없다 — A-1 을 회사정보 세 페이지 공용 틀
#   (Figma 1227:7859, 흰 히어로 + 파랑 지도 띠)로 짰다. network-a1.html 은 손으로 고치는 파일이고
#   A 는 옛 전면 무대 그대로다. PAGES 에는 'network' 를 남겨 둔다(다른 A-1 의 링크가 network-a1.html 로 와야 한다).
# ⚠ 투자정보 네 장(ir-finance · ir-disclosure · ir-stock · ir-policy)도 2026-09-15 부터 여기 없다 —
#   A-1 을 왼쪽 세로 히어로 틀(ir-layout.css, Figma 1248:13870 · 1248:13902)로 짰다. -a1 네 장은
#   손으로 고치는 파일이고 A 는 옛 배너 히어로 그대로다. PAGES 에는 남겨 둔다(다른 A-1 의 링크가 -a1 로 와야 한다).
# ⚠ 지속가능경영 다섯 장 · 커뮤니티 두 장도 같은 날(2026-09-15) 여기서 뺐다 — 투자정보와 같은 세로 히어로 틀
#   (content-side.css)로 짰다. 투자정보 틀 CSS 이름도 그때 ir-layout.css → content-side.css 로 바뀌었다.
#   이제 이 스크립트가 만드는 A-1 은 사업영역 허브(business) 하나뿐이다. PAGES 는 그대로 둔다.
SOURCES = ['business.html']

# body 에 CSS 분기 스위치(class="v-a1")를 달 페이지.
#
# 2026-09-10 부터 비어 있다. 오랫동안 회사소개 하나가 들어 있었고, 그 스위치를 보는
# 규칙이 company.html 의 <style> 과 <script> 에 157곳 자라 있었다(A-1 만의 사옥 사진 ·
# 숫자 판 배치 · Vision 랜드스케이프 모핑). 회사소개도 A 와 같게 가기로 해서 스위치를
# 내린다 — 클래스가 없으면 그 규칙은 한 줄도 걸리지 않으므로 A-1 은 A 와 완전히 같은
# 화면이 된다. 규칙 자체는 페이지에 그대로 두었다(전부 body.v-a1 / body:not(.v-a1) 로
# 갇혀 있어 A 에 새지 않는다) : 다시 갈래를 낼 일이 생기면 이 집합에 company.html 을
# 되돌려 넣는 것만으로 예전 A-1 이 그대로 살아난다.
#
# ⚠ 세부 페이지(business-*)를 여기 넣으면 안 된다 — 그 페이지 <style> 에는
#   body:not(.v-a1) 로 시작하는 상단 고정 바 규칙이 남아 있어서(특정도를 지키려고
#   접두사만 둔 것) 클래스를 붙이는 순간 A-1 만 그 규칙을 통째로 잃는다.
A1_BODY = set()


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
    # 앵커가 붙은 링크(href="business-smart.html#sf01-1")도 함께 바꾼다 — 예전엔 딱 맞는
    # href="page.html" 만 바꿔서, 메가 판 소분류가 A 판으로 새고 A 판엔 그 앵커가 없어 맨 위에 떨어졌다
    for page in PAGES:
        out, k = re.subn(r'href="%s\.html(#[^"]*)?"' % re.escape(page),
                         lambda m, p=page: 'href="%s-a1.html%s"' % (p, m.group(1) or ''), out)
        n_link += k
    # 2026-09-20 까지는 사업장소재가 A-1 에만 있어서(locations-a1.html) A 원본의 빈 링크(href="#")를
    # A-1 에서만 그 페이지로 이어 주었다. 이제 A 에도 locations.html 이 있어 위 PAGES 루프가
    # locations.html → locations-a1.html 로 바꾼다. 아래 줄은 혹시 남아 있는 빈 링크를 위한 보루다
    out, k = re.subn(r'href="#">사업장소재', 'href="locations-a1.html">사업장소재', out)
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
