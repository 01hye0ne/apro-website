# -*- coding: utf-8 -*-
"""홈(시안 C, apro-gray/index-c.html) 문구를 국문영문글정리.xlsx 에 '홈' 시트로 더한다.

사업영역 시트들은 그대로 두고(채워 둔 칸 보존) 홈 시트만 새로 만든다 — 이미 있으면 바꿔 끼운다.
열 · 색 · 자리표 형식은 copy_xlsx.py 와 같다. 같은 문구가 여러 자리에 있으면 한 줄로 합친다.
보도자료 기사 제목 · 날짜는 게시판 글이라 담지 않는다.
"""
import io, re, sys
from collections import OrderedDict
from lxml import html as LH
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from copy import copy

sys.stdout.reconfigure(encoding="utf-8")

SRC = "apro-gray/index-c.html"
OUT = "content-export/국문영문글정리.xlsx"
SHEET = "홈"

HEAD = ["순번", "섹션", "자리", "구분", "묶음", "현재 문구", "변경 문구", "영문 문구",
        "비고", "자리표(건드리지 마세요)"]
W = [6, 24, 16, 8, 6, 54, 54, 54, 20, 44]
HAN = re.compile(r"[가-힣ㄱ-ㆎ]")
CHROME = ("sf-gnb", "c-mega", "navover", "footer", "totop")


def cls(e):
    return set((e.get("class") or "").split())


def anc(e, *names):
    while e is not None:
        if cls(e) & set(names) or e.tag in ("header", "footer"):
            return True
        e = e.getparent()
    return False


def up(e, name):
    while e is not None:
        if name in cls(e):
            return e
        e = e.getparent()
    return None


def chunk(e):
    parts = [e.text or ""]
    for ch in e:
        if isinstance(ch.tag, str) and ch.tag == "br":
            parts.append(ch.tail or "")
        else:
            parts[-1] += (ch.text_content() or "") + (ch.tail or "")
    return "\n".join(" ".join(p.split()) for p in parts).strip()


def role(e):
    """(섹션, 자리, 구분) — 담지 않을 원소면 None"""
    t, c = e.tag, cls(e)
    if t in ("script", "style", "svg", "img"):
        return None
    if t == "h1" and "sr-only" in c:
        return ("히어로", "페이지 제목(화면 낭독기용)", "숨김글")
    if up(e, "v2banner") is not None:
        if t == "p" and "en" in c:  return ("히어로", "메인 문구", "문구")
        if t == "p" and "kor" in c: return ("히어로", "서브 문구", "문구")
        if "bt" in c:               return ("히어로", "하단 탭", "문구")
        return None
    if "hm-lbl" in c:
        sec = {"hm-who-t": "Who we are", "hm-news-t": "News"}.get(e.getparent().get("id"), "Business")
        return (sec, "섹션 라벨", "문구")
    if t == "h2" and "hm-ttl" in c:
        sec = {"hm-who-t": "Who we are", "hm-news-t": "News"}.get(e.get("id"), "Business")
        return (sec, "섹션 제목", "문구")
    card = up(e, "hm-card")
    if card is not None:
        if "nm" in c and up(e, "fold") is not None: return ("Business", "카드 이름", "문구")
        if t == "a" and e.getparent().tag == "h3":  return ("Business", "카드 이름", "문구")
        if t == "p" and "d" in c:                   return ("Business", "카드 설명", "문구")
        if t == "a" and e.getparent().tag == "li":  return ("Business", "소분류 링크", "문구")
        return None
    wv = up(e, "hm-wv")
    if wv is not None:
        if "no" in c:             return ("Who we are", "번호", "번호")
        if t == "h3":             return ("Who we are", "제목", "문구")
        if t == "p" and "d" in c: return ("Who we are", "문단", "문구")
        return None
    if up(e, "v2news") is not None:
        if "more" in c: return ("News", "더보기 단추", "문구")
        if "lb" in c:   return ("News", "목록 '자세히 보기'", "문구")
        return None   # 기사 제목 · 날짜는 게시판 글
    return None


def card_name(e):
    """사업영역 카드 · 히어로 탭의 영역 이름 — 섹션 칸에 어느 카드인지 적는다"""
    card = up(e, "hm-card")
    if card is not None:
        h = card.cssselect("h3 a")
        return h[0].text_content().strip() if h else ""
    wv = up(e, "hm-wv")
    if wv is not None:
        n = wv.cssselect(".hd .no")
        return n[0].text_content().strip() if n else ""
    return ""


def pull():
    tree = LH.parse(io.StringIO(io.open(SRC, encoding="utf-8", newline="").read()))
    body = tree.getroot().cssselect("body")[0]
    rows = OrderedDict()          # 문구(+구분) → 한 줄
    for e in body.iter():
        if not isinstance(e.tag, str) or anc(e, *CHROME):
            continue
        r = role(e)
        if not r:
            continue
        if e.tag == "h2" and "hm-ttl" in cls(e):
            txt = " ".join((e.text_content().replace(chunk(e.cssselect(".hm-lbl")[0]), "", 1)).split()) if e.cssselect(".hm-lbl") else chunk(e)
        else:
            txt = chunk(e)
        if not txt:
            continue
        sec, where, kind = r
        sub = card_name(e)
        label = sec + (" · " + sub if sub and where not in ("카드 이름",) else "")
        flat = " ".join(txt.split())          # 줄을 나눠 적은 같은 이름(카드 제목 '스마트⏎제조')도 한 줄로
        key = (flat, kind) if kind != "번호" else (flat, kind, sub)
        if key not in rows:
            rows[key] = {"text": txt, "kind": kind, "secs": [], "roles": [], "locs": [], "split": False}
        m = rows[key]
        if txt != m["text"]:
            m["split"] = True
        if label not in m["secs"]:
            m["secs"].append(label)
        if where not in m["roles"]:
            m["roles"].append(where)
        m["locs"].append(tree.getpath(e) + "|text")
    return list(rows.values())


def carry(prev):
    """앞 판 홈 시트에서 사람이 채운 칸(변경 · 영문 · 비고)을 현재 문구 기준으로 모은다"""
    keep = {}
    if not prev:
        return keep
    try:
        ws = load_workbook(prev)[SHEET]
    except (KeyError, FileNotFoundError):
        return keep
    for row in ws.iter_rows(min_row=2, values_only=True):
        cur = " ".join(str(row[5] or "").split())
        if not cur:
            continue
        auto_note = re.compile(r"^(같은 문구|카드 제목 자리|사업영역 세부 시트|GNB · 메가)")
        notes = [l for l in str(row[8] or "").split("\n") if l and not auto_note.match(l)]
        en = row[7]
        keep[cur] = {"new": row[6], "en": en if en and " ".join(str(en).split()) != cur else None,
                     "note": "\n".join(notes) or None}
    return keep


def build(prev=OUT):
    old = carry(prev)
    wb = load_workbook(OUT)
    if SHEET in wb.sheetnames:
        del wb[SHEET]
    ref = wb[wb.sheetnames[1]]                  # 사업영역 첫 시트에서 머리줄 모양을 빌린다
    ws = wb.create_sheet(SHEET, 1)              # 안내 바로 다음

    thin = Side(style="thin", color="D0D5DB")
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    yfill = PatternFill("solid", fgColor="FFF6D6")
    bfill = PatternFill("solid", fgColor="E8F1FB")
    gfill = PatternFill("solid", fgColor="F4F6F8")

    ws.append(HEAD)
    for i, w in enumerate(W, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for c, rc in zip(ws[1], ref[1]):
        c.font, c.fill, c.alignment, c.border = copy(rc.font), copy(rc.fill), copy(rc.alignment), copy(rc.border)
    ws.row_dimensions[1].height = 24

    rows = pull()
    for n, m in enumerate(rows, 1):
        t, kind = m["text"], m["kind"]
        notes = []
        if len(m["locs"]) > 1:
            notes.append("같은 문구 %d 곳 — 한 줄로 합침" % len(m["locs"]))
        if m.get("split"):
            notes.append("카드 제목 자리는 두 줄로 나눠 보입니다 — 줄 나눌 곳이 따로 있으면 비고에 적어 주세요")
        if "소분류 링크" in m["roles"]:
            notes.append("사업영역 세부 시트의 소분류 이름과 같은 글 — 한쪽을 바꾸면 함께 고칩니다")
        if "카드 이름" in m["roles"] or "하단 탭" in m["roles"] and t != "에이프로":
            notes.append("GNB · 메가 메뉴 · 푸터의 사업영역 이름도 함께 고칩니다")
        got = old.get(" ".join(t.split()), {})
        if got.get("note"):
            notes.append(got["note"])
        en = got.get("en")
        if not en and kind not in ("번호",) and not HAN.search(t):
            en = t                                   # 영문뿐인 줄은 미리 채운다
        ws.append([n, " · ".join(m["secs"]), " · ".join(m["roles"]), kind, None,
                   t, got.get("new"), en, "\n".join(notes) or None, "\n".join(m["locs"])])
        row = ws[ws.max_row]
        for c in row:
            c.border = bd
            c.alignment = Alignment(vertical="top", wrap_text=True)
            c.font = Font(size=10)
        row[5].fill = gfill
        if kind == "번호":
            row[6].fill = gfill
            row[7].fill = gfill
        else:
            row[6].fill = yfill
            row[7].fill = bfill
        row[9].font = Font(size=8, color="98A2B0")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = "A1:J%d" % ws.max_row

    # 안내 시트 끝에 홈 시트 설명을 더한다(한 번만)
    g = wb["안내"]
    mark = "홈 시트 (2026-10-07 추가)"
    if not any(c.value == mark for c in g["B"]):
        head_style = g["B3"]        # '이 파일이 담은 것' 머리
        body_style = g["B4"]
        r = g.max_row + 1
        for txt, st in [(mark, head_style),
                        ("홈(시안 C, index-c.html)의 문구입니다. 히어로 · Business · Who we are · News 순서로, 화면에 보이는 순서대로 담았습니다.", body_style),
                        ("채우는 법은 사업영역 시트와 같습니다 — 노란 칸에 한글, 파란 칸에 영문. 같은 문구가 여러 자리에 있으면(사업영역 이름이 히어로 탭 · 카드에 함께 있는 것 등) 한 줄로 합쳤습니다.", body_style),
                        ("보도자료 기사 제목 · 날짜는 게시판 글이라 넣지 않았습니다. 게시판에서 고칩니다.", body_style),
                        ("모든 시트가 시안 C 기준입니다(2026-10-07 다시 뽑음). 9 월 A-1 판에서 채운 영문 · 비고는 문구가 같은 줄로 옮겨 담았습니다.", body_style)]:
            c = g.cell(row=r, column=2, value=txt)
            c.font, c.alignment = copy(st.font), copy(st.alignment)
            r += 1
        r += 0
    wb.save(OUT)
    print("홈 시트 %d 줄" % len(rows))
    for m in rows:
        print(" ", m["kind"], "|", " · ".join(m["secs"]), "|", " · ".join(m["roles"]), "|", m["text"][:40].replace("\n", "⏎"))


if __name__ == "__main__":
    # 앞 판(채운 칸을 옮겨 올 파일)을 따로 줄 수 있다 — copy_xlsx.py 로 새로 만든 뒤에는 홈 시트가 없으므로
    build(sys.argv[1] if len(sys.argv) > 1 else OUT)
