# 그림 원본은 Figma "GT Diagram Kit (복제본)" Workspace 페이지에도 벡터로 들어 있다 — 큰 수정은 여기서, 손맛은 Figma 에서.
"""GT Diagram Kit(아이소메트릭) 말씨로 그리는 작은 SVG 도구.
좌표: x → 화면 오른쪽 아래, y → 화면 왼쪽 아래, z → 위. 보이는 면은 +x(오른쪽) · +y(왼쪽) · 윗면.
킷 규칙: 실루엣에만 굵은 진회색 선, 면은 위가 가장 밝은 3단 그라데이션."""
import math

C30, S30 = math.cos(math.pi / 6), 0.5
OUT = '#474c59'
# 킷 Light Style 1 면 색 (위 · 왼쪽(+y) · 오른쪽(+x))
LIGHT = dict(top=('#edf1fd', '#e1e5f1'), left=('#cad1e7', '#b4bdd8'), right=('#cfd8ef', '#d5dae9'))
# 킷 Deep(파랑) Style 1
DEEP = dict(top=('#88a7ff', '#a3bbff'), left=('#618aff', '#3261e4'), right=('#7394f3', '#7d9efc'), out='#3258c2')
BLUE, RED = '#3479ff', '#ed5b47'


class Iso:
    def __init__(self, s=40):
        self.s = s
        self.items = []      # (svg string)
        self.defs = {}
        self.pts = []

    def p(self, x, y, z):
        X = (x - y) * C30 * self.s
        Y = ((x + y) * S30 - z) * self.s
        self.pts.append((X, Y))
        return X, Y

    def path(self, pts3, close=True):
        q = [self.p(*a) for a in pts3]
        return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in q) + (' Z' if close else '')

    def grad(self, a, b, vertical=True):
        hit = self.__dict__.setdefault('_gc', {}).get((a, b, vertical))
        if hit: return hit
        key = f'g{len(self.defs)}'
        self._gc[(a, b, vertical)] = f'url(#{key})'
        x2, y2 = ('0', '1') if vertical else ('1', '0')
        self.defs[key] = (f'<linearGradient id="{key}" x1="0" y1="0" x2="{x2}" y2="{y2}">'
                          f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>')
        return f'url(#{key})'

    def box(self, x, y, z, dx, dy, dz, pal=LIGHT, out=OUT, sw=2.2, name=None, opacity=None, face_op=None):
        """속이 찬 상자 하나 — 세 면 칠 + 실루엣 외곽선(킷처럼 안쪽 모서리엔 선이 없다)"""
        g = []
        fo = f' fill-opacity="{face_op}"' if face_op is not None else ''
        X0, X1, Y0, Y1, Z0, Z1 = x, x + dx, y, y + dy, z, z + dz
        top = [(X0, Y0, Z1), (X1, Y0, Z1), (X1, Y1, Z1), (X0, Y1, Z1)]
        left = [(X0, Y1, Z0), (X1, Y1, Z0), (X1, Y1, Z1), (X0, Y1, Z1)]    # +y 면
        right = [(X1, Y0, Z0), (X1, Y1, Z0), (X1, Y1, Z1), (X1, Y0, Z1)]   # +x 면
        g.append(f'<path d="{self.path(left)}" fill="{self.grad(*pal["left"])}"{fo}/>')
        g.append(f'<path d="{self.path(right)}" fill="{self.grad(*pal["right"])}"{fo}/>')
        g.append(f'<path d="{self.path(top)}" fill="{self.grad(*pal["top"])}"{fo}/>')
        # 안쪽 모서리 — 아주 옅게
        g.append(f'<path d="{self.path([(X1, Y1, Z0), (X1, Y1, Z1), (X0, Y1, Z1)], False)} M{" L".join("%.1f %.1f" % self.p(*a) for a in [(X1, Y0, Z1), (X1, Y1, Z1)])}" '
                 f'fill="none" stroke="#ffffff" stroke-opacity=".75" stroke-width="{sw * .55:.1f}" stroke-linejoin="round"/>')
        sil = [(X0, Y0, Z1), (X1, Y0, Z1), (X1, Y0, Z0), (X1, Y1, Z0), (X0, Y1, Z0), (X0, Y1, Z1)]
        g.append(f'<path d="{self.path(sil)}" fill="none" stroke="{out}" stroke-width="{sw}" stroke-linejoin="round"/>')
        op = f' opacity="{opacity}"' if opacity is not None else ''
        nm = f' id="{name}"' if name else ''
        self.items.append(f'<g{nm}{op}>' + ''.join(g) + '</g>')

    def raw(self, s):
        self.items.append(s)

    def poly(self, pts3, fill='none', stroke=None, sw=1.5, extra=''):
        st = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"' if stroke else ''
        self.items.append(f'<path d="{self.path(pts3)}" fill="{fill}"{st}{extra}/>')

    def line(self, a, b, stroke, sw=1.5, extra=''):
        (x1, y1), (x2, y2) = self.p(*a), self.p(*b)
        self.items.append(f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"{extra}/>')

    def arrow(self, a, b, color, sw=7, head=None, extra=''):
        """킷 Basics Arrows — 굵은 선 + 끝 세모(화면 평면에서)"""
        (x1, y1), (x2, y2) = self.p(*a), self.p(*b)
        ang = math.atan2(y2 - y1, x2 - x1)
        hl = head or sw * 2.6
        hw = hl * .62
        bx, by = x2 - hl * math.cos(ang), y2 - hl * math.sin(ang)
        nx, ny = -math.sin(ang), math.cos(ang)
        self.items.append(
            f'<g{extra}><path d="M{x1:.1f} {y1:.1f} L{bx + hl * .2 * math.cos(ang):.1f} {by + hl * .2 * math.sin(ang):.1f}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" fill="none"/>'
            f'<path d="M{x2:.1f} {y2:.1f} L{bx + nx * hw:.1f} {by + ny * hw:.1f} L{bx - nx * hw:.1f} {by - ny * hw:.1f} Z" fill="{color}" stroke="{color}" stroke-width="{sw * .35:.1f}" stroke-linejoin="round"/></g>')

    def svg(self, size=600, pad=36, bg=None):
        xs = [a for a, _ in self.pts]
        ys = [b for _, b in self.pts]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        w, h = x1 - x0, y1 - y0
        k = (size - 2 * pad) / max(w, h)
        tx = pad + ((size - 2 * pad) - w * k) / 2 - x0 * k
        ty = pad + ((size - 2 * pad) - h * k) / 2 - y0 * k
        body = ''.join(self.items)
        b = f'<rect width="{size}" height="{size}" fill="{bg}"/>' if bg else ''
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}" fill="none">'
                f'<defs>{"".join(self.defs.values())}</defs>{b}'
                f'<g transform="translate({tx:.1f} {ty:.1f}) scale({k:.4f})">{body}</g></svg>')


def ribbon(g, x0, x1, y, z, hw, fill, head=True, hl=0.9, opacity=1, plane='y'):
    """세로 평면(y=상수)에 눕힌 넓은 화살표 — x0 → x1. hw 는 띠 반폭(z 방향)"""
    if head:
        xb = x1 - hl
        pts = [(x0, y, z - hw), (xb, y, z - hw), (xb, y, z - hw * 2.1), (x1, y, z),
               (xb, y, z + hw * 2.1), (xb, y, z + hw), (x0, y, z + hw)]
    else:
        pts = [(x0, y, z - hw), (x1, y, z - hw), (x1, y, z + hw), (x0, y, z + hw)]
    op = f' fill-opacity="{opacity}"' if opacity != 1 else ''
    g.poly(pts, fill=fill, extra=op)


def ribbon3(g, a, b, wv, hw, fill, hl=0.9, opacity=1, hw2=2.1):
    """3차원 넓은 화살표 a → b, 띠 폭 방향 wv(단위 벡터)"""
    ax, ay, az = a; bx, by, bz = b
    L = ((bx - ax) ** 2 + (by - ay) ** 2 + (bz - az) ** 2) ** .5
    d = ((bx - ax) / L, (by - ay) / L, (bz - az) / L)
    cb = (bx - d[0] * hl, by - d[1] * hl, bz - d[2] * hl)
    off = lambda p, k: (p[0] + wv[0] * k, p[1] + wv[1] * k, p[2] + wv[2] * k)
    pts = [off(a, -hw), off(cb, -hw), off(cb, -hw * hw2), b, off(cb, hw * hw2), off(cb, hw), off(a, hw)]
    op = f' fill-opacity="{opacity}"' if opacity != 1 else ''
    g.poly(pts, fill=fill, extra=op)


def plane(g, origin, axis, body):
    """면 위 2차원 그림 — origin(3차원)에서 u 는 axis('x' 또는 y') 방향, w 는 아래(-z). 단위는 3차원 단위"""
    X, Y = g.p(*origin)
    s = g.s
    if axis == 'x':
        m = (C30 * s, S30 * s, 0, s)
    else:
        m = (-C30 * s, S30 * s, 0, s)
    g.items.append(f'<g transform="matrix({m[0]:.3f} {m[1]:.3f} {m[2]:.3f} {m[3]:.3f} {X:.2f} {Y:.2f})">{body}</g>')
