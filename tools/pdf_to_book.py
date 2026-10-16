"""Turn a typeset book PDF (made with the Irad book template) into book.json for the reader.

    python3 tools/pdf_to_book.py BOOK.pdf library/works/<slug>/book.json

Reads `pdftohtml -xml`, which keeps italics, bold, positions and font sizes:
- the Contents page (a page whose heading is "Contents") gives the sections,
  their labels ("1".."12", "Coda" or none) and start pages;
- running heads (top of page) and page numbers (bottom) are dropped;
- a line indented past the text margin starts a paragraph; a centred "⁂" is a
  scene break; other centred or right-aligned lines become centred/right blocks;
- on each section's first page the big title and the spaced label are skipped,
  and the italic line under the title is kept as the section's subtitle.
Check the result by eye.
"""
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

LIG = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl"}


def inner(el):
    """Element content as HTML with <i>/<b> kept."""
    out = [(el.text or "")]
    for c in el:
        t = inner(c)
        if c.tag in ("i", "b"):
            out.append(f"<{c.tag}>{t}</{c.tag}>")
        else:
            out.append(t)
        out.append(c.tail or "")
    return "".join(out)


SUBDIGITS = {0x2080 + i: ord("0") + i for i in range(10)}   # the PDF's old-style figures come out as subscript digits


def clean(s):
    s = s.translate(SUBDIGITS)
    for a, b in LIG.items():
        s = s.replace(a, b)
    s = s.replace("&", "&amp;").replace("&amp;lt;", "&lt;")
    s = re.sub(r"[  ]{2,}", " ", s)
    s = s.replace("</i><i>", "").replace("</b><b>", "").replace("</i> <i>", " ")
    return s.strip()


def load(pdf):
    xml = subprocess.run(["pdftohtml", "-xml", "-i", "-q", "-stdout", pdf], capture_output=True, text=True, check=True).stdout
    xml = re.sub(r"<!DOCTYPE[^>]*>", "", xml)
    root = ET.fromstring(xml)
    sizes, pages = {}, []
    for p in root.iter("page"):
        for fs in p.iter("fontspec"):
            sizes[fs.get("id")] = int(fs.get("size"))
        els = []
        for t in p.iter("text"):
            els.append(dict(top=int(t.get("top")), left=int(t.get("left")), width=int(t.get("width")),
                            size=sizes.get(t.get("font"), 0), html=inner(t), plain="".join(t.itertext())))
        pages.append(dict(no=int(p.get("number")), height=int(p.get("height")), width=int(p.get("width")), els=els))
    return pages


def lines_of(page):
    els = [e for e in page["els"] if 50 < e["top"] < page["height"] - 60]
    els.sort(key=lambda e: (e["top"], e["left"]))
    groups = []
    for e in els:
        if groups and abs(groups[-1][0]["top"] - e["top"]) <= 3:
            groups[-1].append(e)
        else:
            groups.append([e])
    lines = []
    for g in groups:
        g.sort(key=lambda e: e["left"])
        L = dict(top=g[0]["top"], left=g[0]["left"], right=g[0]["left"] + g[0]["width"], size=g[0]["size"], html=g[0]["html"], plain=g[0]["plain"])
        for e in g[1:]:
            gap = " " if e["left"] > L["right"] + 3 and not L["plain"].endswith(" ") and not e["plain"].startswith(" ") else ""
            L["html"] += gap + e["html"]; L["plain"] += gap + e["plain"]
            L["right"] = max(L["right"], e["left"] + e["width"]); L["size"] = max(L["size"], e["size"])
        L["html"] = clean(L["html"]); L["plain"] = clean(L["plain"])
        lines.append(L)
    return lines


def contents(pages):
    for pg in pages:
        ls = lines_of(pg)
        if any(L["plain"].replace(" ", "") == "Contents" for L in ls):
            secs = []
            for L in ls:
                m = re.match(r"^(?:(\d+|Coda)\s+)?(.+?)\s+(\d+)$", L["plain"])
                if m and L["plain"].replace(" ", "") != "Contents":
                    secs.append(dict(label=m.group(1) or "", title=m.group(2).strip(), page=int(m.group(3))))
            return pg["no"], secs
    raise SystemExit("no Contents page")


def body_margin(pages):
    from collections import Counter
    c = Counter(L["left"] for pg in pages for L in lines_of(pg) if L["size"] == 16)
    return c.most_common(1)[0][0]


def convert(pdf):
    pages = load(pdf)
    cpage, secs = contents(pages)
    margin = body_margin(pages)
    last = pages[-1]["no"]
    for i, s in enumerate(secs):
        s["end"] = (secs[i + 1]["page"] - 1) if i + 1 < len(secs) else last - 1   # last page is the back cover
    out = []
    for s in secs:
        blocks, cur, sub = [], None, ""
        def flush():
            nonlocal cur
            if cur:
                blocks.append(cur)
            cur = None
        for pg in pages:
            if not (s["page"] <= pg["no"] <= s["end"]):
                continue
            ls = lines_of(pg)
            if pg["no"] == s["page"]:
                # drop the opening heading block: everything before the first body-size line
                first = next((k for k, L in enumerate(ls) if L["size"] == 16 and L["left"] in (margin, margin + 20)), len(ls))
                for L in ls[:first]:
                    if L["html"].startswith("<i>") and L["plain"] != s["title"]:
                        sub = re.sub(r"</?i>", "", L["html"])
                ls = ls[first:]
            for L in ls:
                pw = pg["width"]
                if L["plain"] in ("⁂", "***", "* * *"):
                    flush(); blocks.append(dict(k="brk")); continue
                indent = L["left"] - margin
                if L["size"] >= 20:
                    flush(); blocks.append(dict(k="h3", html=L["html"])); continue
                pw = pg["width"]
                all_i = re.fullmatch(r"(<i>[^<]*</i>\s*)+", L["html"]) is not None
                sym = abs((L["left"] - margin) - (pw - margin - L["right"])) <= 8 and indent >= 10
                if all_i and ((cur and cur["k"] == "quote" and L["top"] - cur["_top"] < 30) or (indent >= 10 and L["right"] - L["left"] > 250)):
                    if cur and cur["k"] == "quote" and L["top"] - cur["_top"] < 30:
                        cur["html"] = cur["html"] + (" " if not cur["html"].endswith("-") else "") + L["html"]; cur["_top"] = L["top"]
                    else:
                        flush(); cur = dict(k="quote", html=L["html"], _top=L["top"])
                    continue
                is_right = L["right"] > pw - margin - 20 and L["left"] > pw / 2 and indent > 40
                is_center = indent > 40 and not is_right
                if is_right or is_center:
                    k = "right" if is_right else "center"
                    if cur and cur["k"] == k and L["top"] - cur["_top"] < 40:
                        cur["html"] += "<br>" + L["html"]; cur["_top"] = L["top"]
                    else:
                        flush(); cur = dict(k=k, html=L["html"], _top=L["top"])
                    continue
                if cur is None or cur["k"] != "p" or indent >= 10:
                    flush(); cur = dict(k="p", html=L["html"], _top=L["top"])
                else:
                    h = cur["html"]
                    cur["html"] = (h + L["html"]) if h.endswith("-") else (h + " " + L["html"])
                    cur["_top"] = L["top"]
        flush()
        for b in blocks:
            b.pop("_top", None)
            if b["k"] == "quote":
                b["html"] = b["html"].replace("</i> <i>", " ").replace("</i><i>", "")
        out.append(dict(id=re.sub(r"[^a-z0-9]+", "-", s["title"].lower()).strip("-"), label=s["label"], title=s["title"],
                        subtitle=sub, page=s["page"], blocks=blocks))
    # front matter between title pages and the contents: dedication, epigraph
    front = []
    for pg in pages:
        if 1 < pg["no"] < cpage:
            ls = lines_of(pg)
            txt = " ".join(L["plain"] for L in ls)
            if ls and ("dedicat" in txt.lower() or txt.lower().startswith("for ") or "proverb" in txt.lower() or "—" in txt) and len(txt) < 400:
                front.append("<br>".join(L["html"] for L in ls))
    back = " ".join(L["html"] for L in lines_of(pages[-1]))
    return dict(front=front, sections=out, back_cover=back)


if __name__ == "__main__":
    pdf, dest = sys.argv[1:3]
    book = convert(pdf)
    json.dump(book, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n = sum(len(re.sub("<[^>]+>", "", b.get("html", "")).split()) for s in book["sections"] for b in s["blocks"])
    print(dest, len(book["sections"]), "sections,", n, "words")
