# -*- coding: utf-8 -*-
"""뽑아 둔 문구를 채워 넣기 좋은 엑셀 한 권으로 묶는다."""
import io, json, os, re, sys
from collections import Counter
from lxml import html as LH
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from copy_pull import pull, AREAS

OUT = "content-export/04_사업영역_문구.xlsx"

# ── 자리 이름 → 구분 ────────────────────────────────────────────────────
KIND = {
    "장 번호": "번호", "머리 번호": "번호", "인덱스 그룹 번호": "번호",
    "번호 목록 번호": "번호", "적용처 번호": "번호",
    "개요 그림 대체글": "대체글", "그림 대체글": "대체글", "제품 사진 대체글": "대체글",
    "그림 자리표시 문구": "자리표시", "본문(예정)": "자리표시",
}

HEAD = ["순번", "섹션", "자리", "구분", "묶음", "현재 문구", "변경 문구", "영문 문구",
        "비고", "자리표(건드리지 마세요)"]
W = [6, 24, 16, 8, 6, 54, 54, 54, 20, 44]

HAN = re.compile(r"[가-힣ㄱ-ㆎ]")


def rail_map(path):
    """왼쪽 인덱스에서 '01-1 공정 프로세스 맵' 꼬리표를 만든다"""
    doc = LH.fromstring(io.open(path, encoding="utf-8", newline="").read())
    out = {}
    for grp in doc.cssselect("nav.sf-rail div.sf-grp"):
        hd = grp.cssselect("p.hd span")
        num = (hd[0].text or "").strip() if hd else ""
        for a in grp.cssselect("a"):
            sid = (a.get("href") or "").lstrip("#")
            nm = " ".join((a.text_content() or "").split())
            tail = sid.replace("sf", "")
            out[sid] = "%s %s" % (tail, nm) if nm else tail
    return out


def build():
    wb = Workbook()
    guide = wb.active
    guide.title = "안내"

    thin = Side(style="thin", color="D0D5DB")
    bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    hfill = PatternFill("solid", fgColor="1B2733")
    yfill = PatternFill("solid", fgColor="FFF6D6")
    bfill = PatternFill("solid", fgColor="E8F1FB")
    gfill = PatternFill("solid", fgColor="F4F6F8")

    # 같은 글자끼리 묶음 번호를 매긴다 — 한 곳만 채우면 나머지도 함께 바꿔 준다
    data = {}
    for key, name in AREAS:
        data[key] = pull("apro-gray/business-%s-a1.html" % key)
    tally = Counter()
    for rows in data.values():
        for r in rows:
            tally[r["text"]] += 1
    gid, gmap = 0, {}
    for rows in data.values():
        for r in rows:
            t = r["text"]
            if tally[t] > 1 and t not in gmap:
                gid += 1
                gmap[t] = gid

    total = 0
    for key, name in AREAS:
        ws = wb.create_sheet(name)
        rmap = rail_map("apro-gray/business-%s-a1.html" % key)
        ws.append(HEAD)
        for i, w in enumerate(W, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF", size=10)
            c.fill = hfill
            c.alignment = Alignment(vertical="center")
            c.border = bd
        ws.row_dimensions[1].height = 24

        n = 0
        for r in data[key]:
            n += 1
            total += 1
            sec = r["sec"]
            if sec:
                label = rmap.get(sec, sec)
            elif r["role"].startswith("히어로"):
                label = "히어로"
            elif r["role"].startswith("개요"):
                label = "개요"
            else:
                label = "좌측 인덱스"
            g = gmap.get(r["text"], "")
            kind = KIND.get(r["role"], "문구")
            note = "묶음 %d — 같은 문구 %d 곳" % (g, tally[r["text"]]) if g else ""
            # 이미 영문(또는 숫자·기호)뿐인 줄은 영문 칸을 미리 채워 둔다 —
            # 손볼 게 없으면 그대로 두면 된다. 묶음에 든 줄은 비워 둔다:
            # 미리 채워 두면 '한 줄만 채우면 나머지에도' 규칙과 부딪힌다
            en = r["text"] if not HAN.search(r["text"]) else None
            if kind == "번호" or g:
                en = None
            ws.append([n, label, r["role"], kind, g,
                       r["text"], None, en, note, r["xp"] + "|" + r["kind"]])
            row = ws[ws.max_row]
            for c in row:
                c.border = bd
                c.alignment = Alignment(vertical="top", wrap_text=True)
                c.font = Font(size=10)
            row[5].fill = gfill                     # 현재 문구
            if kind == "번호":
                row[6].fill = gfill                 # 번호는 손댈 일이 없다
                row[7].fill = gfill
            else:
                row[6].fill = yfill                 # 변경 문구 — 한글을 쓴다
                row[7].fill = bfill                 # 영문 문구 — 영문을 쓴다
            row[9].font = Font(size=8, color="98A2B0")
            ws.row_dimensions[ws.max_row].height = None

        ws.freeze_panes = "A2"
        ws.auto_filter.ref = "A1:J%d" % ws.max_row
        ws.sheet_view.zoomScale = 100

    # ── 안내 ──
    guide.column_dimensions["A"].width = 4
    guide.column_dimensions["B"].width = 118
    lines = [
        ("t", "사업영역 세부(A-1) 문구 정리"),
        ("", ""),
        ("h", "이 파일이 담은 것"),
        ("p", "지금 사업영역 세부 네 장(business-*-a1.html)에 들어가 있는 문구 전부입니다. 시트가 사업영역이고, "
              "시트 안에서 섹션 순서대로, 화면에 보이는 순서대로 늘어놓았습니다. 모두 %d 줄입니다." % total),
        ("p", "GNB · 메가 메뉴 · 푸터 · 전체 메뉴처럼 모든 장이 함께 쓰는 문구는 넣지 않았습니다. "
              "히어로 아래 흐르는 띠지도 넣지 않았습니다 — 좌측 인덱스와 같은 이름이라 그쪽만 고치면 함께 바뀝니다."),
        ("", ""),
        ("h", "채우는 법"),
        ("p", "색 있는 두 칸에만 쓰시면 됩니다. 노란 칸에 한글, 파란 칸에 영문입니다. "
              "그대로 둘 줄은 비워 두세요 — 빈 칸은 '그대로'로 읽습니다."),
        ("p", "지우고 싶은 줄은 변경 문구에 '삭제'라고만 써 주세요. 줄을 지우지는 말아 주세요."),
        ("p", "줄바꿈이 필요하면 칸 안에서 Alt+Enter 로 줄을 나누시면 됩니다. 현재 문구에 이미 줄이 나뉜 것도 "
              "그 자리에 줄바꿈이 들어가 있다는 뜻입니다."),
        ("p", "비고 칸은 자유롭게 쓰셔도 됩니다 — 고민 중인 대안이나 저에게 남기는 말도 좋습니다."),
        ("", ""),
        ("h", "영문 문구 칸"),
        ("p", "영문 사이트에 쓸 글입니다. 지금 회색 사이트에는 영문 장이 아직 없어서, 채워 주신 영문은 "
              "바로 화면에 붙지 않습니다. 별도 파일로 모아 두고 영문 장을 만들 때 그대로 씁니다."),
        ("p", "이미 영문뿐인 줄(영문 제목, Grid Stabilization 같은 항목)은 미리 채워 두었습니다. "
              "손볼 게 없으면 그대로 두시면 됩니다."),
        ("p", "한글만 고치고 영문은 나중에 하셔도 됩니다. 두 칸은 서로 기다리지 않습니다."),
        ("", ""),
        ("h", "묶음 칸"),
        ("p", "같은 문구가 여러 곳에 있으면 같은 묶음 번호를 달아 두었습니다. 그중 한 줄만 채우면 나머지도 "
              "같이 바꿔 넣습니다. 한글과 영문 모두 그렇습니다."),
        ("p", "굳이 여러 번 쓰지 않으셔도 됩니다."),
        ("p", "소분류 이름을 바꾸시면 좌측 인덱스 · 띠지 · 메가 메뉴 · 푸터에 있는 같은 이름도 제가 함께 고칩니다."),
        ("", ""),
        ("h", "구분 칸"),
        ("p", "문구 — 읽는 글입니다. 대체글 — 눈이 아닌 화면 낭독기가 읽는 사진 설명입니다. "
              "번호 — 01, 02 같은 자리 번호로, 채울 칸을 회색으로 막아 두었습니다. 자리표시 — 아직 글이 안 들어온 자리입니다."),
        ("p", "대체글은 화면에 보이지 않지만 검색과 접근성에 쓰입니다. 손대지 않으셔도 제가 문구에 맞춰 다듬습니다."),
        ("", ""),
        ("h", "마지막 칸(자리표)"),
        ("p", "제가 그 문구를 페이지에서 찾는 데 쓰는 주소입니다. 지우거나 고치면 그 줄을 넣을 수 없습니다."),
        ("p", "돌려주실 때는 이 파일을 그대로 저장해서 주시면 됩니다. 시트 이름과 열 순서만 지켜 주세요."),
    ]
    for kind, txt in lines:
        guide.append([None, txt])
        c = guide.cell(row=guide.max_row, column=2)
        if kind == "t":
            c.font = Font(bold=True, size=16)
        elif kind == "h":
            c.font = Font(bold=True, size=11, color="2C5790")
        else:
            c.font = Font(size=10)
            c.alignment = Alignment(wrap_text=True, vertical="top")
        guide.row_dimensions[guide.max_row].height = 30 if kind == "p" else 22
    guide.sheet_view.showGridLines = False

    wb.save(OUT)
    print("썼다", OUT, total, "줄")


if __name__ == "__main__":
    build()
