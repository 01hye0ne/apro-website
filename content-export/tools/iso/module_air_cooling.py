# 실행: python content-export/tools/iso/module_air_cooling.py assets/ess-module-air-cooling.svg
"""Module Air Cooling v2 — 실제 제품(검정 케이스 · 앞면 그릴 · 커넥터 · A-PRO 명판)처럼.
위를 걷어 낸 단면이라 안의 회백색 셀이 보인다. 찬 공기는 앞 그릴로 들어가고(파랑) 더운 공기는 위로 빠진다(빨강)."""
import sys, os
VAR = os.environ.get('LID', 'white')     # 'white' 흰 젖빛 반투명 케이스(2026-10-08 확정) · '' 열린 검정 단면 · 'lid' 검정 반투명 뚜껑 · 'all' 검정 뚜껑+벽 반투명
from iso import Iso, LIGHT, DEEP, BLUE, RED, ribbon3, plane

BLK = dict(top=('#454a55', '#3a3e48'), left=('#24272e', '#1c1f25'), right=('#2e3139', '#25282f'))
BLK_IN = dict(top=('#454a55', '#3a3e48'), left=('#3a3e48', '#31353e'), right=('#363a43', '#2d3139'))
FLOOR_IN = dict(top=('#2a2d34', '#25282e'), left=('#1c1f25', '#1c1f25'), right=('#22252b', '#22252b'))
BASE = dict(top=('#3a3e47', '#33373f'), left=('#16181d', '#121418'), right=('#1d2026', '#181a1f'))
EDGE = '#0c0d10'
WHITE = VAR == 'white'                     # 흰 젖빛 반투명 케이스(뚜껑 · 벽 모두)
if WHITE:
    BLK = dict(top=('#ffffff', '#f4f7fd'), left=('#eef2fb', '#e1e7f5'), right=('#f5f8fe', '#e9eef8'))
    BLK_IN = BLK
    FLOOR_IN = dict(top=('#e6ebf6', '#dde3f1'), left=('#cfd6e8', '#cfd6e8'), right=('#d8deee', '#d8deee'))
CASE_EDGE = '#474c59' if WHITE else EDGE
# 셀 — 흰 케이스와 갈리게 아주 연한 파랑(2026-10-08 사용자)
CELL = dict(top=('#dbe7ff', '#cbdbff'), left=('#a4bbee', '#91abe4'), right=('#bacdf6', '#abc2f0')) if WHITE else LIGHT
SEAM = '#c3cbe0' if WHITE else '#3a3e47'
SLOT = ('#4a5163', '#9aa3bb') if WHITE else ('#07080a', '#3b3f48')

g = Iso(40)
L, D, H, T = 11.0, 8.0, 2.7, 0.28          # 케이스 폭(x) · 깊이(y) · 높이 · 벽 두께
N, ct, cg = 8, 1.0, 0.26                    # 줄당 셀 수 · 셀 두께 · 틈
rows = [(T + 0.3, 3.4), (T + 0.3 + 3.4 + 0.45, 3.4)]
ch = 2.15                                   # 셀 높이

# 밑판(케이스보다 조금 넓은 받침)
g.box(-0.25, -0.25, -0.22, L + 0.5, D + 0.5, 0.22, pal=BASE, out=EDGE, sw=2)
# 안쪽 바닥 · 뒤 벽 · 왼쪽 벽(안쪽 면이 보인다)
g.box(T, T, 0, L - 2 * T, D - 2 * T, 0.18, pal=FLOOR_IN, out=CASE_EDGE, sw=1.2)
IOP = 0.55 if WHITE else None
g.box(0, 0, 0, L, T, H, pal=BLK_IN, out=CASE_EDGE, face_op=IOP)
g.box(0, T, 0, T, D - T, H, pal=BLK_IN, out=CASE_EDGE, face_op=IOP)
# 셀 — 뒤 줄부터, 줄 안에선 왼쪽부터
cx0 = T + (L - 2 * T - (N * ct + (N - 1) * cg)) / 2
for (y0, dy) in rows:
    for i in range(N):
        x = cx0 + i * (ct + cg)
        g.box(x, y0, 0.18, ct, dy, ch, pal=CELL)
        for yy in (y0 + 0.45, y0 + dy - 1.0):
            g.box(x + 0.25, yy, 0.18 + ch, 0.5, 0.55, 0.16, pal=DEEP, out=DEEP['out'], sw=1.2)
# 오른쪽 벽 · 앞 벽(바깥 면이 보인다)
WOP = 0.5 if VAR == 'all' else 0.55 if WHITE else None
g.box(L - T, T, 0, T, D - 2 * T, H, pal=BLK, out=CASE_EDGE, face_op=WOP)
g.box(0, D - T, 0, L, T, H, pal=BLK, out=CASE_EDGE, face_op=WOP)

# ── 앞면 디테일 (y = D 평면, u = x, w = 위에서 아래로) ──
slots = ''.join(f'<rect x="{u:.2f}" y="{w:.2f}" width=".62" height=".15" rx=".075" fill="{SLOT[0]}" stroke="{SLOT[1]}" stroke-width=".02"/>'
                for w in (1.55, 1.85, 2.15) for u in [0.9 + k * 0.8 for k in range(12)] if u < L - 0.9)
screws = ''.join(f'<circle cx="{u}" cy="{w}" r=".075" fill="#5d636e" stroke="#0c0d10" stroke-width=".02"/>'
                 for u in (0.22, L - 0.22, L / 2) for w in (0.22, H - 0.22))
front = (
    f'<rect x=".1" y=".1" width="{L - .2}" height="{H - .2}" fill="none" stroke="{SEAM}" stroke-width=".03"/>'
    + slots + screws
    # 둥근 커넥터
    + '<circle cx=".75" cy=".75" r=".3" fill="#3c414b" stroke="#0c0d10" stroke-width=".04"/><circle cx=".75" cy=".75" r=".16" fill="#16181c" stroke="#6a707b" stroke-width=".02"/>'
    # 검정 커넥터(사각 + 안쪽 단자)
    + '<rect x="1.4" y=".28" width="1.3" height="1.12" rx=".07" fill="#101215" stroke="#5a606b" stroke-width=".045"/>'
    + '<rect x="1.66" y=".48" width=".78" height=".72" rx=".05" fill="#050607" stroke="#2a2d33" stroke-width=".03"/>'
    + '<rect x="1.86" y=".64" width=".38" height=".4" rx=".03" fill="#1d2025"/>'
    + ''.join(f'<circle cx="{u}" cy="{w}" r=".055" fill="#8a909b"/>' for u in (1.5, 2.6) for w in (.38, 1.3))
    # A-PRO 명판
    + f'<rect x="{L / 2 - 1.3}" y=".42" width="2.6" height=".78" rx=".08" fill="#121418" stroke="#4d525c" stroke-width=".035"/>'
    + f'<text x="{L / 2}" y=".98" text-anchor="middle" font-family="SUIT, Pretendard, Arial, sans-serif" font-weight="800" font-size=".48" fill="#ffffff" letter-spacing=".02">A-PRO</text>'
    # 주황 커넥터
    + f'<rect x="{L - 2.35}" y=".3" width="1.15" height="1.1" rx=".07" fill="#f07c2c" stroke="#a94f14" stroke-width=".045"/>'
    + f'<rect x="{L - 2.12}" y=".52" width=".69" height=".66" rx=".05" fill="#b8551a" stroke="#7d3a10" stroke-width=".03"/>'
    + f'<rect x="{L - 1.95}" y=".64" width=".35" height=".42" rx=".03" fill="#e4e7ee"/>'
    + ''.join(f'<circle cx="{u}" cy="{w}" r=".05" fill="#c8ccd4"/>' for u in (L - 2.25, L - 1.3) for w in (.4, 1.3))
)
plane(g, (0, D, H), 'x', front)
# 오른쪽 면 디테일 (x = L 평면, u = -y 방향이 아니라 y 방향)
right = (f'<rect x=".1" y=".1" width="{D - .2}" height="{H - .2}" fill="none" stroke="{SEAM}" stroke-width=".03"/>'
         + ''.join(f'<circle cx="{u}" cy="{w}" r=".075" fill="#5d636e" stroke="#0c0d10" stroke-width=".02"/>' for u in (0.22, D - 0.22) for w in (0.22, H - 0.22)))
plane(g, (L, 0, H), 'y', right)

# 반투명 뚜껑
if VAR:
    g.box(-0.04, -0.04, H, L + 0.08, D + 0.08, 0.16, pal=BLK, out=CASE_EDGE, face_op=0.3 if WHITE else 0.42)

# ── 공기 ──
def fade(gid, a, b, color, o0, o1, s0=0, s1=1):
    (x1, y1), (x2, y2) = g.p(*a), g.p(*b)
    g.defs[gid] = (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}">'
                   f'<stop offset="{s0}" stop-color="{color}" stop-opacity="{o0}"/><stop offset="{s1}" stop-color="{color}" stop-opacity="{o1}"/></linearGradient>')
    return f'url(#{gid})'

# 더운 공기 — 셀 위에서 위로(뒤쪽부터 그린다)
for j, x in enumerate((2.3, 4.5, 6.7, 8.9)):
    y = D * 0.45
    a, b = (x, y, H - 0.1 + (0.26 if VAR else 0)), (x, y, H + 3.7)
    ribbon3(g, a, b, (1, 0, 0), 0.34, fade(f'hot{j}', a, b, RED, 0.0, 1, 0, .7), hl=1.0, hw2=2.0)
# 찬 공기 — 앞 그릴로 들어간다
for j, x in enumerate((2.2, 4.4, 6.6, 8.8)):
    a, b = (x, D + 3.6, 0.75), (x, D + 0.25, 0.75)
    ribbon3(g, a, b, (1, 0, 0), 0.3, fade(f'cool{j}', a, b, BLUE, 0.0, 1, 0, .6), hl=0.95, hw2=2.0)

open(sys.argv[1], 'w', encoding='utf-8').write(g.svg(600, 12))
