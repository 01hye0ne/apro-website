# 실행: python content-export/tools/iso/rack_bms.py <종류> <출력.svg>
#   종류: rack-energy · rack-power · bms-module · bms-rack · bms-system
"""Rack · BMS — 냉각 그림들과 같은 GT Diagram Kit 말씨(30° 아이소 · 실루엣 외곽선 · 면 3단 그라데이션)로,
흐름 화살표가 없어 반투명 대신 실사 색을 불투명하게 쓴다(2026-10-08 사용자). 로고는 GNB 로고 path(iso.logo)."""
import sys
from iso import Iso, plane, logo

KIND = sys.argv[1]
g = Iso(40)
BLK = dict(top=('#3d424c', '#343842'), left=('#1f2228', '#191b20'), right=('#2a2d34', '#23262c'))
BLK2 = dict(top=('#30343c', '#2a2d34'), left=('#17191d', '#131518'), right=('#202328', '#1b1d22'))
WHT = dict(top=('#ffffff', '#f3f5f9'), left=('#e9ecf2', '#dde1e9'), right=('#f2f4f8', '#e6e9ef'))
SILV = dict(top=('#f1f3f7', '#dfe3ea'), left=('#a9b0bd', '#959dac'), right=('#c4cad4', '#b3bac6'))
ORG = dict(top=('#ff9a52', '#f5853a'), left=('#d8661f', '#c45a18'), right=('#ec7a2e', '#dc6c24'))
CON = dict(top=('#fafbfc', '#eef0f4'), left=('#d5d9e0', '#c8cdd6'), right=('#e4e7ec', '#d8dce3'))
PCB = dict(top=('#2f7a4c', '#286a42'), left=('#1d5a36', '#174b2d'), right=('#24683f', '#1e5a36'))
EDGE, CE = '#0c0d10', '#474c59'


def module_face(w, h, slim=False):
    """랙 안 배터리 모듈 앞면 — 양끝 손잡이 · 왼쪽 검정 커넥터 · 가운데 흰 로고 · 오른쪽 주황 커넥터"""
    s = f'<rect x="0" y="0" width="{w:.2f}" height="{h:.2f}" rx=".06" fill="#1b1d22" stroke="#4a4f59" stroke-width=".04"/>'
    if slim:   # High Power 맨 위 BMS 단
        s += f'<rect x=".35" y="{h * .25:.2f}" width=".35" height="{h * .5:.2f}" rx=".04" fill="#0b0c0f" stroke="#5a606b" stroke-width=".03"/>'
        s += f'<rect x="{w - .75:.2f}" y="{h * .22:.2f}" width=".38" height="{h * .56:.2f}" rx=".04" fill="#f07c2c"/>'
        s += f'<path d="M{w * .38:.2f} {h / 2:.2f} H{w * .62:.2f}" stroke="#7a808b" stroke-width=".05" stroke-dasharray=".12 .08"/>'
        return s
    for u in (0.12, w - 0.28):
        s += f'<rect x="{u:.2f}" y="{h * .18:.2f}" width=".16" height="{h * .64:.2f}" rx=".05" fill="#3a3f48"/>'
    s += f'<rect x=".55" y="{h * .2:.2f}" width="{h * .55:.2f}" height="{h * .6:.2f}" rx=".05" fill="#08090b" stroke="#5a606b" stroke-width=".035"/>'
    s += f'<rect x="{.55 + h * .14:.2f}" y="{h * .34:.2f}" width="{h * .27:.2f}" height="{h * .32:.2f}" rx=".03" fill="#22252b"/>'
    lw = min(w * .26, 1.5)
    s += logo(w / 2 - lw / 2, h / 2 - lw * 17 / 78 / 2, lw, '#ffffff')
    s += f'<rect x="{w - .55 - h * .55:.2f}" y="{h * .18:.2f}" width="{h * .55:.2f}" height="{h * .64:.2f}" rx=".06" fill="#f07c2c" stroke="#a94f14" stroke-width=".035"/>'
    s += f'<rect x="{w - .55 - h * .42:.2f}" y="{h * .32:.2f}" width="{h * .29:.2f}" height="{h * .36:.2f}" rx=".03" fill="#b8551a"/>'
    return s


def rack(power):
    W, Dp, H = 5.6, 5.2, 10.6
    zb = 0.75                                               # 다리 · 받침 높이
    for (x, y) in ((0.35, 0.35), (W - 0.85, 0.35), (W - 0.85, Dp - 0.85), (0.35, Dp - 0.85)):
        g.box(x, y, 0, 0.5, 0.5, zb - 0.25, pal=BLK2, out=EDGE, sw=1.6)     # 수평 다리
    g.box(0, 0, zb - 0.25, W, Dp, 0.25, pal=BLK2, out=EDGE, sw=1.8)        # 받침
    g.box(0, 0, zb, W, Dp, H, pal=BLK, out=EDGE)                           # 캐비닛
    # 앞면 — 테 · 안쪽 어둠 · 모듈 단
    fr = 0.32
    face = f'<rect x="{fr:.2f}" y="{fr:.2f}" width="{W - 2 * fr:.2f}" height="{H - 2 * fr - .4:.2f}" fill="#07080a"/>'
    face += ''.join(f'<circle cx="{u:.2f}" cy="{w:.2f}" r=".06" fill="#5d636e"/>' for u in (0.16, W - 0.16) for w in (0.3, H / 2, H - 0.5))
    inner_w = W - 2 * fr - 0.3
    rows = ([('slim', 0.55)] if power else []) + [('m', 1.12 if power else 1.28)] * 7
    w = fr + 0.2
    for kind, hh in rows:
        face += f'<g transform="translate({fr + .15:.2f} {w:.2f})">{module_face(inner_w, hh, kind == "slim")}</g>'
        w += hh + 0.1
    face += f'<rect x="0" y="{H - .45:.2f}" width="{W}" height=".45" fill="#15171b"/>'
    plane(g, (0, Dp, zb + H), 'x', face, flipw=W)
    # 옆면 — 손잡이 홈 · 나사
    side = f'<rect x="{Dp - 1.2:.2f}" y="1.6" width=".22" height=".9" rx=".1" fill="#0b0c0f"/>'
    side += ''.join(f'<circle cx="{u:.2f}" cy="{w:.2f}" r=".06" fill="#4d535e"/>' for u in (0.3, Dp - 0.3) for w in (0.3, H - 0.3))
    plane(g, (W, 0, zb + H), 'y', side)
    # 열린 문 — 왼쪽 경첩에서 90° 열려 앞으로 나온다. 안쪽(타공판)이 보인다
    dw = W - 0.2
    g.box(-0.18, Dp, zb + 0.15, 0.18, dw, H - 0.3, pal=BLK, out=EDGE)
    perf = f'<rect x=".35" y=".5" width="{dw - .7:.2f}" height="{H - 1.3:.2f}" rx=".05" fill="#191b20" stroke="#3a3e47" stroke-width=".04"/>'
    for band in (0, 1, 2, 4, 5, 6):                      # 타공 띠(가운데는 막힘)
        w0 = 0.75 + band * (H - 1.8) / 7
        for r in range(4):
            for c in range(int((dw - 1.0) / 0.22)):
                perf += f'<circle cx="{0.55 + c * 0.22:.2f}" cy="{w0 + r * 0.22:.2f}" r=".055" fill="#55606e"/>'
    perf += f'<rect x="{dw - .35:.2f}" y="{H / 2 - .5:.2f}" width=".14" height="1.0" rx=".05" fill="#5d636e"/>'
    plane(g, (0.0, Dp, zb + H - 0.15), 'y', perf)
    for wz in (1.2, H / 2, H - 1.4):                     # 경첩
        g.box(-0.05, Dp - 0.12, zb + wz, 0.12, 0.24, 0.5, pal=BLK2, out=EDGE, sw=1.2)


def bms_module():
    Lx, T, Hh = 10.0, 0.3, 5.0
    g.box(0, 0, 0, 0.55, 1.0, Hh + 0.4, pal=BLK, out=EDGE)                # 왼쪽 브래킷
    g.box(0.55, 0.45, 0.2, Lx - 1.1, T, Hh, pal=PCB, out='#123a24')        # 기판
    # 위아래 흰 커넥터(기판 앞으로 튀어나옴)
    for u in (1.2, 2.3, 3.4, 4.5, 6.4, 7.6, 8.4):
        g.box(u, 0.45 + T, 0.2 + Hh - 0.6, 0.6, 0.28, 0.45, pal=CON, out=CE, sw=1.1)
    for u in (1.4, 2.5, 3.6, 4.7, 6.2, 7.6, 8.4):
        g.box(u, 0.45 + T, 0.35, 0.6, 0.28, 0.45, pal=CON, out=CE, sw=1.1)
    board = ''
    for (u, w, bw, bh) in [(1.6, 1.3, .55, .5), (2.7, 1.3, .55, .5), (3.8, 1.3, .55, .5), (5.0, 1.3, .55, .5), (6.6, 1.25, .5, .45), (7.6, 1.1, .6, .65),
                           (1.6, 3.3, .55, .5), (2.7, 3.3, .55, .5), (3.8, 3.3, .55, .5), (5.0, 3.3, .55, .5), (6.7, 3.3, .5, .45), (7.7, 3.3, .5, .45),
                           (5.2, 2.15, .7, .7), (6.4, 2.25, .5, .5), (7.3, 2.15, .6, .6)]:
        board += f'<rect x="{u - .55:.2f}" y="{w:.2f}" width="{bw}" height="{bh}" rx=".03" fill="#15171b"/>'
        board += ''.join(f'<path d="M{u - .55 + k * bw / 4 + .07:.2f} {w + bh:.2f} V{w + bh + .18:.2f}" stroke="#c9cdd4" stroke-width=".03"/>' for k in range(4))
    board += ''.join(f'<path d="M{.4 + k * .65:.2f} 2.0 H{.4 + k * .65 + .4:.2f} V2.9" stroke="#3f9a62" stroke-width=".03" fill="none"/>' for k in range(13))
    board += logo(1.15, 2.2, 2.0, '#ffffff')
    board += '<rect x=".2" y="2.05" width=".7" height=".75" rx=".06" fill="#101215"/>'
    plane(g, (0.55, 0.45 + T, 0.2 + Hh), 'x', board, flipw=Lx - 1.1)
    g.box(Lx - 0.55, 0, 0, 0.55, 1.0, Hh + 0.4, pal=BLK, out=EDGE)         # 오른쪽 브래킷
    br = ''.join(f'<rect x=".14" y="{w:.2f}" width=".27" height=".4" rx=".08" fill="#e9ecf2"/>' for w in (1.3, Hh - 1.3))
    plane(g, (0, 1.0, Hh + 0.4), 'x', br)


def bms_rack():
    Lx, Dp, Hh = 11.0, 6.5, 2.6
    g.box(0.35, 0, 0, Lx - 0.7, Dp, Hh, pal=BLK, out=EDGE)                 # 섀시
    for x in (0, Lx - 0.35):                                               # 랙 귀
        g.box(x, Dp - 0.12, 0, 0.35, 0.12, Hh, pal=BLK2, out=EDGE, sw=1.4)
    face = f'<rect x=".25" y=".22" width="{Lx - 1.2:.2f}" height="{Hh - .44:.2f}" fill="none" stroke="#3a3e47" stroke-width=".035"/>'
    face += ''.join(f'<circle cx="{u:.2f}" cy="{w:.2f}" r=".05" fill="#5d636e"/>' for u in (.2, Lx - .9, (Lx - .7) / 2) for w in (.12, Hh - .12))
    for k, col in enumerate(('#ef4b3c', '#ef4b3c', '#2fbf5a', '#2fbf5a')):   # 왼쪽 LED
        face += f'<circle cx="2.05" cy="{.55 + k * .42:.2f}" r=".07" fill="{col}"/><circle cx="2.3" cy="{.55 + k * .42:.2f}" r=".035" fill="#6a707b"/>'
    for k, col in enumerate(('#f2b134', '#f2b134', '#2fbf5a', '#2fbf5a')):   # 오른쪽 LED
        face += f'<circle cx="{Lx - 3.1:.2f}" cy="{.55 + k * .42:.2f}" r=".07" fill="{col}"/><circle cx="{Lx - 3.35:.2f}" cy="{.55 + k * .42:.2f}" r=".035" fill="#6a707b"/>'
    face += '<rect x=".55" y=".75" width=".9" height=".12" fill="#8a909b"/><rect x=".55" y="1.05" width=".55" height=".08" fill="#5d636e"/>'
    for w in (.35, 1.35):                                                   # 커넥터 둘
        face += f'<rect x="{Lx - 2.45:.2f}" y="{w:.2f}" width=".9" height=".9" rx=".06" fill="#0b0c0f" stroke="#5a606b" stroke-width=".04"/>'
        face += f'<circle cx="{Lx - 2.0:.2f}" cy="{w + .45:.2f}" r=".28" fill="#16181c" stroke="#6a707b" stroke-width=".04"/>'
    lw = 1.9
    face += logo((Lx - .7) / 2 - lw / 2, 0.45, lw, '#ffffff')
    face += f'<rect x="{(Lx - .7) / 2 - .62:.2f}" y="1.15" width="1.24" height=".6" rx=".12" fill="#121418" stroke="#4d525c" stroke-width=".03"/>'
    face += f'<text x="{(Lx - .7) / 2:.2f}" y="1.6" text-anchor="middle" font-family="SUIT, Pretendard, Arial, sans-serif" font-weight="700" font-size=".42" fill="#ffffff">BPU</text>'
    plane(g, (0.35, Dp, Hh), 'x', face, flipw=Lx - 0.7)
    for x in (0.05, Lx - 0.3):                                              # 은색 손잡이
        g.box(x, Dp, 0.45, 0.25, 0.42, 0.12, pal=SILV, out=CE, sw=1.2)
        g.box(x, Dp, Hh - 0.57, 0.25, 0.42, 0.12, pal=SILV, out=CE, sw=1.2)
        g.box(x, Dp + 0.3, 0.45, 0.25, 0.12, Hh - 0.9, pal=SILV, out=CE, sw=1.2)


def bms_system():
    Lx, Dp, Hh = 9.6, 3.6, 9.4
    g.box(0, 0, 0, Lx, Dp, 0.55, pal=BLK2, out=EDGE, sw=1.8)               # 검정 받침
    g.box(0, 0, 0.55, Lx, Dp, Hh, pal=WHT, out=CE)                          # 제어반
    dw = Lx / 3
    face = ''.join(f'<path d="M{dw * k:.2f} .1 V{Hh - .1:.2f}" stroke="#b9c0cc" stroke-width=".05"/>' for k in (1, 2))
    face += ''.join(f'<rect x="{dw * k + .12:.2f}" y=".15" width="{dw - .24:.2f}" height="{Hh - .3:.2f}" fill="none" stroke="#d3d8e1" stroke-width=".04"/>' for k in range(3))
    for k in range(3):                                                      # 손잡이
        face += f'<rect x="{dw * k + .3:.2f}" y="{Hh * .52:.2f}" width=".16" height=".6" rx=".05" fill="#9aa2b3" stroke="#6c7489" stroke-width=".03"/>'
    lw = 2.2
    face += logo(dw / 2 - lw / 2 + .1, 1.1, lw, '#1f3f8f')
    face += f'<path d="M{dw / 2 - 1.0:.2f} 1.85 H{dw / 2 + 1.2:.2f}" stroke="#1f3f8f" stroke-width=".04"/>'
    face += f'<text x="{dw / 2 + .1:.2f}" y="2.5" text-anchor="middle" font-family="SUIT, Pretendard, Arial, sans-serif" font-weight="800" font-size=".55" fill="#1f3f8f">BCP</text>'
    face += f'<rect x="{dw / 2 - .55:.2f}" y="3.1" width="1.1" height="1.35" rx=".06" fill="#e9ecf2" stroke="#7d869a" stroke-width=".05"/>'
    face += f'<rect x="{dw / 2 - .42:.2f}" y="3.22" width=".84" height=".8" fill="#cfe2f5" stroke="#8aa0b8" stroke-width=".03"/>'
    face += ''.join(f'<circle cx="{dw / 2 - .25 + k * .25:.2f}" cy="4.22" r=".06" fill="{c}"/>' for k, c in enumerate(('#ef4b3c', '#2a2e36', '#2fbf5a')))
    face += f'<circle cx="{dw / 2 - .3:.2f}" cy="5.0" r=".14" fill="#2a2e36"/><circle cx="{dw / 2 + .3:.2f}" cy="5.0" r=".14" fill="#ef4b3c"/>'
    face += f'<path d="M{dw / 2:.2f} 5.45 L{dw / 2 + .17:.2f} 5.75 L{dw / 2:.2f} 6.05 L{dw / 2 - .17:.2f} 5.75 Z" fill="#2a2e36"/>'

    def louver(u, w, bw, bh, n):
        s = f'<rect x="{u:.2f}" y="{w:.2f}" width="{bw}" height="{bh}" fill="#f4f6fa" stroke="#9aa2b3" stroke-width=".05"/>'
        s += ''.join(f'<path d="M{u + .08:.2f} {w + .12 + k * (bh - .24) / (n - 1):.2f} H{u + bw - .08:.2f}" stroke="#7d869a" stroke-width=".05"/>' for k in range(n))
        return s
    face += louver(dw * 2 - 1.15, 1.6, 0.8, 1.3, 9) + louver(dw * 2 - 1.15, 3.0, 0.8, 1.3, 9)
    face += louver(dw * 2 + .9, 1.85, 1.2, 5.6, 34)
    plane(g, (0, Dp, Hh + 0.55), 'x', face, flipw=Lx)
    side = f'<rect x=".25" y=".2" width="{Dp - .5:.2f}" height="{Hh - .4:.2f}" fill="none" stroke="#d3d8e1" stroke-width=".04"/>'
    plane(g, (Lx, 0, Hh + 0.55), 'y', side)


{'rack-energy': lambda: rack(False), 'rack-power': lambda: rack(True), 'bms-module': bms_module,
 'bms-rack': bms_rack, 'bms-system': bms_system}[KIND]()
open(sys.argv[2], 'w', encoding='utf-8').write(g.svg(600, 24))
