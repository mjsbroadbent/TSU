"""Make the home-page slider banners (text baked into the image, like a real
university portal's promo slides) and the news/journal pictures.

    python3 tools/make_banners.py

Sources are in img/src/ (FLUX renders; cut-outs are on white). Output: img/banner_*.jpg
(1600x868) and img/mag_*.jpg. Deliberately a bit rough: hard cut-out edges, crowded
type, JPEG at quality 72, the way the press office's designer does it.
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "img" / "src"
OUT = ROOT / "img"
W, H = 1600, 868
NAVY, BLUE, BLUE2, ORANGE = (37, 81, 142), (42, 110, 203), (64, 140, 230), (248, 132, 55)
INTER = "/usr/share/fonts/opentype/inter/"


def F(weight, size):
    name = {"r": "Inter-Regular", "m": "Inter-Medium", "b": "Inter-Bold", "x": "Inter-ExtraBold", "k": "Inter-Black",
            "d": "InterDisplay-Bold", "dl": "InterDisplay-Light"}[weight]
    return ImageFont.truetype(f"{INTER}{name}.otf", size)


def img(name):
    return Image.open(SRC / name).convert("RGB") if (SRC / name).exists() else Image.open(OUT / name).convert("RGB")


def cutout(im, thresh=236, feather=0):
    """Rough white-background removal (flood from the corners)."""
    g = im.convert("L").point(lambda v: 255 if v >= thresh else 0)
    flood = Image.new("L", (im.width + 2, im.height + 2), 255)
    flood.paste(g, (1, 1))
    ImageDraw.floodfill(flood, (0, 0), 128)
    bg = flood.crop((1, 1, im.width + 1, im.height + 1)).point(lambda v: 255 if v == 128 else 0)
    a = ImageOps.invert(bg)
    if feather:
        a = a.filter(ImageFilter.GaussianBlur(feather))
    out = im.convert("RGBA")
    out.putalpha(a)
    return out.crop(a.getbbox())


def cover(im, size, focus=(0.5, 0.5)):
    return ImageOps.fit(im, size, Image.LANCZOS, centering=focus)


def rrect(d, box, r, fill):
    d.rounded_rectangle(box, radius=r, fill=fill)


def logo(canvas, xy, h=70, white=False):
    m = Image.open(SRC / "logo-mark.png").convert("RGBA")
    m = m.resize((round(m.width * h / m.height), h), Image.LANCZOS)
    if white:  # mark on a white tile, white lettering
        ImageDraw.Draw(canvas).rounded_rectangle((xy[0] - 8, xy[1] - 6, xy[0] + m.width + 8, xy[1] + h + 6), radius=8, fill="white")
    canvas.paste(m, xy, m)
    d = ImageDraw.Draw(canvas)
    col = (255, 255, 255) if white else NAVY
    d.text((xy[0] + m.width + 12, xy[1] + h * 0.18), "TALAS STATE", font=F("b", round(h * 0.3)), fill=col)
    d.text((xy[0] + m.width + 12, xy[1] + h * 0.52), "UNIVERSITY", font=F("b", round(h * 0.3)), fill=col)


def fake_qr(n=29, px=7, seed=3):
    rnd = random.Random(seed)
    im = Image.new("RGB", (n * px + 4 * px, n * px + 4 * px), "white")
    d = ImageDraw.Draw(im)
    o = 2 * px
    for y in range(n):
        for x in range(n):
            if rnd.random() < 0.48:
                d.rectangle((o + x * px, o + y * px, o + x * px + px - 1, o + y * px + px - 1), fill="black")
    for fx, fy in ((0, 0), (n - 7, 0), (0, n - 7)):
        X, Y = o + fx * px, o + fy * px
        d.rectangle((X, Y, X + 7 * px - 1, Y + 7 * px - 1), fill="black")
        d.rectangle((X + px, Y + px, X + 6 * px - 1, Y + 6 * px - 1), fill="white")
        d.rectangle((X + 2 * px, Y + 2 * px, X + 5 * px - 1, Y + 5 * px - 1), fill="black")
    return im


def save(im, name, q=72):
    im.convert("RGB").save(OUT / name, quality=q, optimize=True)
    print(name)


def banner_admission():
    c = Image.new("RGB", (W, H), (240, 244, 250))
    bld = cover(img("main_building.jpg"), (1100, H), (0.45, 0.5))
    mask = Image.new("L", (1100, H), 0)
    ImageDraw.Draw(mask).polygon([(170, 0), (1100, 0), (1100, H), (0, H)], fill=255)
    c.paste(bld, (W - 1100, 0), mask)
    d = ImageDraw.Draw(c, "RGBA")
    d.polygon([(0, 0), (720, 0), (560, H), (0, H)], fill=(255, 255, 255, 235))
    d.polygon([(0, H - 230), (380, H), (0, H)], fill=BLUE + (255,))
    d.polygon([(0, H - 150), (250, H), (0, H)], fill=BLUE2 + (255,))
    d.polygon([(W - 330, H), (W, H - 380), (W, H)], fill=ORANGE + (255,))
    d.polygon([(W - 230, H), (W, H - 250), (W, H)], fill=(255, 176, 90, 255))
    for i in range(6):  # the designer's dotted decoration
        for j in range(3):
            d.ellipse((60 + i * 16, 560 + j * 16, 65 + i * 16, 565 + j * 16), fill=BLUE + (200,))
    st = cutout(img("students_cut.png"))
    st = st.resize((round(st.width * 720 / st.height), 720), Image.LANCZOS)
    c.paste(st, (W - st.width - 120, H - st.height + 10), st)
    d.text((60, 70), "Talas State University", font=F("b", 58), fill=(20, 20, 20))
    d.text((60, 140), "Admissions Office 2027", font=F("b", 58), fill=(20, 20, 20))
    d.text((60, 250), "Apply for a Bachelor's degree at the", font=F("r", 30), fill=(40, 40, 40))
    d.text((60, 290), "oldest university of Irad!", font=F("r", 30), fill=(40, 40, 40))
    rrect(d, (60, 380, 400, 452), 14, ORANGE + (255,))
    d.text((230, 416), "Open", font=F("m", 30), fill="white", anchor="mm")
    d.text((60, 480), "Applications from 20 June 2027", font=F("m", 22), fill=NAVY)
    logo(c, (60, 560), 70)
    save(c, "banner_admission.jpg")


def banner_dorm():
    c = Image.new("RGB", (W, H), (18, 52, 110))
    d = ImageDraw.Draw(c, "RGBA")
    for i in range(H):  # cheap vertical gradient
        t = i / H
        d.line((0, i, W, i), fill=(int(18 + 20 * t), int(52 + 30 * t), int(110 + 60 * t)))
    side = cover(img("students.jpg"), (520, H), (0.3, 0.5))
    m2 = Image.new("L", side.size, 0); ImageDraw.Draw(m2).polygon([(120, 0), (520, 0), (520, H), (0, H)], fill=255)
    c.paste(side, (W - 520, 0), m2)
    room = cover(img("dorm.png"), (640, 460))
    m = Image.new("L", room.size, 0); ImageDraw.Draw(m).ellipse((0, 0, 640, 460), fill=255)
    c.paste(room, (690, 200), m)
    d.ellipse((686, 196, 1334, 664), outline=ORANGE + (255,), width=6)
    d.text((80, 70), "Dormitory accommodation help centre", font=F("m", 28), fill="white")
    rrect(d, (80, 130, 260, 196), 16, ORANGE + (255,))
    d.text((170, 163), "24/7", font=F("b", 40), fill="white", anchor="mm")
    d.text((80, 260), "DORMITORY", font=F("x", 76), fill="white")
    d.text((80, 345), "HELP CENTRE", font=F("x", 76), fill="white")
    qr = fake_qr()
    c.paste(qr.resize((170, 170), Image.NEAREST), (80, 520))
    for k, t in enumerate(("+996 (39) 2-31-40-44", "0 (555) 31-40-44", "University St. 12, Building 6")):
        y = 530 + k * 56
        d.ellipse((280, y, 316, y + 36), fill=(255, 255, 255, 60))
        d.ellipse((292, y + 12, 304, y + 24), fill="white")
        d.text((330, y), t, font=F("b" if k < 2 else "m", 30), fill="white")
    d.text((80, 780), "Places for 2026–27 are still available in Buildings 2 and 6", font=F("r", 24), fill=(200, 215, 240))
    save(c, "banner_dorm.jpg")


def banner_evening():
    c = Image.new("RGB", (W, H), (244, 245, 247))
    d = ImageDraw.Draw(c, "RGBA")
    d.ellipse((-300, -200, 700, 800), fill=(232, 236, 243, 255))
    d.text((80, 90), "EVENING COURSES", font=F("m", 26), fill=BLUE)
    d.text((80, 140), "GAIN NEW PROFESSIONAL", font=F("b", 64), fill=(35, 35, 35))
    d.text((80, 220), "SKILLS AFTER WORK", font=F("b", 64), fill=BLUE)
    d.text((80, 300), "IN TALAS", font=F("b", 64), fill=BLUE)
    rrect(d, (80, 430, 1000, 740), 20, (255, 255, 255, 255))
    d.text((110, 475), "Advantages of training", font=F("m", 26), fill=(40, 40, 40))
    items = [("Classes 18:30–20:30, Mon–Thu", (120, 540)), ("State certificate on completion", (120, 650)),
             ("Accounting, English, IT", (570, 540)), ("Enrolment until 1 November", (570, 650))]
    for t, (x, y) in items:
        rrect(d, (x, y, x + 56, y + 56), 12, BLUE + (40,))
        d.ellipse((x + 18, y + 18, x + 38, y + 38), outline=BLUE + (255,), width=4)
        d.text((x + 72, y + 6), t, font=F("r", 22), fill=(60, 60, 60))
    wm = cutout(img("woman_cut.png"))
    wm = wm.resize((round(wm.width * 820 / wm.height), 820), Image.LANCZOS)
    c.paste(wm, (W - wm.width - 80, H - wm.height), wm)
    logo(c, (80, 790), 52)
    save(c, "banner_evening.jpg")


def banner_archive():
    c = Image.new("RGB", (W, H), NAVY)
    rr = cover(img("reading_room.jpg"), (W, H)).filter(ImageFilter.GaussianBlur(2))
    c = Image.blend(c, rr, 0.35)
    d = ImageDraw.Draw(c, "RGBA")
    d.rectangle((0, 0, 820, H), fill=(14, 34, 70, 200))
    d.text((80, 110), "SCIENTIFIC LIBRARY", font=F("m", 26), fill=(255, 200, 150))
    d.text((80, 160), "DIGITAL", font=F("k", 104), fill="white")
    d.text((80, 270), "ARCHIVE", font=F("k", 104), fill="white")
    d.text((80, 420), "Read Aikokul Tursunbek kyzy's", font=F("r", 32), fill="white")
    d.text((80, 464), "“Twelve Kilometres” online — free", font=F("b", 32), fill="white")
    rrect(d, (80, 560, 420, 632), 14, ORANGE + (255,))
    d.text((250, 596), "Read now  →", font=F("m", 30), fill="white", anchor="mm")
    cov = Image.open(ROOT / "library/works/twelve-kilometres/cover.jpg").convert("RGBA").resize((380, 538), Image.LANCZOS)
    sh = Image.new("RGBA", (cov.width + 60, cov.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((30, 30, 30 + cov.width, 30 + cov.height), fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    sh.paste(cov, (20, 20), cov)
    sh = sh.rotate(-6, expand=True, resample=Image.BICUBIC)
    c.paste(sh, (1000, 120), sh)
    logo(c, (80, 740), 64, white=True)
    save(c, "banner_archive.jpg")


def banner_mascot():
    c = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(c, "RGBA")
    d.polygon([(0, 0), (W, 0), (W, 300), (0, 520)], fill=BLUE + (255,))
    d.polygon([(0, 520), (W, 300), (W, 360), (0, 580)], fill=ORANGE + (255,))
    d.text((80, 80), "STUDENT COUNCIL", font=F("m", 30), fill="white")
    d.text((80, 130), "ELECTIONS", font=F("k", 110), fill="white")
    d.text((80, 260), "20 OCTOBER 2026", font=F("b", 52), fill=(255, 220, 160))
    d.text((80, 640), "Vote in your faculty, 10:00–17:00.", font=F("m", 34), fill=(30, 30, 30))
    d.text((80, 690), "Ilbirs says: your voice matters!", font=F("r", 30), fill=(60, 60, 60))
    ms = cutout(img("mascot.png"))
    ms = ms.resize((round(ms.width * 800 / ms.height), 800), Image.LANCZOS)
    c.paste(ms, (W - ms.width - 140, H - ms.height), ms)
    logo(c, (80, 770), 64)
    save(c, "banner_council.jpg")


def magazines():
    """Cluttered collage covers for the journals block."""
    pics = ["lab_staff.png", "komuz.png", "dedication.png", "stage.png", "glacier.jpg", "archive.jpg", "graduation.jpg", "students.jpg"]
    specs = [("BULLETIN", "History series", "No. 3 (2026)", (32, 40, 64), [5, 6, 2]),
             ("BULLETIN", "Philology series", "No. 2 (2026)", (60, 30, 60), [1, 7, 3]),
             ("BULLETIN", "Natural sciences", "No. 2 (2026)", (25, 60, 52), [4, 0, 6]),
             ("TSU NEWS", "University newspaper", "September 2026", (40, 40, 40), [2, 3, 0, 7])]
    for k, (t, s, no, bg, ids) in enumerate(specs):
        c = Image.new("RGB", (600, 800), bg)
        d = ImageDraw.Draw(c)
        d.text((36, 30), "TALAS STATE UNIVERSITY", font=F("b", 18), fill=(220, 220, 220))
        d.text((36, 70), t, font=F("k", 76), fill="white")
        d.text((40, 160), s + "  •  " + no, font=F("m", 22), fill=(255, 200, 150))
        boxes = [(36, 220, 380, 470), (392, 220, 564, 470), (36, 482, 300, 760), (312, 482, 564, 760)]
        for b, i in zip(boxes, ids):
            p = cover(img(pics[i]), (b[2] - b[0], b[3] - b[1]))
            c.paste(p, b[:2])
            d.rectangle(b, outline="white", width=3)
        d.rectangle((36, 700, 300, 760), fill=(248, 132, 55))
        d.text((48, 712), "Read inside →", font=F("b", 24), fill="white")
        save(c, f"mag_{k + 1}.jpg", q=70)


def news_pics():
    for n in ("lab_staff", "stage", "dedication", "komuz"):
        im = img(n + ".png")
        im = im.resize((793, round(793 * im.height / im.width)), Image.LANCZOS)
        save(im, f"news_{n}.jpg", q=68)


if __name__ == "__main__":
    for fn in (banner_admission, banner_dorm, banner_evening, banner_archive, banner_mascot, magazines, news_pics):
        try:
            fn()
        except FileNotFoundError as ex:
            print("skip", fn.__name__, ex)
