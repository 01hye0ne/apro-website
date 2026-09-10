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


def loose(text):
    """정규화된 글에서, 원본의 빈칸·줄바꿈·<br> 을 허용하는 무늬를 만든다"""
    lines = [l for l in text.split("\n")]
    outs = []
    for line in lines:
        toks = [re.escape(t) for t in line.split(" ") if t]
        outs.append(r"\s*".join(toks) if toks else "")
    return r"\s*(?:<br\s*/?>)\s*".join(outs)


def esc_html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def apply_one(src, el, cur, new, kind):
    """(바뀐 원본, 알림) — 못 바꾸면 원본 그대로 돌려준다"""
    if kind == "alt":
        pat = re.compile(r'alt="' + loose(cur) + r'"')
        hits = list(pat.finditer(src))
        if len(hits) != 1:
            return src, "대체글 자리를 %d 곳에서 찾았다" % len(hits)
        a, b = hits[0].span()
        return src[:a] + 'alt="' + esc_html(new) + '"' + src[b:], None

    tag = el.tag
    body = loose(cur)
    pat = re.compile(r"(<" + tag + r"\b[^>]*>)(\s*" + body + r"\s*)(</" + tag + r">)")
    hits = list(pat.finditer(src))
    if not hits:
        return src, "글을 원본에서 못 찾았다"
    if len(hits) > 1:
        # 같은 글이 여러 곳이면 lxml 이 알려 준 줄에 가장 가까운 것을 고른다
        want = el.sourceline or 1
        hits.sort(key=lambda m: abs(src.count("\n", 0, m.start()) + 1 - want))
    m = hits[0]
    fill = "<br />".join(esc_html(p) for p in new.split("\n"))
    return src[:m.start(2)] + fill + src[m.end(2):], None


def read_book(path=BOOK):
    """엑셀을 줄 목록으로 읽고, 묶음이 하나만 채워졌으면 나머지에도 옮겨 준다"""
    wb = load_workbook(path)
    all_rows = []
    for sheet, key in SHEETS.items():
        if sheet not in wb.sheetnames:
            continue
        for row in wb[sheet].iter_rows(min_row=2, values_only=True):
            n, sec, role, kind, grp, cur, new, note, loc = (list(row) + [None] * 9)[:9]
            if not loc:
                continue
            xp, _, nk = str(loc).partition("|")
            all_rows.append({
                "key": key, "sheet": sheet, "n": n, "role": role, "grp": grp,
                "cur": str(cur or "").replace("\r", "").strip(),
                "new": str(new).replace("\r", "").strip() if norm(new) else "",
                "xp": xp, "nk": nk or "text"})

    # 같은 묶음에서 채운 줄이 딱 하나면 그 글을 나머지에도 얹는다
    box = {}
    for r in all_rows:
        if r["grp"]:
            box.setdefault(r["grp"], []).append(r)
    for g, rows in box.items():
        filled = {x["new"] for x in rows if x["new"]}
        if len(filled) != 1:
            if len(filled) > 1:
                print("  ~ 묶음 %s — 서로 다른 글이 %d 개라 각자 그대로 넣는다" % (g, len(filled)))
            continue
        word = filled.pop()
        for x in rows:
            if not x["new"]:
                x["new"] = word
                print("  + 묶음 %s — %s %s 에도 같이 넣는다" % (g, x["sheet"], x["n"]))
    return [r for r in all_rows if r["new"]]


def run(dry=True, only=None):
    jobs = {}
    for r in read_book():
        if only and r["sheet"] != only:
            continue
        jobs.setdefault(r["key"], []).append(
            {"n": r["n"], "sheet": r["sheet"], "role": r["role"], "cur": r["cur"],
             "raw_new": r["new"], "xp": r["xp"], "nk": r["nk"]})

    for key, rows in jobs.items():
        path = "apro-gray/business-%s-a1.html" % key
        src = io.open(path, encoding="utf-8", newline="").read().replace("\r\n", "\n")
        tree = LH.parse(io.StringIO(src))
        ok = bad = 0
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
        print("%-8s 넣음 %d, 못 넣음 %d" % (key, ok, bad))
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
