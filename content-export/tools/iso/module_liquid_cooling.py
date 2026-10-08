# 실행: python content-export/tools/iso/module_liquid_cooling.py assets/ess-module-liquid-cooling.svg
"""Module Liquid Cooling — 에어 쿨링과 같은 흰 젖빛 반투명 케이스 · 연한 파랑 셀.
셀 밑에 냉각판(청록)이 깔린다. 냉각수는 왼쪽에서 들어와(파랑) 판을 따라 흐르고, 셀의 열이 판으로 내려가며(빨강 ↓)
데워진 냉각수는 오른쪽 옆면 피팅으로 나간다(빨강). 2026-10-08 클라이언트 참고 자료(Coolant Inlet 왼쪽 · Outlet 오른쪽)대로."""
import sys
from iso import Iso, DEEP, BLUE, RED, ribbon3, plane

CASE = dict(top=('#ffffff', '#f4f7fd'), left=('#eef2fb', '#e1e7f5'), right=('#f5f8fe', '#e9eef8'))
CELL = dict(top=('#dbe7ff', '#cbdbff'), left=('#a4bbee', '#91abe4'), right=('#bacdf6', '#abc2f0'))
PLATE = dict(top=('#a6eef5', '#86e2ec'), left=('#22b4c7', '#1199ae'), right=('#4fcad8', '#35bccc'))   # 냉각판(킷 Custom 청록 계열)
METAL = dict(top=('#f1f3f7', '#dfe3ea'), left=('#a9b0bd', '#959dac'), right=('#c4cad4', '#b3bac6'))
BASE = dict(top=('#3a3e47', '#33373f'), left=('#16181d', '#121418'), right=('#1d2026', '#181a1f'))
EDGE, CE, SEAM = '#0c0d10', '#474c59', '#c3cbe0'
PLATE_EDGE = '#1d8a99'

g = Iso(40)


def fade(gid, a, b, color, o0, o1, s0=0, s1=1):
    (x1, y1), (x2, y2) = g.p(*a), g.p(*b)
    g.defs[gid] = (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}">'
                   f'<stop offset="{s0}" stop-color="{color}" stop-opacity="{o0}"/><stop offset="{s1}" stop-color="{color}" stop-opacity="{o1}"/></linearGradient>')
    return f'url(#{gid})'

L, D, H, T = 11.8, 8.0, 2.7, 0.28          # 오른쪽에 배관 자리(≈1)를 두려고 에어 쿨링보다 0.8 넓다
N, ct, cg = 8, 1.0, 0.26
rows = [(T + 0.3, 3.4), (T + 0.3 + 3.4 + 0.45, 3.4)]
ch, pz = 1.85, 0.6                          # 셀 높이 · 냉각판 두께
cx0 = T + 0.31
# 피팅 자리(오른쪽 면) — 들어옴(아래) · 나감(위)
FIT = dict(out=(1.0, 0.5))                # 옆면 오른쪽(뒤) 구석 냉각판 높이 피팅 하나 — 2026-10-08 사용자
INLET_Y = D - 0.6                          # 들어오는 쪽(왼쪽 끝) — 냉각판 높이

g.box(-0.25, -0.25, -0.22, L + 0.5, D + 0.5, 0.22, pal=BASE, out=EDGE, sw=2)
g.box(0, 0, 0, L, T, H, pal=CASE, out=CE, face_op=0.55)
g.box(0, T, 0, T, D - T, H, pal=CASE, out=CE, face_op=0.55)
# 냉각판 — 셀 밑을 다 덮는다
g.box(T, T, 0, L - 2 * T, D - 2 * T, pz, pal=PLATE, out=PLATE_EDGE, sw=1.6)
for (y0, dy) in rows:
    for i in range(N):
        x = cx0 + i * (ct + cg)
        g.box(x, y0, pz, ct, dy, ch, pal=CELL)
        for yy in (y0 + 0.45, y0 + dy - 1.0):
            g.box(x + 0.25, yy, pz + ch, 0.5, 0.55, 0.16, pal=DEEP, out=DEEP['out'], sw=1.2)

def pipe(pts3, color, sw=15):
    d = 'M' + ' L'.join('%.1f %.1f' % g.p(*q) for q in pts3)
    g.raw(f'<path d="{d}" stroke="#ffffff" stroke-width="{sw + 5}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
          f'<path d="{d}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>')


g.box(L - T, T, 0, T, D - 2 * T, H, pal=CASE, out=CE, face_op=0.55)
g.box(0, D - T, 0, L, T, H, pal=CASE, out=CE, face_op=0.55)


# 앞면 — 에어 쿨링과 같은 제품 앞판(그릴 · 커넥터 · 명판)
slots = ''.join(f'<rect x="{u:.2f}" y="{w:.2f}" width=".62" height=".15" rx=".075" fill="#4a5163" stroke="#9aa3bb" stroke-width=".02"/>'
                for w in (1.5, 1.8) for u in [0.9 + k * 0.8 for k in range(13)] if u < L - 0.9)
screws = ''.join(f'<circle cx="{u}" cy="{w}" r=".075" fill="#5d636e" stroke="#0c0d10" stroke-width=".02"/>'
                 for u in (0.22, L - 0.22, L / 2) for w in (0.22, H - 0.22))
front = (
    f'<rect x=".1" y=".1" width="{L - .2}" height="{H - .2}" fill="none" stroke="{SEAM}" stroke-width=".03"/>'
    + slots + screws
    + '<circle cx=".75" cy=".75" r=".3" fill="#3c414b" stroke="#0c0d10" stroke-width=".04"/><circle cx=".75" cy=".75" r=".16" fill="#16181c" stroke="#6a707b" stroke-width=".02"/>'
    + '<rect x="1.4" y=".28" width="1.3" height="1.12" rx=".07" fill="#101215" stroke="#5a606b" stroke-width=".045"/>'
    + '<rect x="1.66" y=".48" width=".78" height=".72" rx=".05" fill="#050607" stroke="#2a2d33" stroke-width=".03"/>'
    + '<rect x="1.86" y=".64" width=".38" height=".4" rx=".03" fill="#1d2025"/>'
    + ''.join(f'<circle cx="{u}" cy="{w}" r=".055" fill="#8a909b"/>' for u in (1.5, 2.6) for w in (.38, 1.3))
    + f'<rect x="{L / 2 - 1.3}" y=".42" width="2.6" height=".78" rx=".08" fill="#121418" stroke="#4d525c" stroke-width=".035"/>'
    + f'<text x="{L / 2}" y=".98" text-anchor="middle" font-family="SUIT, Pretendard, Arial, sans-serif" font-weight="800" font-size=".48" fill="#ffffff" letter-spacing=".02">A-PRO</text>'
    + f'<rect x="{L - 2.35}" y=".3" width="1.15" height="1.1" rx=".07" fill="#f07c2c" stroke="#a94f14" stroke-width=".045"/>'
    + f'<rect x="{L - 2.12}" y=".52" width=".69" height=".66" rx=".05" fill="#b8551a" stroke="#7d3a10" stroke-width=".03"/>'
    + f'<rect x="{L - 1.95}" y=".64" width=".35" height=".42" rx=".03" fill="#e4e7ee"/>'
    + ''.join(f'<circle cx="{u}" cy="{w}" r=".05" fill="#c8ccd4"/>' for u in (L - 2.25, L - 1.3) for w in (.4, 1.3))
)
plane(g, (0, D, H), 'x', front)
right = (f'<rect x=".1" y=".1" width="{D - .2}" height="{H - .2}" fill="none" stroke="{SEAM}" stroke-width=".03"/>'
         + ''.join(f'<circle cx="{u}" cy="{w}" r=".075" fill="#5d636e" stroke="#0c0d10" stroke-width=".02"/>' for u in (0.22, D - 0.22) for w in (0.22, H - 0.22)))
plane(g, (L, 0, H), 'y', right)

g.box(-0.04, -0.04, H, L + 0.08, D + 0.08, 0.16, pal=CASE, out=CE, face_op=0.3)

# 냉각판 속 물길 — 앞면 판 높이(x-ray). 들어온 냉각수가 판을 따라 흐르며 셀 열을 받아 데워진다
(px1, py1), (px2, py2) = g.p(0.9, D, pz / 2), g.p(L - 0.9, D, pz / 2)
g.defs['flow'] = (f'<linearGradient id="flow" gradientUnits="userSpaceOnUse" x1="{px1:.1f}" y1="{py1:.1f}" x2="{px2:.1f}" y2="{py2:.1f}">'
                  f'<stop offset=".72" stop-color="{BLUE}"/><stop offset="1" stop-color="{RED}"/></linearGradient>')
g.raw('<g opacity=".85">')
for k in range(9):
    x1 = 0.75 + k * 1.15
    ribbon3(g, (x1, D + 0.02, pz / 2), (x1 + 0.8, D + 0.02, pz / 2), (0, 0, 1), 0.08, 'url(#flow)', hl=0.32, hw2=2.2)
g.raw('</g>')
# 셀의 열이 냉각판으로 — 뒤 줄 셀을 지나 내려가는 빨강 화살표(x-ray)
g.raw('<g opacity=".9">')
XL = cx0 + (N - 1) * (ct + cg) + ct          # 오른쪽 끝 셀의 옆면
for j, y in enumerate((rows[0][0] + rows[0][1] / 2, rows[1][0] + rows[1][1] / 2)):
    a, b = (XL + 0.02, y, pz + ch + 0.9), (XL + 0.02, y, pz + 0.1)
    ribbon3(g, a, b, (0, 1, 0), 0.22, fade(f'heat{j}', a, b, RED, 0.15, 1, 0, .55), hl=0.42, hw2=2.2)
g.raw('</g>')
# 찬 냉각수 들어옴(Inlet) — 왼쪽 끝 냉각판 높이로, 모듈을 가리킨다
a, b = (-3.3, INLET_Y, pz / 2 - 0.1), (-0.15, INLET_Y, pz / 2 - 0.1)
ribbon3(g, a, b, (0, 0, 1), 0.26, fade('cin', a, b, BLUE, 0, 1, 0, .55), hl=0.85, hw2=2.1)





# 바깥 피팅(금속 너트 + 슬리브)과 냉각수 화살표 — 위(나감)를 먼저, 아래(들어옴)를 나중에
for k in ('out',):
    yy, zz = FIT[k]
    g.box(L, yy - 0.34, zz - 0.34, 0.32, 0.68, 0.68, pal=METAL, out=CE, sw=1.8)
    g.box(L + 0.32, yy - 0.24, zz - 0.24, 0.5, 0.48, 0.48, pal=METAL, out=CE, sw=1.6)
    if k == 'inn':     # 찬 냉각수가 들어온다 — 끝이 피팅을 가리킨다
        a, b = (L + 4.1, yy, zz), (L + 0.9, yy, zz)
        ribbon3(g, a, b, (0, 0, 1), 0.26, fade('cin', a, b, BLUE, 0, 1, 0, .55), hl=0.85, hw2=2.1)
    else:              # 데워진 냉각수가 나간다
        a, b = (L + 0.9, yy, zz), (L + 4.1, yy, zz)     # 데워진 냉각수 나감(Outlet) — 바깥으로
        ribbon3(g, a, b, (0, 0, 1), 0.26, fade('cout', a, b, RED, 1, 1), hl=0.85, hw2=2.1)

open(sys.argv[1], 'w', encoding='utf-8').write(g.svg(600, 12))
