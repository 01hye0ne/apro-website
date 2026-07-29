# -*- coding: utf-8 -*-
"""북미 라벨 재배치 검증 — 미시간·조지아만 왼쪽으로 뻗고, 팝업은 그 라벨 아래로.
45° 규칙과 팝업이 지도 밖으로 안 나가는지까지 같이 본다."""
import re
from PIL import Image, ImageDraw, ImageFont

K = 387.78 / 1000
LAT_TOP, LAT_BOT = 83.6, -56.0
DW = 958

svg = open('world-map.svg', encoding='utf-8').read()
vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
VW, VH = float(vb.group(1)), float(vb.group(2))
DH = round(DW * VH / VW)

PINS = [
    ('캐나다 온타리오', '',               43.65,  -79.38, 36.0, 18.0, 'l'),
    ('미시간',          '북미법인',       42.33,  -83.05, 20.0, 20.0, 'r'),
    ('오하이오',        '',               39.96,  -82.99, 36.0, 30.0, 'l'),
    ('테네시',          '',               36.16,  -86.78, 36.0, 42.0, 'l'),
    ('조지아',          '',               33.75,  -84.39, 20.0, 46.0, 'r'),
    ('독일',            '',               50.94,    6.96, 43.0, 11.0, 'r'),
    ('폴란드',          '유럽법인',       51.11,   17.03, 62.0,  8.0, 'l'),
    ('중국 남경',       '중국법인',       32.06,  118.80, 88.0, 47.0, 'l'),
    ('인도네시아 카라왕', '인도네시아법인', -6.31,  107.30, 72.0, 79.0, 'r'),
]

# 팝업: 오른쪽 끝을 30% 에 맞추고 라벨 아래로 떨군다
POP_RIGHT, POP_W = 30.0, 22.0
POPS = {'미시간': 20.0, '조지아': 46.0}     # 라벨 y

def pos(lon, lat):
    return (lon + 180) / 360 * 100, (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * 100

rows = []
for nm, sub, lat, lon, lx, ly, side in PINS:
    x, y = pos(lon, lat)
    dirx = 1 if lx > x else -1
    need = abs(ly - y) * K
    ex = x + dirx * need
    rows.append((nm, sub, x, y, ex, lx, ly, side, need, abs(lx - x)))

print(f'{"거점":<18}{"팔꿈치x":>9}{"필요":>7}{"여유":>7}  판정')
for nm, sub, x, y, ex, lx, ly, side, need, room in rows:
    print(f'{nm:<18}{ex:9.2f}{need:7.2f}{room:7.2f}  {"OK" if room >= need - 1e-9 else "부족!"}')

# 팝업 세로 크기 (CSS 와 동일 계산)
img_w = DW * POP_W / 100 - 12
pop_h = 6 + img_w * 2 / 3 + 26 + 6
print(f'\n팝업 {DW*POP_W/100:.0f} x {pop_h:.0f}px  (지도 높이 {DH}px)')

img = Image.new('RGB', (DW, DH), 'white')
dr = ImageDraw.Draw(img)
d = re.search(r'<path class="land"[^>]*d="([^"]+)"', svg).group(1)
S = DW / VW
for s_ in d.split('Z'):
    pts = [(float(a) * S, float(b) * S) for a, b in re.findall(r'[ML](-?[\d.]+) (-?[\d.]+)', s_)]
    if len(pts) >= 3:
        dr.polygon(pts, fill=(216, 220, 226), outline=(255, 255, 255))

F = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 13)
FS = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 11)
BLUE = (44, 87, 144)
def topx(u, v): return u / 100 * DW, v / 100 * DH

print()
for nm, sub, x, y, ex, lx, ly, side, need, room in rows:
    p0, p1, p2 = topx(x, y), topx(ex, ly), topx(lx, ly)
    dr.line([p0, p1, p2], fill=BLUE, width=1)
    if nm in POPS:      # 칩
        w = max(dr.textlength(nm, font=F), dr.textlength(f'({sub})', font=FS) if sub else 0)
        h = 34 if sub else 20
        dr.rounded_rectangle([p2[0]-w-9, p2[1]-h/2, p2[0]+2, p2[1]+h/2], 3, fill=(228, 236, 246))
        lab_bottom = (p2[1] + h/2) / DH * 100
        top = lab_bottom + 2.5
        px0, py0 = topx(POP_RIGHT - POP_W, top)
        dr.rectangle([px0, py0, px0 + DW*POP_W/100, py0 + pop_h], outline=(200,60,60), width=2)
        print(f'{nm} 팝업 top {top:5.1f}%  bottom {(py0+pop_h)/DH*100:5.1f}%  '
              f'{"OK" if py0 + pop_h <= DH else "지도 밖!"}')
    dr.ellipse([p0[0]-3.5, p0[1]-3.5, p0[0]+3.5, p0[1]+3.5], outline=BLUE, width=2, fill=(255,255,255))
    anc = 'lm' if side == 'l' else 'rm'
    tx = p2[0] + (5 if side == 'l' else -5)
    if sub:
        dr.text((tx, p2[1]-7), nm, font=F, fill=(27,39,51), anchor=anc)
        dr.text((tx, p2[1]+7), f'({sub})', font=FS, fill=BLUE, anchor=anc)
    else:
        dr.text((tx, p2[1]), nm, font=F, fill=(27,39,51), anchor=anc)

img.save('proof-left.png')
print('\n<!-- 폴리라인 -->')
for nm, sub, x, y, ex, lx, ly, side, need, room in rows:
    print(f'            <polyline points="{x:.2f},{y:.2f} {ex:.2f},{ly:g} {lx:g},{ly:g}" />')
