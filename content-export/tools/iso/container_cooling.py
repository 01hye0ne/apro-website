# 실행: python content-export/tools/iso/container_cooling.py air assets/ess-container-air-cooling.svg
#       python content-export/tools/iso/container_cooling.py liquid assets/ess-container-liquid-cooling.svg
"""Container Air / Liquid Cooling — 모듈 두 장과 같은 말씨(흰 젖빛 반투명 케이스 · 연한 파랑 배터리).
실제 컨테이너 사진처럼 골판 벽 · A-PRO 로고 · 끝면 문 · 모서리 쇠붙이 · 검정 밑틀.
air    : 문(옆면)에 붙은 HVAC 로 찬 공기(파랑)를 안으로 들여 랙 줄을 따라 흘린다 — 밖으로 빼는 더운 바람은 없다(2026-10-08 클라이언트)
liquid : 안쪽 끝 칠러가 랙 앞을 두르는 순환 배관으로 찬 냉각수(파랑, 아래)를 보내고 데워진 냉각수(빨강, 위)를 돌려받는다(2026-10-08 클라이언트 참고 자료)"""
import sys
from iso import Iso, DEEP, BLUE, RED, ribbon3, plane

KIND = sys.argv[1]
CASE = dict(top=('#ffffff', '#f4f7fd'), left=('#eef2fb', '#e1e7f5'), right=('#f5f8fe', '#e9eef8'))
RACK = dict(top=('#dbe7ff', '#cbdbff'), left=('#a4bbee', '#91abe4'), right=('#bacdf6', '#abc2f0'))
FLOOR = dict(top=('#e6ebf6', '#dde3f1'), left=('#cfd6e8', '#cfd6e8'), right=('#d8deee', '#d8deee'))
BASE = dict(top=('#3a3e47', '#33373f'), left=('#16181d', '#121418'), right=('#1d2026', '#181a1f'))
CAST = dict(top=('#5d636e', '#4d535e'), left=('#2a2e36', '#22252c'), right=('#353a43', '#2c3038'))
CHILL = dict(top=('#c9ced8', '#b9bfcb'), left=('#7d8597', '#6d7588'), right=('#9aa1b0', '#8b93a3'))   # 칠러 — 젖빛 너머로 보이게 짙은 회색
UNIT = dict(top=('#f1f3f7', '#dfe3ea'), left=('#a9b0bd', '#959dac'), right=('#c4cad4', '#b3bac6'))
EDGE, CE, SEAM = '#0c0d10', '#474c59', '#c9d0e2'
NAVY = '#1f3f8f'

g = Iso(40)
L, D, H, T = 15.0, 6.0, 6.4, 0.22          # 컨테이너 길이(x) · 폭(y) · 높이 · 벽 두께
WOP = 0.72                                 # 벽 젖빛 — 모듈(55%)보다 짙게, 안이 큰 만큼 랙이 앞으로 튀지 않게


def fade(gid, a, b, color, o0, o1, s0=0, s1=1):
    (x1, y1), (x2, y2) = g.p(*a), g.p(*b)
    g.defs[gid] = (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}">'
                   f'<stop offset="{s0}" stop-color="{color}" stop-opacity="{o0}"/><stop offset="{s1}" stop-color="{color}" stop-opacity="{o1}"/></linearGradient>')
    return f'url(#{gid})'


def pipe(pts3, color, sw=12):
    d = 'M' + ' L'.join('%.1f %.1f' % g.p(*q) for q in pts3)
    g.raw(f'<path d="{d}" stroke="#ffffff" stroke-width="{sw + 4}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
          f'<path d="{d}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>')


# 밑틀 · 뒤 벽 · 왼쪽 끝 벽 · 바닥
g.box(-0.2, -0.2, -0.35, L + 0.4, D + 0.4, 0.35, pal=BASE, out=EDGE, sw=2)
g.box(0, 0, 0, L, T, H, pal=CASE, out=CE, face_op=WOP)
g.box(0, T, 0, T, D - T, H, pal=CASE, out=CE, face_op=WOP)
g.box(T, T, 0, L - 2 * T, D - 2 * T, 0.12, pal=FLOOR, out=CE, sw=1.2)

# 배터리 랙 — 뒤 벽을 따라 한 줄
CX0, CW = T + 0.15, 2.35                   # 칠러(리퀴드) — 컨테이너 맨 안쪽(문 반대 끝, 2026-10-08 사용자)
CD = D - 0.6                               # 칠러 앞면 y — 앞쪽으로 깊게(2026-10-08 사용자). 랙보다 안쪽(x 작음)이라 랙은 여전히 칠러 위로 겹친다
CH = 4.7                                   # 칠러 높이
HOLE = dict(red=1.3, blue=0.55)            # 칠러 옆면(문 쪽 면) 아래 배관 구멍 높이
x0r = 0.6 if KIND == 'air' else CX0 + CW + 0.35
x_end = L - 0.5
NR, rg = (9 if KIND == 'air' else 7), 0.14
rw = (x_end - x0r - (NR - 1) * rg) / NR
ry0, rd, rh = 0.55, 2.1, 4.6
racks = []
RACK_AT = len(g.items)                     # 칠러는 랙보다 먼저 그려야 랙이 위로 겹친다 — 칠러 조각을 이 자리로 옮겨 넣는다
for i in range(NR):
    x = x0r + i * (rw + rg)
    racks.append(x)
    g.box(x, ry0, 0.12, rw, rd, rh, pal=RACK)
    # 랙 앞면(+y) 모듈 칸 줄 · 상태 표시 점
    lines = ''.join(f'<path d="M.12 {w:.2f} H{rw - .12:.2f}" stroke="#7f95cc" stroke-width=".035"/>' for w in [0.55 + k * 0.58 for k in range(8)])
    lines += f'<rect x="{rw / 2 - .18:.2f}" y=".18" width=".36" height=".2" rx=".04" fill="#3261e4"/>'
    plane(g, (x, ry0 + rd, 0.12 + rh), 'x', lines)

ztop = 0.12 + rh                           # 랙 윗면
yp = ry0 + rd + 0.32                        # 순환 배관이 지나는 줄(랙 앞)
zt, zb = ztop - 0.3, 0.5                    # 위 회수관(빨강) · 아래 공급관(파랑)
risers = [x - rg / 2 for x in racks] + [racks[-1] + rw + rg / 2]


def loop_pipes():
    """랙을 두르는 순환 배관 — 위 빨강 · 아래 파랑 · 랙 사이 세로관(아래 파랑 → 위 빨강)"""
    for j, xr in enumerate(risers):
        (x1, y1), (x2, y2) = g.p(xr, yp, zb), g.p(xr, yp, zt)
        gid = f'rs{j}'
        g.defs[gid] = (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}">'
                       f'<stop offset=".15" stop-color="{BLUE}"/><stop offset=".85" stop-color="{RED}"/></linearGradient>')
        pipe([(xr, yp, zb), (xr, yp, zt)], f'url(#{gid})', 8)
    xd = CX0 + CW + 0.32                    # 칠러 앞에서 아래로 꺾어 구멍으로
    pipe([(risers[-1], yp, zt), (xd, yp, zt), (xd, yp, HOLE['red']), (CX0 + CW, yp, HOLE['red'])], RED, 11)
    pipe([(risers[-1], yp, zb), (xd, yp, zb), (xd, yp, HOLE['blue']), (CX0 + CW, yp, HOLE['blue'])], BLUE, 11)


def chiller():
    """칠러 — 맨 안쪽 끝, 앞면(+y)에 팬 그릴"""
    g.box(CX0, 0.45, 0.12, CW, CD - 0.45, CH, pal=CHILL, out=CE)
    zc = 0.12 + CH
    fan = ''.join(f'<path d="M.25 {w:.2f} H{CW - .25:.2f}" stroke="#5d6475" stroke-width=".07"/>' for w in [0.4 + k * 0.22 for k in range(9)])
    fan += f'<rect x=".2" y="2.55" width="{CW - .4:.2f}" height="1.9" fill="none" stroke="#5d6475" stroke-width=".05"/><circle cx="{CW / 2:.2f}" cy="3.5" r=".1" fill="#3d4352"/>'
    plane(g, (CX0, CD, zc), 'x', fan)
    # 윗면 둥근 팬 둘 — 테 · 날개 · 가운데 축
    top = ''
    for v in ((CD - 0.45) * 0.3, (CD - 0.45) * 0.72):
        cu, r = CW / 2, 0.82
        top += f'<circle cx="{cu:.2f}" cy="{v:.2f}" r="{r}" fill="#5d6475" stroke="#3d4352" stroke-width=".06"/>'
        top += f'<circle cx="{cu:.2f}" cy="{v:.2f}" r="{r - .12:.2f}" fill="#7d8597"/>'
        top += ''.join(f'<path d="M{cu:.2f} {v:.2f} L{cu + (r - .18) * __import__("math").cos(a):.3f} {v + (r - .18) * __import__("math").sin(a):.3f}" stroke="#3d4352" stroke-width=".09" stroke-linecap="round"/>'
                       for a in [k * 3.14159 / 3 + .3 for k in range(6)])
        top += f'<circle cx="{cu:.2f}" cy="{v:.2f}" r=".16" fill="#3d4352"/>'
    plane(g, (CX0, 0.45, zc), 'z', top)
    # 옆면(문 쪽 면) 아래 배관 구멍
    holes = ''.join(f'<circle cx="{yp - 0.45:.2f}" cy="{CH + 0.12 - z:.2f}" r=".24" fill="#2a2e36" stroke="#3d4352" stroke-width=".05"/>' for z in HOLE.values())
    plane(g, (CX0 + CW, 0.45, zc), 'y', holes)


if KIND == 'liquid':
    n0 = len(g.items)
    chiller()
    chunk = g.items[n0:]                     # 칠러 조각을 떼어
    del g.items[n0:]
    g.items[RACK_AT:RACK_AT] = chunk         # 랙 앞으로(2026-10-08: 사이트에서 칠러가 랙 위로 올라와 보였다)
    loop_pipes()

# 오른쪽 끝 벽(문) · 앞 벽(긴 면)
g.box(L - T, T, 0, T, D - 2 * T, H, pal=CASE, out=CE, face_op=WOP)
g.box(0, D - T, 0, L, T, H, pal=CASE, out=CE, face_op=WOP)

if KIND == 'liquid':
    g.raw('<g opacity=".7">')                 # 젖빛 벽 너머로 또렷이 — 배관만 한 번 더(칠러는 덧그리면 랙을 덮는다)
    loop_pipes()
    g.raw('</g>')

# ── 앞면(긴 면) 디테일 — 골판 · 로고 · 루버 ──
ribs = ''.join(f'<path d="M{u:.2f} .3 V{H - .35:.2f}" stroke="{SEAM}" stroke-width=".04"/>' for u in [0.55 + k * 0.42 for k in range(int((L - 1.1) / 0.42) + 1)])
front = (f'<rect x=".08" y=".08" width="{L - .16}" height="{H - .16}" fill="none" stroke="{SEAM}" stroke-width=".05"/>'
         f'<path d="M.08 .3 H{L - .08} M.08 {H - .35:.2f} H{L - .08}" stroke="{SEAM}" stroke-width=".05"/>' + ribs)


def louver(u, w, bw, bh, n):
    s = f'<rect x="{u:.2f}" y="{w:.2f}" width="{bw}" height="{bh}" fill="#eef1f7" stroke="#8a93a8" stroke-width=".05"/>'
    s += ''.join(f'<path d="M{u + .1:.2f} {w + .14 + k * (bh - .28) / (n - 1):.2f} H{u + bw - .1:.2f}" stroke="#6c7489" stroke-width=".07"/>' for k in range(n))
    return s


lu = ()
for u in lu:
    front += louver(u, H - 1.95, 1.5, 1.35, 7)
if KIND == 'liquid':
    front += louver(CX0 + 0.6, 1.9, 1.15, 3.2, 14)      # 칠러 앞 통풍 루버
# A-PRO 로고 — GNB 로고(assets/logo-apro-blue.svg, 78×17 path 하나)를 그대로 앞면 각도로. 앞면 가운데
import os, re
_logo = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'assets', 'logo-apro-blue.svg'), encoding='utf-8').read()
LOGO_D, LOGO_FILL = re.search(r'<path d="([^"]+)" fill="([^"]+)"', _logo).groups()
LW = 5.2                                    # 로고 폭(단위) — 78 → 5.2
lk = LW / 78
front += f'<g transform="translate({L / 2 - LW / 2:.3f} 1.85) scale({lk:.5f})"><path d="{LOGO_D}" fill="{LOGO_FILL}"/></g>'
front += (f'<text x="{L / 2:.2f}" y="3.55" text-anchor="middle" font-family="SUIT, Pretendard, Arial, sans-serif" font-weight="700" font-size=".44" fill="#3a3f4a">ENERGY STORAGE SYSTEM</text>')
plane(g, (0, D, H), 'x', front)

# ── 끝면(문) 디테일 ──
door = (f'<rect x=".25" y=".35" width="{D / 2 - .3:.2f}" height="{H - .75:.2f}" fill="none" stroke="#aab2c3" stroke-width=".05"/>'
        f'<rect x="{D / 2 + .05:.2f}" y=".35" width="{D / 2 - .3:.2f}" height="{H - .75:.2f}" fill="none" stroke="#aab2c3" stroke-width=".05"/>')
for u in (0.85, 2.15, D / 2 + 0.85, D / 2 + 2.15):
    door += f'<path d="M{u:.2f} .45 V{H - .5:.2f}" stroke="#7d869a" stroke-width=".09"/>'
    door += f'<rect x="{u - .12:.2f}" y="{H * .55:.2f}" width=".24" height=".5" rx=".04" fill="#9aa2b3" stroke="#5d6475" stroke-width=".03"/>'
for w in (0.9, H / 2, H - 1.2):
    door += f'<rect x=".08" y="{w:.2f}" width=".22" height=".38" fill="#9aa2b3"/><rect x="{D - .3:.2f}" y="{w:.2f}" width=".22" height=".38" fill="#9aa2b3"/>'
plane(g, (L, 0, H), 'y', door)

# 지붕(반투명)
g.box(-0.04, -0.04, H, L + 0.08, D + 0.08, 0.14, pal=CASE, out=CE, face_op=0.45)
# 모서리 쇠붙이(보이는 꼭짓점)
c = 0.42
for (x, y, z) in [(0, D - c, -0.02), (L - c, D - c, -0.02), (L - c, 0, -0.02), (0, D - c, H + 0.14 - c), (L - c, D - c, H + 0.14 - c), (L - c, 0, H + 0.14 - c), (0, 0, H + 0.14 - c)]:
    g.box(x, y, z, c, c, c, pal=CAST, out=EDGE, sw=1.4)

# ── 흐름 ──
if KIND == 'liquid':
    g.raw('<g opacity=".95">')
    for k in range(3):                        # 파랑 칠러 → 랙(→, 아래) · 빨강 랙 → 칠러(←, 위)
        xa = CX0 + CW + 0.7 + k * 3.2
        ribbon3(g, (xa, yp + 0.05, zb), (xa + 0.95, yp + 0.05, zb), (0, 0, 1), 0.14, BLUE, hl=0.42, hw2=2.2)
        ribbon3(g, (xa + 0.95, yp + 0.05, zt), (xa, yp + 0.05, zt), (0, 0, 1), 0.14, RED, hl=0.42, hw2=2.2)
    g.raw('</g>')

if KIND == 'air':
    # 문짝(앞쪽 문)에 붙은 HVAC — 위아래 흡입 그릴 둘 + 가운데 판
    hy0, hy1, hz0, hz1 = D / 2 + 0.3, D - 0.5, 0.9, 5.3
    g.box(L, hy0, hz0, 0.5, hy1 - hy0, hz1 - hz0, pal=UNIT, out=CE)
    hw_, hh = hy1 - hy0, hz1 - hz0
    grill = lambda w0, w1: (f'<rect x=".22" y="{w0:.2f}" width="{hw_ - .44:.2f}" height="{w1 - w0:.2f}" fill="#e6e9f0" stroke="#7d869a" stroke-width=".05"/>'
                            + ''.join(f'<path d="M.32 {w0 + .16 + k * .2:.2f} H{hw_ - .32:.2f}" stroke="#5d6475" stroke-width=".07"/>' for k in range(int((w1 - w0 - .2) / .2))))
    hv = grill(0.3, 1.75) + grill(hh - 1.75, hh - 0.3)
    hv += f'<rect x=".22" y="2.0" width="{hw_ - .44:.2f}" height="{hh - 4.0:.2f}" fill="none" stroke="#9aa2b3" stroke-width=".05"/><circle cx="{hw_ / 2:.2f}" cy="{hh / 2:.2f}" r=".1" fill="#5d6475"/>'
    plane(g, (L + 0.5, hy0, hz1), 'y', hv)
    # 찬 공기 — 밖에서 HVAC 로 들어간다
    yc = (hy0 + hy1) / 2
    for j, z in enumerate((hz1 - 0.95, (hz0 + hz1) / 2, hz0 + 0.95)):
        a, b = (L + 4.0, yc, z), (L + 0.65, yc, z)
        ribbon3(g, a, b, (0, 0, 1), 0.28, fade(f'cool{j}', a, b, BLUE, 0, 1, 0, .6), hl=0.95, hw2=2.0)
    # 안 — 찬 공기가 랙 줄을 따라 흐른다(벽 너머 x-ray, 문 쪽에서 안쪽으로 옅어짐)
    yi = ry0 + rd + 0.45
    for j, z in enumerate((2.35, 1.15)):
        (x1, y1), (x2, y2) = g.p(L - 0.6, yi, z), g.p(4.6, yi, z)
        gid = f'in{j}'
        g.defs[gid] = (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}">'
                       f'<stop offset="0" stop-color="{BLUE}" stop-opacity=".75"/><stop offset="1" stop-color="{BLUE}" stop-opacity=".2"/></linearGradient>')
        for k in range(3):                       # 셋 — 넷째는 앞면 로고와 겹친다
            xa = L - 0.8 - k * 3.4
            ribbon3(g, (xa, yi, z), (xa - 2.4, yi, z), (0, 0, 1), 0.3, f'url(#{gid})', hl=0.9, hw2=1.9)

open(sys.argv[2], 'w', encoding='utf-8').write(g.svg(600, 12))
