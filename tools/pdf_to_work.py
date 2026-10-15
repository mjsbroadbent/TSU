"""Turn a typeset PDF of a long work into the reader's text file.

    python3 tools/pdf_to_work.py WORK.pdf library/works/<slug>/text.md [--italic word ...]

Uses `pdftotext -layout`. A line indented by 3+ spaces starts a paragraph; a
centred line like "IV. St. Janyl" is a chapter heading; "⁂" is a scene break;
lone page numbers are dropped. The output is plain markdown-ish text:
"## heading", blank-line separated paragraphs, "* * *" for breaks and
*italics* for the words given with --italic (pdftotext loses italics).
Check the result by eye; front matter (title page) is skipped up to the
first heading.
"""
import re
import subprocess
import sys


def convert(pdf, italics=()):
    raw = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
    lines = raw.replace("\f", "\n").split("\n")
    blocks, cur = [], None   # blocks: ("h", text) / ("p", text) / ("br",)
    started = False
    prev_kind = "h"
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if re.fullmatch(r"\d{1,4}", s):               # page number
            continue
        indent = len(ln) - len(ln.lstrip(" "))
        if re.fullmatch(r"[IVXLC]+\.\s+.+", s) and indent >= 8:
            if cur: blocks.append(("p", cur)); cur = None
            blocks.append(("h", s)); started = True; prev_kind = "h"
            continue
        if not started:
            continue
        if s in ("⁂", "***", "* * *", "⁂⁂"):
            if cur: blocks.append(("p", cur)); cur = None
            blocks.append(("br",)); prev_kind = "br"
            continue
        if cur is None or indent >= 3:
            if cur: blocks.append(("p", cur))
            cur = s
        else:
            cur = cur + s if cur.endswith("-") else cur + " " + s
        prev_kind = "p"
    if cur:
        blocks.append(("p", cur))
    out = []
    for b in blocks:
        if b[0] == "h":
            out.append("## " + b[1])
        elif b[0] == "br":
            out.append("* * *")
        else:
            t = b[1]
            for w in sorted(italics, key=len, reverse=True):
                t = re.sub(r"(?<![\w*])" + re.escape(w) + r"(?![\w*])", "*" + w + "*", t)
            out.append(t)
    return "\n\n".join(out) + "\n"


if __name__ == "__main__":
    args = sys.argv[1:]
    it = []
    if "--italic" in args:
        i = args.index("--italic")
        it, args = args[i + 1:], args[:i]
    pdf, dest = args
    text = convert(pdf, it)
    open(dest, "w", encoding="utf-8").write(text)
    print(dest, len(text.split()), "words")
