# -*- coding: utf-8 -*-
"""채워 온 엑셀의 '변경 문구'를 페이지에 되돌려 넣는다.

원본 HTML 을 다시 뽑아 쓰지 않는다 — 손으로 짠 줄바꿈과 주석을 lxml 이
전부 새로 쓰면 페이지가 남의 것이 되기 때문이다. 자리는 lxml 로 찾고,
글자만 원본 글에서 찾아 바꾼다. 찾은 자리가 하나가 아니면 그 줄은
건드리지 않고 알린다.
"""
import io, os, re, sys
from lxml import html as LH
from openpyxl import load_workbook

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from copy_pull import chunk          # 뽑을 때와 똑같은 잣대로 견준다

SHEETS = {"스마트 제조": "smart", "에너지 솔루션": "energy",
          "인공지능 플랫폼": "ai", "화합물 전력 반도체": "semicon"}
BOOK = "content-export/04_사업영역_문구.xlsx"


def norm(s):
    return " ".join((s or "").split())


ENT = {"&": r"(?:&amp;|&)", "<": r"(?:&lt;|<)", ">": r"(?:&gt;|>)"}


def tok(t):
    """한 낱말을 무늬로 — & 는 원본에서 &amp; 로 적혀 있을 수 있다"""
    out = ""
    for ch in t:
        out += ENT[ch] if ch in ENT else re.escape(ch)
    return out


def loose(text):
    """정규화된 글에서, 원본의 빈칸·줄바꿈·<br> 을 허용하는 무늬를 만든다"""
    outs = []
    for line in text.split("\n"):
        toks = [tok(t) for t in line.split(" ") if t]
        outs.append(r"\s*".join(toks) if toks else "")
    return r"\s*(?:<br\s*/?>)\s*".join(outs)


def esc_html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


DEL = "삭제"


def find_one(src, el, cur):
    """이 원소를 원본 글에서 찾아 (여는 태그 시작, 속, 닫는 태그 끝) 을 준다"""
    pat = re.compile(r"(<" + el.tag + r"\b[^>]*>)(\s*" + loose(cur) + r"\s*)(</" + el.tag + r">)")
    hits = list(pat.finditer(src))
    if not hits:
        return None
    if len(hits) > 1:
        # 같은 글이 여러 곳이면 lxml 이 알려 준 줄에 가장 가까운 것을 고른다
        want = el.sourceline or 1
        hits.sort(key=lambda m: abs(src.count("\n", 0, m.start()) + 1 - want))
    return hits[0]


def cut_one(src, el, cur):
    """그 원소를 통째로 걷어낸다 — 앞뒤 빈칸과 빈 줄까지 같이 지운다"""
    m = find_one(src, el, cur)
    if not m:
        return src, "글을 원본에서 못 찾았다"
    a, b = m.start(), m.end()
    # 앞은 줄머리까지, 뒤는 줄끝 다음까지 — 그 사이에 다른 글이 없을 때만
    ls = src.rfind("\n", 0, a) + 1
    le = src.find("\n", b)
    le = len(src) if le < 0 else le + 1
    if not src[ls:a].strip() and not src[b:le].strip():
        return src[:ls] + src[le:], None
    return src[:a] + src[b:], None


def apply_one(src, el, cur, new, kind):
    """(바뀐 원본, 알림) — 못 바꾸면 원본 그대로 돌려준다"""
    if kind == "alt":
        pat = re.compile(r'alt="' + loose(cur) + r'"')
        hits = list(pat.finditer(src))
        if len(hits) != 1:
            return src, "대체글 자리를 %d 곳에서 찾았다" % len(hits)
        a, b = hits[0].span()
        return src[:a] + 'alt="' + esc_html(new) + '"' + src[b:], None

    m = find_one(src, el, cur)
    if not m:
        return src, "글을 원본에서 못 찾았다"
    fill = "<br />".join(esc_html(p) for p in new.split("\n"))
    return src[:m.start(2)] + fill + src[m.end(2):], None


def cell(s):
    return str(s).replace("\r", "").strip() if norm(s) else ""


def read_book(path=BOOK):
    """엑셀을 줄 목록으로 읽는다.

    열은 이름으로 찾는다 — 칸이 하나 늘어도 자리로 세다가 어긋나지 않게.
    같은 묶음에서 채운 줄이 딱 하나면 그 글을 나머지에도 옮겨 준다(한글·영문 따로).
    """
    wb = load_workbook(path)
    all_rows = []
    for sheet, key in SHEETS.items():
        if sheet not in wb.sheetnames:
            continue
        ws = wb[sheet]
        head = [str(c.value or "").strip() for c in ws[1]]

        def col(name, *alts):
            for cand in (name,) + alts:
                for i, h in enumerate(head):
                    if h.startswith(cand):
                        return i
            return None

        ix = {k: col(*v) for k, v in {
            "n": ("순번",), "role": ("자리",), "grp": ("묶음",),
            "cur": ("현재 문구",), "new": ("변경 문구",), "en": ("영문 문구",),
            "loc": ("자리표",)}.items()}
        if ix["loc"] is None:
            print("  ! %s — 자리표 열을 못 찾았다" % sheet)
            continue
        for row in ws.iter_rows(min_row=2, values_only=True):
            g = lambda k: row[ix[k]] if ix[k] is not None and ix[k] < len(row) else None
            loc = g("loc")
            if not loc:
                continue
            xp, _, nk = str(loc).partition("|")
            all_rows.append({
                "key": key, "sheet": sheet, "n": g("n"), "role": g("role"),
                "grp": g("grp"), "cur": cell(g("cur")), "new": cell(g("new")),
                "en": cell(g("en")), "xp": xp, "nk": nk or "text"})

    box = {}
    for r in all_rows:
        if r["grp"]:
            box.setdefault(r["grp"], []).append(r)
    for g, rows in box.items():
        for field, tag in (("new", "한글"), ("en", "영문")):
            filled = {x[field] for x in rows if x[field]}
            if len(filled) != 1:
                if len(filled) > 1:
                    print("  ~ 묶음 %s %s — 서로 다른 글이 %d 개라 각자 그대로 넣는다"
                          % (g, tag, len(filled)))
                continue
            word = filled.pop()
            for x in rows:
                if not x[field]:
                    x[field] = word
                    print("  + 묶음 %s %s — %s %s 에도 같이 넣는다"
                          % (g, tag, x["sheet"], x["n"]))
    return all_rows


EN_OUT = "content-export/data/business-a1-en.json"


def save_en(rows):
    """영문은 붙일 장이 아직 없다 — 자리표와 함께 따로 모아 둔다"""
    import json
    keep = {}
    for r in rows:
        if not r["en"]:
            continue
        keep.setdefault(r["key"], []).append(
            {"role": r["role"], "ko": r["new"] or r["cur"], "en": r["en"], "at": r["xp"]})
    if not keep:
        return
    io.open(EN_OUT, "w", encoding="utf-8", newline="\n").write(
        json.dumps(keep, ensure_ascii=False, indent=1))
    print("영문 %d 줄을 %s 에 모았다" % (sum(len(v) for v in keep.values()), EN_OUT))


def run(dry=True, only=None, hold=()):
    """hold 는 이번에는 건드리지 않을 (시트, 순번) 들 — 따로 의논할 줄을 미뤄 둔다"""
    book = read_book()
    if not dry:
        save_en(book)
    jobs = {}
    for r in book:
        if only and r["sheet"] != only:
            continue
        if not r["new"]:
            continue
        if (r["sheet"], r["n"]) in hold:
            print("  · %s %s — 미뤄 둔다" % (r["sheet"], r["n"]))
            continue
        jobs.setdefault(r["key"], []).append(
            {"n": r["n"], "sheet": r["sheet"], "role": r["role"], "cur": r["cur"],
             "raw_new": r["new"], "xp": r["xp"], "nk": r["nk"]})

    for key, rows in jobs.items():
        path = "apro-gray/business-%s-a1.html" % key
        src = io.open(path, encoding="utf-8", newline="").read().replace("\r\n", "\n")
        tree = LH.parse(io.StringIO(src))
        ok = bad = 0
        # 지우는 줄은 뒤로 미룬다 — 줄이 사라지면 남은 자리의 줄 번호가 흔들린다
        cuts = [j for j in rows if j["raw_new"] == DEL]
        rows = [j for j in rows if j["raw_new"] != DEL]
        for j in rows:
            found = tree.xpath(j["xp"])
            if not found:
                print("  ! %s %s — 자리표가 가리키는 곳이 없다" % (j["sheet"], j["n"]))
                bad += 1
                continue
            el = found[0]
            here = (el.get("alt") or "").strip() if j["nk"] == "alt" else chunk(el)
            if here != j["cur"]:
                print("  ! %s %s — 지금 페이지 글이 표와 다르다\n      표 : %s\n      페이지: %s"
                      % (j["sheet"], j["n"], j["cur"][:50], here[:50]))
                bad += 1
                continue
            new_src, err = apply_one(src, el, j["cur"], j["raw_new"], j["nk"])
            if err:
                print("  ! %s %s — %s" % (j["sheet"], j["n"], err))
                bad += 1
                continue
            src = new_src
            ok += 1
            print("  · %s %s %s → %s" % (j["sheet"], j["n"], j["cur"].replace(chr(10),"⏎")[:28],
                                         j["raw_new"].replace(chr(10),"⏎")[:28]))
        # 지우기 — 하나 지울 때마다 다시 읽는다(줄 번호가 밀리기 때문)
        gone = 0
        for j in cuts:
            tree = LH.parse(io.StringIO(src))
            found = tree.xpath(j["xp"])
            if not found:
                print("  ! %s %s — 지울 자리를 못 찾았다" % (j["sheet"], j["n"]))
                bad += 1
                continue
            el = found[0]
            here = (el.get("alt") or "").strip() if j["nk"] == "alt" else chunk(el)
            if here != j["cur"]:
                print("  ! %s %s — 지우려는 글이 페이지와 다르다" % (j["sheet"], j["n"]))
                bad += 1
                continue
            src, err = cut_one(src, el, j["cur"])
            if err:
                print("  ! %s %s — %s" % (j["sheet"], j["n"], err))
                bad += 1
                continue
            gone += 1
            print("  − %s %s 지움: %s" % (j["sheet"], j["n"], j["cur"][:40].replace(chr(10), "⏎")))

        print("%-8s 넣음 %d, 지움 %d, 못 한 것 %d" % (key, ok, gone, bad))
        if not dry:
            io.open(path, "w", encoding="utf-8", newline="\r\n").write(src)

        # 바꾼 글이 회색 사이트 다른 장에 아직 남아 있으면 알린다 — 소분류 이름이
        # 띠지 · 메가 메뉴 · 푸터에도 박혀 있어서, 한쪽만 고치면 어긋난다
        import glob, os
        for j in rows:
            if len(j["cur"]) < 3 or "\n" in j["cur"]:
                continue
            hit = []
            for f in sorted(glob.glob("apro-gray/*.html")):
                if os.path.basename(f).startswith("_"):
                    continue
                if j["cur"] in io.open(f, encoding="utf-8", newline="").read():
                    hit.append(os.path.basename(f))
            if hit:
                print("  ? '%s' 이(가) 아직 남아 있다: %s" % (j["cur"], ", ".join(hit)))


if __name__ == "__main__":
    run(dry="--write" not in sys.argv)
