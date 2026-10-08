# 실행: python content-export/tools/iso/container_cooling.py air assets/ess-container-air-cooling.svg
#       python content-export/tools/iso/container_cooling.py liquid assets/ess-container-liquid-cooling.svg
"""Container Air / Liquid Cooling — 모듈 두 장과 같은 말씨(흰 젖빛 반투명 케이스 · 연한 파랑 배터리).
실제 컨테이너 사진처럼 골판 벽 · A-PRO 로고 · 끝면 문 · 모서리 쇠붙이 · 검정 밑틀.
air    : 문(옆면)에 붙은 HVAC 로 찬 공기(파랑)를 안으로 들여 랙 줄을 따라 흘린다 — 밖으로 빼는 더운 바람은 없다(2026-10-08 클라이언트)
liquid : 안쪽 끝 칠러가 랙마다 찬 냉각수(파랑)를 보내고 데워진 냉각수(빨강)를 돌려받는다"""
import sys
from iso import Iso, DEEP, BLUE, RED, ribbon3, plane

KIND = sys.argv[1]
CASE = dict(top=('#ffffff', '#f4f7fd'), left=('#eef2fb', '#e1e7f5'), right=('#f5f8fe', '#e9eef8'))
RACK = dict(top=('#dbe7ff', '#cbdbff'), left=('#a4bbee', '#91abe4'), right=('#bacdf6', '#abc2f0'))
FLOOR = dict(top=('#e6ebf6', '#dde3f1'), left=('#cfd6e8', '#cfd6e8'), right=('#d8deee', '#d8deee'))
BASE = dict(top=('#3a3e47', '#33373f'), left=('#16181d', '#121418'), right=('#1d2026', '#181a1f'))
CAST = dict(top=('#5d636e', '#4d535e'), left=('#2a2e36', '#22252c'), right=('#353a43', '#2c3038'))
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
x_end = L - 0.5
NR, rg = 9, 0.14
rw = (x_end - 0.6 - (NR - 1) * rg) / NR
ry0, rd, rh = 0.55, 2.1, 4.6
racks = []
for i in range(NR):
    x = 0.6 + i * (rw + rg)
    racks.append(x)
    g.box(x, ry0, 0.12, rw, rd, rh, pal=RACK)
    # 랙 앞면(+y) 모듈 칸 줄 · 상태 표시 점
    lines = ''.join(f'<path d="M.12 {w:.2f} H{rw - .12:.2f}" stroke="#7f95cc" stroke-width=".035"/>' for w in [0.55 + k * 0.58 for k in range(8)])
    lines += f'<rect x="{rw / 2 - .18:.2f}" y=".18" width=".36" height=".2" rx=".04" fill="#3261e4"/>'
    plane(g, (x, ry0 + rd, 0.12 + rh), 'x', lines)

ztop = 0.12 + rh                           # 랙 윗면
zp = ztop + 0.35                            # 배관 높이(랙 위)
YB, YR = ry0 + rd * 0.32, ry0 + rd * 0.72   # 파랑(공급) · 빨강(회수) 줄
PIPES = []
if KIND == 'liquid':
    # 랙마다 위에서 짧게 내려 꽂고, 두 줄이 끝면을 지나 바깥 냉각 유닛 윗면으로 들어간다
    for x in racks:
        xc = x + rw / 2
        PIPES.append(([(xc, YB, zp), (xc, YB, ztop)], BLUE, 7))
        PIPES.append(([(xc, YR, zp), (xc, YR, ztop)], RED, 7))
    for yy, c in ((YB, BLUE), (YR, RED)):
        PIPES.append(([(racks[0] + rw / 2, yy, zp), (L + 1.4, yy, zp), (L + 1.4, yy, 4.4)], c, 12))

# 오른쪽 끝 벽(문) · 앞 벽(긴 면)
g.box(L - T, T, 0, T, D - 2 * T, H, pal=CASE, out=CE, face_op=WOP)
g.box(0, D - T, 0, L, T, H, pal=CASE, out=CE, face_op=WOP)

if KIND == 'liquid':
    g.raw('<g opacity=".55">')
    for pts, c, w in PIPES:
        inner = [q for q in pts if q[0] <= L - T]
        if len(pts) == 3:
            inner = [pts[0], (L - T, pts[0][1], pts[0][2])]
        pipe(inner, c, w)
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
    front += louver(L - 3.2, 1.9, 1.15, 3.2, 14)
front += (f'<text x="{L * 0.36:.2f}" y="2.55" text-anchor="middle" font-family="SUIT, Pretendard, Arial, sans-serif" font-weight="800" font-size="1.15" fill="{NAVY}">A-PRO</text>'
          f'<text x="{L * 0.36:.2f}" y="3.35" text-anchor="middle" font-family="SUIT, Pretendard, Arial, sans-serif" font-weight="700" font-size=".44" fill="#3a3f4a">ENERGY STORAGE SYSTEM</text>')
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
    ux0, uw = L + 0.35, 2.2
    g.box(ux0, 0.6, 0, uw, D - 1.2, 4.4, pal=UNIT, out=CE)              # 냉각 유닛(칠러)
    fan = ''.join(f'<circle cx="{u:.2f}" cy="1.25" r=".72" fill="#8f98aa" stroke="#474c59" stroke-width=".05"/><circle cx="{u:.2f}" cy="1.25" r=".18" fill="#474c59"/>'
                  for u in (1.2, D - 2.4))
    fan += ''.join(f'<path d="M.3 {w:.2f} H{D - 1.5:.2f}" stroke="#9aa2b3" stroke-width=".06"/>' for w in (2.6, 2.9, 3.2, 3.5, 3.8))
    plane(g, (ux0 + uw, 0.6, 4.4), 'y', fan)
    side = f'<rect x=".25" y=".3" width="{uw - .5:.2f}" height="3.8" fill="none" stroke="#9aa2b3" stroke-width=".05"/>'
    plane(g, (ux0, D - 0.6, 4.4), 'x', side)
    for pts, c, w in PIPES:                                              # 끝면 밖 배관(지붕 높이 → 유닛 윗면)
        if len(pts) == 3:
            pipe([(L, pts[0][1], zp), (L + 1.4, pts[0][1], zp), (L + 1.4, pts[0][1], 4.4)], c, w)
    for k in range(4):                                                   # 파랑 → 랙으로(←) · 빨강 → 유닛으로(→)
        xa = L - 1.3 - k * 3.3
        ribbon3(g, (xa, YB, zp + 0.02), (xa - 1.0, YB, zp + 0.02), (0, 1, 0), 0.13, BLUE, hl=0.42, hw2=2.2)
        ribbon3(g, (xa - 1.0, YR, zp + 0.02), (xa, YR, zp + 0.02), (0, 1, 0), 0.13, RED, hl=0.42, hw2=2.2)

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
