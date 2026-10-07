# -*- coding: utf-8 -*-
"""04_푸터_정책문서.xlsx → apro-gray/policy-c.js (푸터 '개인정보처리방침' · '이메일무단수집거부' 팝업 글).

엑셀의 한 행 = 문단 하나. 조제목은 조 머리, 소제목은 굵은 머리글, 본문은 문단, 목록은 글머리 줄로 옮긴다.
국문 · 영문을 함께 담는다(영문 장은 아직 없어 팝업은 국문만 쓴다). 엑셀을 고친 뒤 다시 돌리면 된다:
  python content-export/tools/policy_js.py
"""
import io, json, sys
from openpyxl import load_workbook

sys.stdout.reconfigure(encoding="utf-8")
SRC = "content-export/04_푸터_정책문서.xlsx"
OUT = "apro-gray/policy-c.js"
KIND = {"조제목": "h", "소제목": "s", "본문": "p", "목록": "li"}


def privacy(ws):
    """조항 · 조 제목 · 구분 · 순서 · 내용 — 조 단위로 묶는다(조항이 빈 첫 줄은 머리말)"""
    intro, arts, cur = [], [], None
    for row in ws.iter_rows(min_row=2, values_only=True):
        art, _title, kind, _n, text = row[:5]
        if not text:
            continue
        k = KIND.get(kind, "p")
        if not art:
            intro.append([k, str(text).strip()])
            continue
        if k == "h":
            cur = {"t": str(text).strip(), "b": []}
            arts.append(cur)
        elif cur is not None:
            cur["b"].append([k, str(text).strip()])
    return {"intro": intro, "arts": arts}


def email(ws, lang):
    out = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        lg, kind, _n, text = row[:4]
        if lg != lang or not text:
            continue
        out.append([KIND.get(kind, "p"), str(text).strip()])
    return {"intro": out, "arts": []}


def main():
    wb = load_workbook(SRC, read_only=True)
    data = {
        "privacy": {"ko": {"title": "개인정보처리방침", **privacy(wb["개인정보처리방침_국문"])},
                    "en": {"title": "Privacy Policy", **privacy(wb["개인정보처리방침_영문"])}},
        "email": {"ko": {"title": "이메일무단수집거부", **email(wb["이메일무단수집거부"], "한국어")},
                  "en": {"title": "Refusal of Unauthorized Email Collection", **email(wb["이메일무단수집거부"], "영문")}},
    }
    js = ("/* 푸터 정책 팝업 글 — content-export/tools/policy_js.py 가 04_푸터_정책문서.xlsx 에서 만든다. 손으로 고치지 말 것.\n"
          "   [종류, 글] — h 조 머리 · s 굵은 머리글 · p 문단 · li 글머리 줄 */\n"
          "window.APRO_POLICY = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(js)
    for k, v in data.items():
        print(k, "ko 조 %d · 머리말 %d" % (len(v["ko"]["arts"]), len(v["ko"]["intro"])),
              "| en 조 %d" % len(v["en"]["arts"]))


if __name__ == "__main__":
    main()
