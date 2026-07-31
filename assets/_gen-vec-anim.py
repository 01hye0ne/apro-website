#!/usr/bin/env python3
"""픽토그램 SVG 에 trim path(선 그려지기) 애니메이션을 심는다

    python _gen-vec-anim.py                 # vec-*.svg 전부
    python _gen-vec-anim.py vec-smart.svg   # 지정한 파일만
    python _gen-vec-anim.py --strip         # 애니메이션을 걷어내고 원본 상태로

사업영역 페이지가 픽토그램을 <img> 로 불러오기 때문에 페이지의 CSS/JS 는 SVG 안에
닿지 못한다. 그래서 애니메이션을 SVG 파일 안에 심는다 — <img> 로 써도 선언적
애니메이션(CSS)은 그대로 재생된다(스크립트만 차단된다).

원리는 After Effects 의 trim path 와 같다. 도형마다 제 둘레 길이만큼 점선 간격을
주고(stroke-dasharray) 그만큼 밀어 둔 뒤(stroke-dashoffset) 0 으로 당기면 선이
그려지는 것처럼 보인다. 길이는 도형마다 다르므로 여기서 계산해 박아 넣는다.

  · 시작 순서 : 아래 → 위. 두 픽토그램 모두 바닥선이 있어서, 바닥이 먼저 그어지고
                구조물이 올라오는 순서가 자연스럽다.
  · 지속 시간 : 길이에 비례(160 units/s), 0.45~1.25s 로 자른다. 짧은 선이 순간이동
                하듯 튀지 않고, 긴 선이 혼자 늘어지지도 않는다.
  · 전체 길이 : 도형이 몇 개든 스태거 구간을 1.05s 로 고정한다. 선이 99개인 스마트
                제조와 49개인 반도체가 따로 놀지 않고 네 패널이 같이 끝난다.
                전체는 LEAD_IN + STAGGER + DUR_MAX ≈ 2.45s.

다시 실행해도 안전하다 — 심어 둔 것을 먼저 걷어내고 새로 넣는다.

주의: .svg 파일은 XML 파서로 읽히므로 값 없는 속성(data-draw)이나 깨진 태그가
하나라도 있으면 이미지 전체가 렌더되지 않는다. 마지막에 XML 파싱으로 검증한다.
"""
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).parent

SPEED = 160.0        # units/sec — 선 길이를 지속 시간으로 바꾸는 비율
DUR_MIN, DUR_MAX = 0.45, 1.25
STAGGER = 1.05       # 첫 도형과 마지막 도형의 시작 간격(도형 수와 무관하게 고정)
LEAD_IN = 0.15       # 페이지가 뜨고 숨 한 번 쉬고 시작

STYLE_ID = 'vec-draw'
SHAPES = ('rect', 'circle', 'line', 'path')

# 숨김 상태는 반드시 키프레임 안에만 둔다. stroke-dashoffset 을 속성으로 미리 밀어 두면
# 애니메이션이 돌지 않는 상황(감속 모션 설정, 인쇄, 미지원 환경)에서 그래픽이 통째로
# 사라진다 — 기본값은 '다 그려진 상태', 애니메이션이 있을 때만 --L 만큼 되감는다.
STYLE_BLOCK = """<style id="%s">
    @keyframes vecdraw{from{stroke-dashoffset:calc(var(--L) * 1px)}to{stroke-dashoffset:0}}
    @keyframes vecfade{from{opacity:0}to{opacity:1}}
    [data-draw="1"]{animation-name:vecdraw;animation-timing-function:cubic-bezier(.22,1,.36,1);animation-fill-mode:both}
    [data-fade="1"]{animation-name:vecfade;animation-timing-function:ease-out;animation-fill-mode:both}
    @media (prefers-reduced-motion:reduce){
      [data-draw="1"],[data-fade="1"]{animation:none}
    }
  </style>""" % STYLE_ID


def attrs(tag):
    """<rect x="1" y="2"/> → {'x':'1','y':'2'}"""
    return dict(re.findall(r'([\w:-]+)\s*=\s*"([^"]*)"', tag))


def num(a, key, default=0.0):
    try:
        return float(a.get(key, default))
    except ValueError:
        return default


CURVE_STEPS = 12   # 곡선 하나를 직선 몇 토막으로 볼지. 이 크기(≈250px)에선 이걸로 충분하다


def path_points(d):
    """경로를 꼭짓점 목록으로 편다. 곡선(C)은 잘게 쪼개 직선으로 근사한다 —
    길이는 애니메이션 속도를 정하는 데만 쓰이므로 소수점 오차는 보이지 않는다.
    (dasharray 는 실제 길이보다 조금 길어도 선이 다 그려진 뒤 잠깐 멈출 뿐이고,
     짧으면 끝이 잘리므로 근사는 넉넉한 쪽이 안전하다)"""
    pts, cur, start = [], [0.0, 0.0], None
    tokens = re.findall(r'([MLHVCSQTAZmlhvcsqtaz])([^MLHVCSQTAZmlhvcsqtaz]*)', d)
    for cmd, arg in tokens:
        vals = [float(v) for v in re.findall(r'-?\d*\.?\d+(?:[eE][-+]?\d+)?', arg)]
        up, rel = cmd.upper(), cmd.islower()
        if up == 'Z':
            if start:
                pts.append(list(start))
                cur = list(start)
            continue
        step = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'T': 2, 'A': 7}[up]
        for i in range(0, len(vals) - step + 1, step):
            seg = vals[i:i + step]
            if up in ('M', 'L', 'T'):
                nxt = ([cur[0] + seg[0], cur[1] + seg[1]] if rel else [seg[0], seg[1]])
            elif up == 'H':
                nxt = [cur[0] + seg[0] if rel else seg[0], cur[1]]
            elif up == 'V':
                nxt = [cur[0], cur[1] + seg[0] if rel else seg[0]]
            elif up == 'C':
                ox, oy = (cur if rel else [0.0, 0.0])
                p1 = (ox + seg[0], oy + seg[1])
                p2 = (ox + seg[2], oy + seg[3])
                nxt = [ox + seg[4], oy + seg[5]]
                for k in range(1, CURVE_STEPS + 1):
                    t, u = k / CURVE_STEPS, 1 - k / CURVE_STEPS
                    pts.append([
                        u**3 * cur[0] + 3*u*u*t * p1[0] + 3*u*t*t * p2[0] + t**3 * nxt[0],
                        u**3 * cur[1] + 3*u*u*t * p1[1] + 3*u*t*t * p2[1] + t**3 * nxt[1]])
                cur = nxt
                continue
            else:
                # S / Q / A — 끝점만 보고 직선으로 친다. 이 픽토그램들엔 나오지 않지만
                # 나중에 섞여 들어와도 길이를 0 으로 만들지는 않게 둔다
                nxt = ([cur[0] + seg[-2], cur[1] + seg[-1]] if rel else [seg[-2], seg[-1]])
            pts.append(list(nxt))
            cur = nxt
            if up == 'M':
                start = list(cur)   # Z 는 가장 가까운 M 으로 돌아간다(하위 경로마다 갱신)
    return pts


def measure(name, a):
    """(그려야 할 길이, 세로 위치) — 세로 위치는 아래→위 순서를 정하는 데만 쓴다"""
    if name == 'rect':
        w, h = num(a, 'width'), num(a, 'height')
        length, y = 2 * (w + h), num(a, 'y') + h / 2
    elif name == 'circle':
        length, y = 2 * math.pi * num(a, 'r'), num(a, 'cy')
    elif name == 'line':
        x1, y1 = num(a, 'x1'), num(a, 'y1')
        x2, y2 = num(a, 'x2'), num(a, 'y2')
        length, y = math.hypot(x2 - x1, y2 - y1), (y1 + y2) / 2
    else:
        pts = path_points(a.get('d', ''))
        length = sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
                     for i in range(len(pts) - 1))
        y = sum(p[1] for p in pts) / len(pts) if pts else 0.0

    # transform 의 세로 이동만 반영한다 — 순서를 정하는 값이라 이 정도면 충분하고,
    # 여기 쓰인 matrix 는 전부 뒤집기(±1)라서 길이는 변하지 않는다
    t = a.get('transform', '')
    m = re.search(r'matrix\(([^)]*)\)', t)
    if m:
        v = [float(x) for x in re.findall(r'-?\d*\.?\d+', m.group(1))]
        if len(v) == 6:
            y = v[3] * y + v[5]
    m = re.search(r'translate\(([^)]*)\)', t)
    if m:
        v = [float(x) for x in re.findall(r'-?\d*\.?\d+', m.group(1))]
        if len(v) == 2:
            y += v[1]
    return max(length, 1.0), y


def strip(text):
    """심어 둔 것을 걷어내 원본 상태로 되돌린다"""
    text = re.sub(r'\s*<style id="%s">.*?</style>' % STYLE_ID, '', text, flags=re.S)
    text = re.sub(r'\s+data-(?:draw|fade)="1"', '', text)
    text = re.sub(r'\s+stroke-dash(?:array|offset)="[^"]*"', '', text)
    text = re.sub(r'\s+style="(?:--L:[^;]*;)?animation-[^"]*"', '', text)
    return text


def hidden_ranges(text):
    """<mask>/<defs>/<clipPath> 안쪽 구간. 여기 도형은 그림이 아니라 다른 도형을
    오려 내는 틀이라 건드리면 안 된다 — 애니메이션을 걸면 마스크가 깨진다"""
    spans = []
    for tag in ('mask', 'defs', 'clipPath'):
        for m in re.finditer(r'<%s\b.*?</%s>' % (tag, tag), text, flags=re.S):
            spans.append((m.start(), m.end()))
    return spans


def build(text):
    text = strip(text)
    skip = hidden_ranges(text)
    tags = [m for m in re.finditer(r'<(%s)\b[^>]*?/?>' % '|'.join(SHAPES), text)
            if not any(s <= m.start() < e for s, e in skip)]
    if not tags:
        return text, 0

    info = []
    for m in tags:
        a = attrs(m.group(0))
        length, y = measure(m.group(1), a)
        drawable = a.get('stroke') not in (None, 'none')
        info.append({'m': m, 'len': length, 'y': y, 'draw': drawable})

    # 아래에서 위로. 같은 높이면 원본 순서를 지킨다
    order = sorted(range(len(info)), key=lambda i: (-info[i]['y'], i))
    step = STAGGER / max(len(order) - 1, 1)
    for rank, i in enumerate(order):
        info[i]['delay'] = LEAD_IN + rank * step

    out, cursor = [], 0
    for it in info:
        m = it['m']
        tag = m.group(0)
        add = ' data-draw="1"' if it['draw'] else ' data-fade="1"'
        pre = ''
        if it['draw']:
            L = round(it['len'], 1)
            # dasharray 만 속성으로 둔다 — 이 값 하나로는 도형이 그대로 다 보인다
            add += ' stroke-dasharray="%s"' % L
            pre = '--L:%s;' % L
            dur = min(max(it['len'] / SPEED, DUR_MIN), DUR_MAX)
        else:
            dur = DUR_MIN
        add += ' style="%sanimation-duration:%.2fs;animation-delay:%.2fs"' % (pre, dur, it['delay'])

        close = '/>' if tag.endswith('/>') else '>'
        out.append(text[cursor:m.start()])
        out.append(tag[:-len(close)].rstrip() + add + close)
        cursor = m.end()
    out.append(text[cursor:])
    text = ''.join(out)

    # <style> 은 여는 <svg> 바로 뒤에. 첫 도형 앞에 넣으면 그 도형이 <mask> 안에
    # 있을 때 <style> 이 마스크 안으로 들어가 버린다
    root = re.search(r'<svg\b[^>]*>', text)
    cut = root.end()
    text = text[:cut] + '\n  ' + STYLE_BLOCK + text[cut:]
    return text, len(info)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    files = [HERE / a for a in args] if args else sorted(HERE.glob('vec-*.svg'))
    undo = '--strip' in sys.argv

    for p in files:
        if not p.exists():
            print('  !! 없음: %s' % p.name)
            continue
        src = p.read_text(encoding='utf-8')
        if undo:
            out, n = strip(src), 0
        else:
            out, n = build(src)
        try:
            ET.fromstring(out)          # XML 이 깨지면 이미지가 통째로 안 뜬다
        except ET.ParseError as e:
            print('  !! %s : XML 오류 — 원본 유지 (%s)' % (p.name, e))
            continue
        p.write_text(out, encoding='utf-8')
        print('  %-18s %s  (%.1fKB)'
              % (p.name, '원본 복구' if undo else '도형 %d개' % n, len(out) / 1024))
    return 0


if __name__ == '__main__':
    sys.exit(main())
