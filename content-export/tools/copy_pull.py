# -*- coding: utf-8 -*-
"""사업영역 세부 네 장(A-1)의 문구를 자리와 함께 뽑는다.

한 줄 = 화면에 보이는 문구 한 덩이. <br> 로 나뉜 줄은 한 덩이로 묶고
줄바꿈은 \n 으로 남긴다 — 되돌려 넣을 때 그대로 <br> 로 되살린다.
자리표는 lxml 의 xpath 라, 문구를 넣을 때 그 자리를 정확히 찾는다.

담는 원소는 '잎'만이다 — 자식 중에 또 자리가 있으면 그 그릇은 버린다.
그래야 같은 글이 겹쳐 나오지 않는다.
"""
import io, json, sys
from lxml import html as LH

sys.stdout.reconfigure(encoding="utf-8")

AREAS = [("smart", "스마트 제조"), ("energy", "에너지 솔루션"),
         ("ai", "인공지능 플랫폼"), ("semicon", "화합물 전력 반도체")]

CHROME = ("sf-gnb", "sf-mega", "sf-scrim", "footer", "navover", "bhop", "sf-ticker")


def cls(el):
    return set((el.get("class") or "").split())


def anc(el, *names):
    cur = el
    want = set(names)
    while cur is not None:
        if cls(cur) & want:
            return True
        cur = cur.getparent()
    return False


def pcls(el):
    p = el.getparent()
    return cls(p) if p is not None else set()


def role(el):
    """문구 한 덩이를 담는 잎이면 사람이 읽는 이름을 돌려준다"""
    t, c = el.tag, cls(el)

    if t == "img":
        if anc(el, "sf-introfig"): return "개요 그림 대체글"
        if anc(el, "sf-prod"):     return "제품 사진 대체글"
        if anc(el, "sf-figstack"): return "그림 대체글"
        return None

    # ── 히어로 · 개요 ──
    if anc(el, "sf-herocap"):
        if "ko" in c: return "히어로 제목(한글)"
        if "en" in c: return "히어로 제목(영문)"
        return None
    if "a" in c and "sf-lead" in pcls(el): return "개요 리드 1"
    if "b" in c and "sf-lead" in pcls(el): return "개요 리드 2"
    if t == "p" and anc(el, "sf-cards"):   return "개요 카드"

    # ── 좌측 인덱스 ──
    if anc(el, "sf-rail"):
        if t == "span" and "hd" in pcls(el):
            return "인덱스 그룹 번호" if el.getprevious() is None else "인덱스 그룹 이름"
        if t == "a": return "인덱스 항목"
        return None

    # ── 제품 카드(에너지 03) ──
    if anc(el, "sf-prod"):
        if t == "b" and "lbl" in pcls(el):  return "제품 이름"
        if t == "b" and "use" in pcls(el):  return "제품 용도 제목"
        if t == "span" and "use" in pcls(el): return "제품 용도 설명"
        if anc(el, "sf-feat"):
            if "k" in c: return "제품 특징 항목"
            if "d" in c: return "제품 특징 설명"
        return None

    # ── 제품 머리(에너지 03) ──
    if anc(el, "sf-phead"):
        if "sf-tag" in c:               return "머리 번호"
        if t == "h2":                   return "소분류 제목"
        if "lead" in c:                 return "소분류 리드"
        if "ttl" in c and anc(el, "sf-cert"): return "인증 제목"
        if t == "li" and anc(el, "sf-cert"):  return "인증 항목"
        return None

    # ── 그림 칸 ──
    if anc(el, "sf-figstack"):
        if t == "span" and "sf-ph" in pcls(el): return "그림 자리표시 문구"
        if anc(el, "sf-cnt"):
            if t == "b" and "cap" in pcls(el):    return "사진 설명 제목"
            if t == "span" and "cap" in pcls(el): return "사진 설명 본문"
        return None
    if "sf-tag" in c and anc(el, "sf-figcol"): return "장 번호"

    # ── 장 본문 ──
    if anc(el, "sf-sec"):
        if "nm" in c and anc(el, "sf-picks"): return "제품 단추 이름"
        if anc(el, "sf-num"):
            if t == "b":    return "번호 목록 번호"
            if t == "span": return "번호 목록 항목"
            return None
        if anc(el, "sf-apps"):
            if t == "b":    return "적용처 번호"
            if t == "span": return "적용처 항목"
            return None
        if anc(el, "sf-dl"):
            if "k" in c: return "표 왼쪽"
            if "d" in c: return "표 오른쪽"
            return None
        if t == "h2":   return "장 제목"
        if "en" in c:   return "장 영문 제목"
        if "cat" in c:  return "소분류 이름"
        if t == "p" and anc(el, "sf-body"):
            return "본문(예정)" if "tbd" in c else "본문"
        if t == "p" and anc(el, "sf-texts"): return "장 보조 문구"
        return None

    return None


def chunk(el):
    """<br> 로 나뉜 줄을 \n 으로 이어 한 덩이로 만든다"""
    parts = [(el.text or "")]
    for ch in el:
        if isinstance(ch.tag, str) and ch.tag == "br":
            parts.append(ch.tail or "")
        else:
            parts[-1] += (ch.text_content() or "") + (ch.tail or "")
    return "\n".join(" ".join(p.split()) for p in parts).strip()


def pull(path):
    tree = LH.parse(io.StringIO(io.open(path, encoding="utf-8", newline="").read()))
    body = tree.getroot().cssselect("body")[0]

    keep = []
    for el in body.iter():
        if not isinstance(el.tag, str) or el.tag in ("script", "style", "svg"):
            continue
        if anc(el, *CHROME):
            continue
        if role(el):
            keep.append(el)

    # 그릇은 버린다 — 자손 중에 또 자리가 있으면 그 원소는 담지 않는다
    kept = set(keep)
    leaf = [el for el in keep
            if not any(d in kept for d in el.iterdescendants() if isinstance(d.tag, str))]

    rows = []
    for el in leaf:
        if el.tag == "img":
            txt, kind = (el.get("alt") or "").strip(), "alt"
        else:
            txt, kind = chunk(el), "text"
        if not txt:
            continue
        sec, cur = "", el
        while cur is not None:
            if "sf-sec" in cls(cur):
                sec = cur.get("id") or ""
                break
            cur = cur.getparent()
        rows.append({"sec": sec, "role": role(el), "text": txt,
                     "xp": tree.getpath(el), "kind": kind})
    return rows


if __name__ == "__main__":
    out = {}
    for key, name in AREAS:
        rows = pull("apro-gray/business-%s-a1.html" % key)
        out[key] = rows
        print("%-8s %3d 덩이" % (key, len(rows)))
    io.open("copy_rows.json", "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print()
    for key in ("smart", "energy"):
        print("=== %s ===" % key)
        for r in out[key][:6]:
            print("  %-8s %-14s %s" % (r["sec"], r["role"], r["text"][:60].replace("\n", "⏎")))
