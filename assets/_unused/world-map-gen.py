# -*- coding: utf-8 -*-
"""
Natural Earth 110m(퍼블릭 도메인) → 정거원통도법(equirectangular) SVG.

투영식을 여기서 고정하므로, 마커 좌표는 추정 없이 아래 식으로 정확히 나온다:
    x% = (lon + 180) / 360 * 100
    y% = (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * 100
"""
import json

LAT_TOP, LAT_BOT = 83.6, -56.0   # 남극 대륙은 잘라낸다
W = 1000.0
H = round(W * (LAT_TOP - LAT_BOT) / 360.0, 2)
MIN_PX = 1.2                      # 이보다 작은 섬은 버린다 (1000px 기준 1.2px)

src = json.load(open('ne110m.geojson', encoding='utf-8'))

def project(lon, lat):
    x = (lon + 180.0) / 360.0 * W
    y = (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * H
    return x, y

def ring_to_path(ring):
    pts = [project(c[0], c[1]) for c in ring]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    if (max(xs) - min(xs)) < MIN_PX and (max(ys) - min(ys)) < MIN_PX:
        return None
    out, last = [], None
    for i, (x, y) in enumerate(pts):
        xr, yr = round(x, 1), round(y, 1)
        if (xr, yr) == last:          # 반올림 후 중복점 제거
            continue
        out.append(('M' if i == 0 else 'L') + f'{xr:g} {yr:g}')
        last = (xr, yr)
    if len(out) < 4:
        return None
    if not out[0].startswith('M'):
        out[0] = 'M' + out[0][1:]
    return ''.join(out) + 'Z'

parts, kept, dropped = [], 0, 0
for feat in src['features']:
    if feat['properties'].get('NAME') == 'Antarctica':
        continue
    geom = feat['geometry']
    polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
    for poly in polys:
        for ring in poly:                      # [0]=외곽, 이후=구멍
            d = ring_to_path(ring)
            if d:
                parts.append(d); kept += 1
            else:
                dropped += 1

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {H:g}" '
    f'width="{W:g}" height="{H:g}" role="img" aria-label="World map">\n'
    '<title>World map</title>\n'
    '<desc>Made with Natural Earth (public domain). Equirectangular, '
    f'lon -180..180, lat {LAT_TOP}..{LAT_BOT}.</desc>\n'
    '<style>\n'
    # 국경선은 카드 배경색(#fff)과 같게 → 대륙 면이 선으로 갈라져 보인다
    '  .land{fill:#d8dce2;stroke:#fff;stroke-width:.45;'
    'stroke-linejoin:round;vector-effect:non-scaling-stroke}\n'
    '</style>\n'
    f'<path class="land" fill-rule="evenodd" d="{"".join(parts)}"/>\n'
    '</svg>\n'
)
open('world-map.svg', 'w', encoding='utf-8').write(svg)
print(f'viewBox 0 0 {W:g} {H:g}  |  rings kept {kept} / dropped {dropped}  |  '
      f'{len(svg)/1024:.1f} KB')
