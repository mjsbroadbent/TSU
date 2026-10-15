"""Build the Talas State University site (tsu.edu.ir.ad) from tools/ and data/.

    python3 tools/build.py

Writes every page as <dir>/index.html so URLs stay clean on GitHub Pages.
Library works live in library/works/<slug>/ (meta.json, text.md, the PDF);
each gets a record page and a reader at library/archive/<slug>/.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
WORKS = ROOT / "library" / "works"
e = html.escape
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]

# ---------------------------------------------------------------- navigation

MENU = [
    ("Admission", "admission/", [
        ("Undergraduate", "admission/#undergraduate"), ("Graduate (Master's)", "admission/#graduate"),
        ("PhD", "admission/#phd"), ("Tuition fees and grants", "admission/#fees"),
        ("Evening courses for adults", "admission/evening/"), ("Entrance thresholds 2026", "admission/#thresholds"),
        ("Applicant's guide", "admission/#guide"), ("For applicants from the diaspora", "admission/#diaspora")]),
    ("About us", "about/", [
        ("Talas State University", "about/"), ("Rector", "about/rector/"), ("History of the university", "about/history/"),
        ("Council of Elders (Aksakaldar keneshi)", "about/#elders"), ("Quality assurance", "about/#quality"),
        ("Alumni association", "about/#alumni"), ("Anti-corruption", "about/#anticorruption"),
        ("Scientific library", "library/")]),
    ("Research", "research/", [
        ("Institutes and departments", "research/"), ("Bulletin of Talas State University", "research/#bulletin"),
        ("Talas State University Press", "library/press/"), ("Institute of Sociology surveys", "research/#sociology"),
        ("Rabat-i-Safed excavation", "research/#archaeology"), ("Glaciology and the Manas observatory", "research/#glaciology")]),
    ("Faculties", "faculties/", None),
    ("For students", "students/", [
        ("Student life", "students/"), ("Timetables", "students/#timetables"), ("Dormitories", "students/#dorms"),
        ("Sport club and Universitet Talas", "students/#sport"), ("Career centre", "students/#career"),
        ("Student e-portal", "students/#portal")]),
    ("Library", "library/", [
        ("Scientific library", "library/"), ("Digital archive", "library/archive/"),
        ("TSU Press catalogue", "library/press/"), ("Opening hours and services", "library/#hours"),
        ("Ethnography sound archive", "library/#sound"), ("Theses and dissertations", "library/#theses")]),
    ("Contacts", "contacts/", None),
]

ICONS = {
    "entrant": '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21c1-4.5 4-7 8-7s7 2.5 8 7"/></svg>',
    "student": '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 10h5M7 14h8"/><circle cx="16.5" cy="10" r="1.5"/></svg>',
    "graduate": '<svg viewBox="0 0 24 24"><path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c3 2.5 9 2.5 12 0v-5"/></svg>',
    "employee": '<svg viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="13" rx="2"/><circle cx="12" cy="9" r="2.5"/><path d="M8 20h8M8 15c1-2 7-2 8 0"/></svg>',
    "courses": '<svg viewBox="0 0 24 24"><path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 3v4M17 5h4"/></svg>',
    "partner": '<svg viewBox="0 0 24 24"><circle cx="7" cy="8" r="3"/><circle cx="17" cy="8" r="3"/><path d="M2 20c.5-4 2.5-6 5-6s4.5 2 5 6M12 20c.5-4 2.5-6 5-6s4.5 2 5 6"/></svg>',
    "library": '<svg viewBox="0 0 24 24"><path d="M4 4h4v16H4zM10 4h4v16h-4zM16 5l3.5-1 3 15-3.5 1z"/></svg>',
    "archive": '<svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="5" rx="1"/><path d="M5 9v11h14V9M10 13h4"/></svg>',
    "book": '<svg viewBox="0 0 24 24"><path d="M3 5c3-1.3 6-1.3 9 .8 3-2.1 6-2.1 9-.8v14c-3-1.3-6-1.3-9 .8-3-2.1-6-2.1-9-.8z"/><path d="M12 6v14"/></svg>',
    "sound": '<svg viewBox="0 0 24 24"><path d="M3 10v4M7 7v10M11 4v16M15 8v8M19 11v2"/></svg>',
    "clock": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "media": '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="12" rx="2"/><path d="M8 21h8M10 9l5 2.5-5 2.5z"/></svg>',
    "people": '<svg viewBox="0 0 24 24"><circle cx="8" cy="8" r="3"/><circle cx="16" cy="9" r="2.5"/><path d="M2 20c.6-4 3-6 6-6s5.4 2 6 6M14 15c3-.6 6.5.6 7.5 5"/></svg>',
    "briefcase": '<svg viewBox="0 0 24 24"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5h6v2M3 12h18"/></svg>',
    "chart": '<svg viewBox="0 0 24 24"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg>',
    "globe": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/></svg>',
    "medal": '<svg viewBox="0 0 24 24"><path d="M8 3h8l-2 6h-4z"/><circle cx="12" cy="15" r="5"/><path d="M12 12.5l.9 1.8 2 .3-1.4 1.4.3 2-1.8-.9-1.8.9.3-2-1.4-1.4 2-.3z"/></svg>',
    "mountain": '<svg viewBox="0 0 24 24"><path d="M2 20l7-11 4 6 3-4 6 9z"/><path d="M8 10.5l1 1.5 1.2-1"/></svg>',
    "lang": '<svg viewBox="0 0 24 24"><path d="M3 5h10M8 3v2M5 5c1 4 4 7 7 8M11 5c-1 4-4 7-7 8"/><path d="M13 21l4-9 4 9M14.5 18h5"/></svg>',
}

WHO = [("entrant", "Entrant", "admission/"), ("student", "Student", "students/"),
       ("graduate", "Graduate", "about/#alumni"), ("employee", "Employee", "contacts/#staff"),
       ("courses", "Courses", "admission/evening/"), ("partner", "Business partner", "research/#partners")]


def page(title, body, *, base, active="", who="", description="", body_class="", scripts=""):
    menu = []
    for label, href, drop in MENU:
        sub = ""
        if drop:
            sub = '<ul class="drop">' + "".join(f'<li><a href="{base}{h}">{e(t)}</a></li>' for t, h in drop) + "</ul>"
        elif label == "Faculties":
            sub = '<ul class="drop">' + "".join(
                f'<li><a href="{base}faculties/{f["slug"]}/">{e(f["name"])}</a></li>' for f in FACULTIES) + "</ul>"
        on = ' class="on"' if href == active else ""
        menu.append(f'<li{on}><a href="{base}{href}">{e(label)}</a>{sub}</li>')
    who_links = "".join(
        f'<li><a href="{base}{h}"{" class=\"on\"" if k == who else ""}>{ICONS[k]}{e(t)}</a></li>' for k, t, h in WHO)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description or 'Talas State University (TSU), the oldest and largest university in Irad, founded in 1958.')}">
<link rel="icon" href="{base}assets/logo-mark.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}assets/tsu.css">
</head>
<body class="{body_class}" data-base="{base}">
<header class="top">
  <a class="top-logo" href="{base}"><img src="{base}assets/logo-mark.svg" alt=""><span>Talas State<br>University</span></a>
  <button class="burger top-tools" type="button" aria-label="Menu" style="display:none;border:0;background:none;align-items:center;padding:0 12px;font-size:22px;color:#25518e;cursor:pointer">&#9776;</button>
  <ul class="menu">{''.join(menu)}</ul>
  <div class="top-tools">
    <button type="button" class="eye" title="Version for the visually impaired" aria-label="Version for the visually impaired"><svg width="20" height="20" viewBox="0 0 24 24" fill="#25518e"><path d="M12 5C6.5 5 2.7 9.2 1.5 12c1.2 2.8 5 7 10.5 7s9.3-4.2 10.5-7C21.3 9.2 17.5 5 12 5zm0 11a4 4 0 110-8 4 4 0 010 8z"/></svg></button>
    <div class="lang"><button type="button" class="lang-btn">EN</button><span class="lang-note">Iradi and Russian versions are being updated</span></div>
    <button type="button" class="search" aria-label="Search"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/></svg></button>
  </div>
</header>
<form class="searchbar" action="{base}library/press/" method="get" role="search"><input name="q" placeholder="Search the site and the library catalogue" aria-label="Search"><button type="submit">Search</button></form>
<aside class="side">
  <p class="side-h">Information for:</p>
  <ul class="who">{who_links}</ul>
  <div class="side-foot">
    <a class="side-logo" href="{base}"><img src="{base}assets/logo-mark.svg" alt=""><b>Talas State<br>University</b></a>
    <div class="soc"><a class="tp" href="https://mjsbroadbent.github.io/tulpar/" title="TSU on Tulpar" rel="noopener">T</a><a href="https://iradone.com/" title="TSU on IradOne" rel="noopener">1</a><a href="mailto:info@tsu.edu.ir.ad" title="E-mail">@</a></div>
    <ul class="side-links">
      <li><a href="{base}about/">Talas State University</a></li>
      <li><a href="{base}sitemap/">Map of the site</a></li>
      <li><a href="{base}about/#quality">Quality assurance in education</a></li>
      <li><a href="{base}contacts/">Contacts</a></li>
      <li class="gap"><a href="{base}admission/#undergraduate">Undergraduate</a> &nbsp;<a href="{base}admission/#graduate">Graduate</a></li>
      <li><a href="{base}admission/#phd">PhD</a></li>
      <li class="gap"><a href="{base}admission/">Admissions Office</a></li>
      <li><a href="{base}students/#portal">Student e-portal</a></li>
      <li><a href="{base}library/">Scientific library</a></li>
    </ul>
    <p class="side-copy">© 1958–2026 Talas State University</p>
  </div>
</aside>
<main>
{body}
<footer class="foot">
  <div class="wrap">
    <div><h4>Talas State University</h4><p>Talas Mamlekettik Universiteti<br>12 University Street, Talas 724000, Irad<br>Admissions Office: +996-39-2-31-40-11<br>Rector's reception: +996-39-2-31-40-00<br>info@tsu.edu.ir.ad</p></div>
    <div><h4>Study</h4><ul><li><a href="{base}admission/">Admission</a></li><li><a href="{base}faculties/">Faculties</a></li><li><a href="{base}admission/evening/">Evening courses</a></li><li><a href="{base}students/">For students</a></li></ul></div>
    <div><h4>Science</h4><ul><li><a href="{base}research/">Research</a></li><li><a href="{base}library/">Scientific library</a></li><li><a href="{base}library/archive/">Digital archive</a></li><li><a href="{base}library/press/">TSU Press</a></li></ul></div>
    <div><h4>University</h4><ul><li><a href="{base}about/">About us</a></li><li><a href="{base}about/rector/">Rector</a></li><li><a href="{base}news/">News</a></li><li><a href="{base}contacts/">Contacts</a></li></ul></div>
  </div>
  <div class="foot-bottom">© 1958–2026 Talas State University. Materials may be reproduced with a link to tsu.edu.ir.ad. Part of the Irad worldbuilding project: Irad is a fictional country. See also <a href="https://irad.wiki/" style="color:#9fb0c6">the Irad wiki</a> and <a href="https://talasherald.com/" style="color:#9fb0c6">the Talas Herald</a>.</div>
</footer>
</main>
<button class="totop" type="button" onclick="window.scrollTo(0,0)"><span>&uarr;</span>Back to top</button>
<script src="{base}assets/tsu.js"></script>{scripts}
</body>
</html>
"""


def write(rel: str, text: str):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def fmt_date(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


def sec_t(title, href=None, base=""):
    t = f'<a href="{base}{href}">{e(title)}</a> <span class="arr">&#8599;</span>' if href else e(title)
    return f'<h2 class="sec-t">{t}</h2>'


def inner(base, crumbs, title, main_html, subnav=None):
    cr = " / ".join([f'<a href="{base}">Home</a>'] + [f'<a href="{base}{h}">{e(t)}</a>' if h else e(t) for t, h in crumbs])
    side = ""
    if subnav:
        side = '<nav class="card subnav"><h4>' + e(subnav[0]) + "</h4>" + "".join(
            f'<a href="{base}{h}">{e(t)}</a>' for t, h in subnav[1]) + "</nav>"
    return (f'<div class="wrap"><p class="crumbs">{cr}</p><h1 class="page-h">{e(title)}</h1>'
            f'<div class="inner"><div class="card inner-main">{main_html}</div><div>{side}</div></div></div>')


# ---------------------------------------------------------------- content data

FACULTIES = [
    dict(slug="history", name="Faculty of History", since=1958, dean="Prof. Asel Toktogulova",
         depts=["History of Irad", "World History", "Archaeology and Ethnology", "Archival Studies"],
         text="The faculty grew out of the department of history and philology with which the university opened in 1958. Its archaeologists run the university's excavation at the caravanserai of Rabat-i-Safed, and its archival studies programme trains staff for the ISEZ State Archive and the National Historical Museum."),
    dict(slug="philology", name="Faculty of Philology and Journalism", since=1958, dean="Assoc. Prof. Elnura Kadyrova",
         depts=["Iradi Language and Literature", "English Philology", "Russian Philology", "Journalism and Media"],
         text="Teaching in Iradi, English and Russian. The department of Iradi language and literature compiled the <i>Descriptive Grammar of the Iradi Language</i> (2023) and edits the literature series of the <i>Bulletin</i>. Journalism students do placements at the <i>Talas Herald</i> and IradOne."),
    dict(slug="arts", name="Faculty of Arts and Music", since=1994, dean="Prof. Kalys Ismailov",
         depts=["Iradi Traditional Music", "Performance and Composition", "Fine and Applied Arts"],
         text="Komuz, choor, kyl-kyiak and voice, alongside piano and composition. The faculty hosts the qualifying round of the national komuz contest each October and keeps a collection of instruments described in <i>Instruments of the Iradi Tradition</i> (TSU Press, 2010)."),
    dict(slug="physics-mathematics", name="Faculty of Physics, Mathematics and Computer Science", since=1958, dean="Prof. Ruslan Pak",
         depts=["Mathematics", "Physics", "Computer Science", "Applied Informatics"],
         text="One of the three founding faculties. Computer science has been taught since 1979; graduates of the department wrote some of Irad's first school software and, more recently, its most popular messaging app."),
    dict(slug="biology-chemistry", name="Faculty of Biology and Chemistry", since=1958, dean="Prof. Elmira Kasymova",
         depts=["Zoology", "Botany and Ecology", "Chemistry", "Biotechnology"],
         text="The department of zoology monitors the snow leopard and other wildlife of the Talas Alatau and the Chatkal and publishes the faunal checklists of Irad (birds, mammals, fishes, amphibians and reptiles)."),
    dict(slug="geography", name="Faculty of Geography and Earth Sciences", since=1964, dean="Prof. Bolot Kudaibergenov",
         depts=["Physical Geography", "Glaciology and Hydrology", "Geology and Seismology", "Cartography and GIS"],
         text="Glaciologists of the faculty work with the Manas Peak Glaciological Observatory on the inventory of the 268 glaciers of the Iradi Talas basin; its seismologists study the Talas–Fergana Fault."),
    dict(slug="agriculture", name="Faculty of Agriculture", since=1958, dean="Prof. Asan Moldobaev",
         depts=["Agronomy", "Animal Husbandry", "Agricultural Economics", "Irrigation and Land Reclamation"],
         text="A founding faculty. Since the territorial period it has worked with the agribusiness companies of the Talas valley on maize, potatoes, sugar beet and cattle, and with the herding cooperatives of the tribal regions."),
    dict(slug="veterinary", name="Faculty of Veterinary Medicine", since=1971, dean="Prof. Kubanych Sydykov",
         depts=["Veterinary Medicine", "Equine Science", "Veterinary Genetics"],
         text="The faculty carries out DNA parentage testing for the Akyel and Chongtor studbooks together with the Talas Veterinary Research Center, and runs the university's teaching stables."),
    dict(slug="medicine", name="Faculty of Medicine", since=1981, dean="Prof. Aibek Mamatov",
         depts=["General Medicine", "Paediatrics", "Public Health", "Nursing"],
         text="Opened in 1981 with the Talas Regional Hospital Medical Complex as its teaching hospital. Six-year programme in general medicine, taught in English and Iradi."),
    dict(slug="law", name="Faculty of Law", since=1965, dean="Prof. Aizada Bekova",
         depts=["Constitutional and Administrative Law", "Civil and Commercial Law", "Criminal Law and Procedure", "Customary Law (Adat) and Legal History"],
         text="The faculty teaches the law of the ISEZ alongside the customary law of the tribal regions, a course unique in the region. Its legal clinic gives free advice to residents of Talas every Saturday."),
    dict(slug="economics", name="Faculty of Economics and Management", since=1967, dean="Prof. Gulmira Toktosunova",
         depts=["Economics", "Finance and Banking", "Accounting and Audit", "Management and Tourism"],
         text="Economists of the faculty are regular commentators in the <i>Talas Herald</i> on prices, remittances and the som. The faculty runs the evening courses in accounting for adults."),
]

NEWS = [
    dict(slug="digital-archive-bazaar-chubar", date="2026-10-15", img="img/reading_room.jpg", tag="Library",
         title="Digital archive opens with Aikokul Tursunbek kyzy's “Twelve Kilometres”",
         lead="The Scientific Library has opened its Digital Archive to readers, beginning with Aikokul Tursunbek kyzy's stories of the partition years.",
         body=["The Scientific Library of Talas State University has opened a Digital Archive for long-form works that are hard to find in print: literary works, memoirs, theses and the reports of the university's institutes. Every item can be read online in the library's reader or downloaded as a PDF.",
               "The first works in the archive are Aikokul Tursunbek kyzy's <a href=\"../../library/archive/twelve-kilometres/\"><i>Twelve Kilometres</i></a> (<i>On Eki Chakyrym</i>), twelve stories and a coda from the partition years of 2006–2009, published by Arsha Books in Iradi in 2015 and in Aidana Mukash kyzy's English translation in 2016, and the author's <a href=\"../../library/archive/bazaar-chubar/\">revised and expanded “Bazaar Chubar”</a> (2019), the story of a walnut buyer's daughter in Bazar-Korgon in the autumn of 2007.",
               "“A university library should keep what its own country writes about itself,” said the director of the library. Authors and families who wish to deposit a work may write to library@tsu.edu.ir.ad."]),
    dict(slug="rabat-i-safed-coins", date="2026-10-10", img="img/archive.jpg", tag="Research",
         title="Rabat-i-Safed coins go to Nurzhan for testing",
         lead="Kara-Khanid coins found by the university's expedition will be analysed at the Nurzhan Polytechnic Institute before publication.",
         body=["The group of worn 10th- and 11th-century Kara-Khanid coins found in September at the caravanserai of Rabat-i-Safed will be sent to the materials laboratory of the Nurzhan Polytechnic Institute to establish what they are made of. Dr Marat Imanaliev, who led the season, said early tests suggest a very high lead content.",
               "The finds will be deposited with the National Historical Museum of Irad once the study is published. Less than a fifth of the site has been excavated. Dr Imanaliev will give an open lecture on the season on 21 October.",
               "Read the <a href=\"https://talasherald.com/news/2026-10-10-rabat-i-safed-coins-to-be-tested-in-nurzhan-as-museum-asks-for-custody.html\">report in the Talas Herald</a>."]),
    dict(slug="evening-courses-2026", date="2026-10-01", img="img/students.jpg", tag="Admission",
         title="Evening courses for adults: enrolment open until 1 November",
         lead="Three-month courses in accounting and taxes, English (A1–B2) and computer literacy, with a state certificate.",
         body=["Enrolment is open for the autumn intake of the university's evening courses for adults. Classes run from 18:30 to 20:30 on weekdays in Building 3, from 9 November to 12 February.",
               "Courses: accounting and taxes; English, levels A1 to B2; computer literacy. Fee: IS 4,800 for the course. Applications at Building 3, room 104, or by telephone 2-31-40-17.",
               "See <a href=\"../../admission/evening/\">Evening courses</a>."]),
    dict(slug="komuz-contest-qualifying", date="2026-10-08", img="img/main_building.jpg", tag="Culture",
         title="Faculty of Arts and Music hosts komuz contest qualifying on 22 October",
         lead="Players in three age groups will play in the faculty's concert hall; the gala is on 24 October.",
         body=["The qualifying round of the national komuz contest will take place on 22 October in the concert hall of the Faculty of Arts and Music. Every entrant plays one küü from Aigul Choro kyzy's published transcriptions and one piece of free choice.",
               "The winners perform at the gala on Saturday 24 October, shown the same evening by IradOne. Students of the faculty will act as accompanists and stewards."]),
    dict(slug="first-year-2026", date="2026-09-01", img="img/graduation.jpg", tag="University",
         title="4,120 first-year students begin the 2026–27 academic year",
         lead="The rector opened the year on the steps of the main building; 1,350 students study on state grants.",
         body=["Talas State University welcomed 4,120 first-year students on 1 September, 1,350 of them on state grants. The largest intakes were in economics, medicine and computer science.",
               "The rector reminded students that the main building, damaged by shelling in 1992, was restored by the students and staff who studied in it."]),
    dict(slug="glacier-season-2026", date="2026-09-18", img="img/glacier.jpg", tag="Research",
         title="Glaciology field season ends on the Manas massif",
         lead="Faculty of Geography researchers completed this year's mass-balance measurements with the Manas Peak observatory.",
         body=["A team from the Faculty of Geography and Earth Sciences completed the 2026 mass-balance measurements on the glaciers of the Manas massif. Prof. Nazira Isaeva said the summer had been one of the warmest in the observatory's record.",
               "The data feed the inventory of the 268 glaciers of the Iradi Talas basin, whose melt provides a third or more of the August flow of the high tributaries."]),
]

EVENTS = [
    ("Open lecture: Rabat-i-Safed, the 2026 season", "Main building, Hall 214", "October 21, 15:00"),
    ("National komuz contest: qualifying round", "Faculty of Arts and Music, concert hall", "October 22"),
    ("Evening courses: last day of enrolment", "Building 3, room 104", "November 1"),
    ("Women's League: Universitet Talas v Tulpar", "TSU Stadium", "October 25, 14:00"),
]


# ---------------------------------------------------------------- library helpers

def load_works():
    out = []
    for d in sorted(WORKS.iterdir()):
        if (d / "meta.json").exists():
            m = json.loads((d / "meta.json").read_text(encoding="utf-8"))
            m["dir"] = d
            m["book"] = json.loads((d / "book.json").read_text(encoding="utf-8")) if (d / "book.json").exists() else None
            out.append(m)
    out.sort(key=lambda m: m.get("added", ""), reverse=True)
    return out


def inline(t: str) -> str:
    t = e(t, quote=False)
    return re.sub(r"\*([^*\n]+)\*", r"<i>\1</i>", t)


def render_text(md: str):
    parts, toc = [], []
    for block in md.strip().split("\n\n"):
        b = block.strip()
        if b.startswith("## "):
            h = b[3:]
            hid = "ch-" + str(len(toc) + 1)
            toc.append((hid, h))
            parts.append(f'<h2 id="{hid}">{inline(h)}</h2>')
        elif b == "* * *":
            parts.append('<p class="brk" aria-hidden="true">⁂</p>')
        elif b.startswith("@dateline "):
            parts.append(f'<p class="dl-line">{inline(b[10:])}</p>')
        else:
            parts.append(f"<p>{inline(b)}</p>")
    return "\n".join(parts), toc


def citation(m):
    url = f'https://tsu.edu.ir.ad/library/archive/{e(m["slug"])}/'
    if m.get("book"):
        year = re.findall(r"\d{4}", m.get("published", ""))
        tr = f' Translated by {e(m["translator"])}.' if m.get("translator") else ""
        sub = f' ({e(m["subtitle"])})' if m.get("subtitle") else ""
        return (f'{e(m["author_sort"])}. <i>{e(m["title"])}{sub}</i>.{tr} {e(m.get("publisher", ""))}, {year[-1] if year else ""}. '
                f'Talas State University Scientific Library, Digital Archive, {e(m["accession"])}. {url}')
    part = f' In <i>{e(m["part_of"])}</i>.' if m.get("part_of") else ""
    return (f'{e(m["author_sort"])}. \u201c{e(m["title"])}.\u201d{part} '
            f'Talas State University Scientific Library, Digital Archive, {e(m["accession"])}. {url}')


def w_cover(m, base=""):
    if m.get("cover"):
        return f'<div class="w-cover w-img"><img src="{base}library/works/{m["slug"]}/{m["cover"]}" alt="Cover of {e(m["title"])}" loading="lazy"></div>'
    return f'<div class="w-cover"><b>{e(m["title"])}</b><i>{e(m["author"])}</i></div>'


def by_line(m, sub=True):
    t = e(m["author"])
    if m.get("translator"):
        t += f' · translated by {e(m["translator"])}'
    if m.get("part_of"):
        t += f' · from <i>{e(m["part_of"])}</i>'
    elif m.get("subtitle") and sub:
        t += f' · <i>{e(m["subtitle"])}</i>'
    return t


# ---------------------------------------------------------------- pages

def home():
    b = ""
    slides = [("img/main_building.jpg", "Talas State University", "The oldest and largest university in Irad: eleven faculties, 18,400 students, since 1958.", "about/", "About the university"),
              ("img/reading_room.jpg", "The Digital Archive is open", "Read Aikokul Tursunbek kyzy's Twelve Kilometres and other long-form works online.", "library/archive/", "Go to the archive"),
              ("img/students.jpg", "Evening courses for adults", "Accounting, English and computer literacy. Enrolment until 1 November.", "admission/evening/", "Enrol"),
              ("img/glacier.jpg", "Science on the roof of Irad", "TSU glaciologists measure the glaciers of the Talas Alatau and the Manas massif.", "research/#glaciology", "Research at TSU")]
    sl = "".join(f'<div class="slide{" on" if i == 0 else ""}"><img src="{b}{img}" alt=""><div class="slide-cap"><h2>{e(t)}</h2><p>{e(p)}</p>'
                 f'<a class="btn" href="{b}{h}">{e(bt)} &#8599;</a></div></div>' for i, (img, t, p, h, bt) in enumerate(slides))
    hero = f'<section class="hero">{sl}<div class="dots"></div></section>'
    svc = [("TSU Portal", "students/#portal", "timetable, grades"), ("e-Library", "library/", "catalogue"), ("Digital archive", "library/archive/", "read online"),
           ("TSU Press", "library/press/", "132 titles"), ("Dormitory", "students/#dorms", "applications"), ("Career centre", "students/#career", "vacancies"),
           ("Bulletin", "research/#bulletin", "journal"), ("Webmail", "contacts/#staff", "staff")]
    services = (f'<section class="sec wrap">{sec_t("Internal services", "students/")}<div class="svc">'
                + "".join(f'<a href="{b}{h}">{e(t)}<small>{e(s)}</small></a>' for t, h, s in svc) + "</div></section>")
    n = NEWS
    def nc(x, big=False):
        return (f'<a class="card n-card{" big" if big else ""}" href="{b}news/{x["slug"]}/"><img src="{b}{x["img"]}" alt="" loading="lazy">'
                f'<div class="b"><time>{fmt_date(x["date"])}</time><h3>{e(x["title"])}</h3>' + (f'<p>{e(x["lead"])}</p>' if big else "") + "</div></a>")
    ev = "".join(f'<div class="ev-item"><h4>{e(t)}</h4><p><b>Location:</b> {e(l)}</p><p><b>Event dates:</b> {e(d)}</p></div>' for t, l, d in EVENTS)
    news = (f'<section class="sec wrap"><h2 class="sec-t"><a href="{b}news/">News</a> <span class="arr">&#8599;</span>'
            f'<span class="news-tabs"><span class="on">All</span><span>Science</span><span>Library</span><span>Students</span></span></h2>'
            f'<div class="news-grid"><div class="news-col">{nc(n[0], True)}</div><div class="news-col">{nc(n[1])}{nc(n[2])}{nc(n[3])}</div>'
            f'<div class="ev"><h3><a href="{b}news/">Events of the month</a> <span class="arr" style="color:#2a6ecb">&#8599;</span></h3>{ev}</div></div></section>')
    mags = [("#20385f", "Bulletin", "History series", "No. 3 (2026)", "The 1916 revolt in the northern valleys: new sources"),
            ("#5a2a4a", "Bulletin", "Philology series", "No. 2 (2026)", "Urban speech of Talas; a lexicon of walnut growers"),
            ("#1f5145", "Bulletin", "Natural sciences", "No. 2 (2026)", "Snow leopard camera traps, Chatkal 2025"),
            ("#3a3a3a", "TSU News", "University newspaper", "September 2026", "4,120 first-year students; the new library reader")]
    magz = (f'<section class="sec wrap">{sec_t("Journals and newspapers", "research/#bulletin")}<div class="mags">'
            + "".join(f'<a class="card mag" href="{b}research/#bulletin"><div class="mag-cover" style="background:{c}"><small>Talas State<br>University</small>'
                      f'<b>{e(t)}</b><i>{e(s)}</i><em>{e(no)}<br>{e(d)}</em></div><div class="b">{e(t)}: {e(s)}, {e(no)}</div></a>' for c, t, s, no, d in mags)
            + "</div></section>")
    g = [("briefcase", "Programmes in demand: medicine, computer science, economics and law"), ("medal", "1,350 state grants for first-year students each year"),
         ("lang", "Study in Iradi and English, with Russian as an elective"), ("chart", "Credit system: build your own study plan"),
         ("globe", "Exchanges with partner universities in the United States, Turkey and Korea"), ("mountain", "Field practice from the Kyzylkum fringe to the Manas glaciers")]
    guide = (f'<section class="sec"><div class="wrap">{sec_t("Undergraduate applicant’s guide", "admission/#guide")}</div>'
             f'<div class="guide">' + "".join(f'<div class="g-item"><span class="g-ico">{ICONS[i]}</span><span>{e(t)}</span></div>' for i, t in g[:2])
             + f'<div class="guide-photo"><img src="{b}img/graduation.jpg" alt=""></div>'
             + "".join(f'<div class="g-item"><span class="g-ico">{ICONS[i]}</span><span>{e(t)}</span></div>' for i, t in g[2:]) + "</div></section>")
    progs = [("Bachelor's programmes", ["64 educational programmes", "1,350 state grants a year", "Credit system of study", "Iradi and English tracks"], "admission/#undergraduate"),
             ("Master's programmes", ["38 educational programmes", "Research and professional tracks", "Joint supervision with partner universities"], "admission/#graduate"),
             ("Doctoral studies (PhD)", ["21 educational programmes", "Active research in 4 institutes", "Two supervisors, one from abroad", "Publication in the <i>Bulletin</i>"], "admission/#phd")]
    pr = (f'<section class="sec wrap">{sec_t("Entrance to Talas State University", "admission/")}<div class="progs">'
          + "".join(f'<div class="card prog"><h3>{e(t)}</h3><ul>' + "".join(f"<li>{x}</li>" for x in li) + f'</ul><a class="btn btn-w" href="{b}{h}">Learn more &#8599;</a></div>' for t, li, h in progs)
          + "</div></section>")
    intl = (f'<section class="sec"><div class="banner"><img src="{b}img/main_building.jpg" alt=""><div class="in"><h2>International cooperation</h2>'
            f'<ul><li>Partner universities in 14 countries</li><li>Exchange programmes since 1993</li><li>CONIFA-era sport exchanges with Chicago</li></ul></div></div></section>')
    stats = (f'<section class="sec wrap"><h2 class="sec-t bar-t">The university in numbers</h2><div class="stats">'
             + "".join(f'<div class="card"><b>{a}</b><span>{e(c)}</span></div>' for a, c in (("18,400", "students"), ("1,300", "teaching staff"), ("11", "faculties"), ("132", "titles of TSU Press since 1994")))
             + "</div></section>")
    disc = (f'<section class="sec wrap"><div class="disc"><div class="txt"><h2 class="sec-t bar-t">Research is our tradition</h2>'
            f'<p>Talas State University is the main centre of research on Irad: its history, languages, peoples, nature and economy.</p>'
            f'<p>The Institute of History, the Institute of Sociology, the Department of Ethnography with its sound archive of epic and song since the 1950s, and the Department of Zoology work across the ISEZ and, where permitted, the tribal regions.</p></div>'
            f'<div class="card d-card"><b>Rabat-i-Safed excavation</b><img src="{b}img/archive.jpg" alt="" loading="lazy"><a class="btn" href="{b}research/#archaeology">Learn more &#8599;</a></div>'
            f'<div class="card d-card"><b>Glaciology of the Talas basin</b><img src="{b}img/glacier.jpg" alt="" loading="lazy"><a class="btn" href="{b}research/#glaciology">Learn more &#8599;</a></div></div></section>')
    alum = (f'<section class="sec wrap"><div class="alum"><img class="bgimg" src="{b}img/graduation.jpg" alt=""><div><h2>Alumni<br>Talas State University</h2>'
            f'<p>Since 1958 the university has graduated more than 120,000 specialists: the teachers, doctors, lawyers and engineers of Irad, and the students who stood in Central Square in 1992. Join the alumni association, find your classmates and come back to lecture.</p>'
            f'<a class="btn" href="{b}about/#alumni">To the community &#8599;</a></div>'
            f'<div class="alum-card"><div class="alum-ini">AK</div><b>Aiperi Kalysbekova</b><p>Computer science, class of 2013. “We wrote the first version in a dormitory room in Building 6. The department let us use the lab at night.”</p><a class="btn" href="{b}about/#alumni">Read more &#8599;</a></div></div></section>')
    useful = (f'<section class="sec wrap"><h2 class="sec-t bar-t">Useful links</h2><div class="useful">'
              + "".join(f'<div class="card"><div class="ill">{ICONS[i]}</div><a class="btn" href="{b}{h}">{e(t)} &#8599;</a></div>' for i, t, h in (("library", "Scientific library", "library/"), ("media", "Mass media", "news/"), ("people", "For employees", "contacts/#staff")))
              + "</div></section>")
    body = hero + services + news + magz + guide + pr + intl + stats + disc + alum + useful
    return page("Talas State University", body, base=b, who="entrant")


def news_pages():
    base = "../"
    cards = "".join(f'<a class="card n-card" href="{x["slug"]}/"><img src="{base}{x["img"]}" alt="" loading="lazy"><div class="b"><time>{fmt_date(x["date"])} · {e(x["tag"])}</time><h3>{e(x["title"])}</h3><p>{e(x["lead"])}</p></div></a>'
                    for x in sorted(NEWS, key=lambda x: x["date"], reverse=True))
    write("news/index.html", page("News | Talas State University", f'<div class="wrap"><p class="crumbs"><a href="{base}">Home</a> / News</p><h1 class="page-h">News</h1><div class="news-list">{cards}</div></div>', base=base))
    for x in NEWS:
        b2 = "../../"
        main = (f'<p class="muted">{fmt_date(x["date"])} · <span class="tag">{e(x["tag"])}</span></p><img class="article-img" src="{b2}{x["img"]}" alt="">'
                f'<p><b>{e(x["lead"])}</b></p>' + "".join(f"<p>{p}</p>" for p in x["body"]))
        sub = ("Latest news", [(y["title"], f'news/{y["slug"]}/') for y in NEWS if y is not x][:5])
        write(f'news/{x["slug"]}/index.html', page(f'{x["title"]} | Talas State University', inner(b2, [("News", "news/")], x["title"], main, sub), base=b2, description=x["lead"]))


def about_pages():
    b = "../"
    sub = ("About us", [("Talas State University", "about/"), ("Rector", "about/rector/"), ("History", "about/history/"), ("Scientific library", "library/"), ("Contacts", "contacts/")])
    main = f"""
<h2>Talas State University</h2>
<p><b>Talas State University</b> (TSU; Iradi: <i>Talas Mamlekettik Universiteti</i>) is the oldest and largest university in Irad. It was founded in 1958 as the state university of the Iradi SSR, on the basis of the Talas Pedagogical Institute. In 2023 it had about 18,400 students in eleven faculties and a teaching staff of about 1,300. Its publishing house, <a href="{b}library/press/">Talas State University Press</a>, is the main publisher of scholarly work on Irad.</p>
<table><tr><th>Founded</th><td>1958</td></tr><tr><th>Status</th><td>State university of the Irad Special Economic Zone</td></tr><tr><th>Students</th><td>about 18,400 (2023), of them 1,900 in master's and doctoral programmes</td></tr><tr><th>Teaching staff</th><td>about 1,300</td></tr><tr><th>Faculties</th><td><a href="{b}faculties/">11</a></td></tr><tr><th>Languages of instruction</th><td>Iradi and English; Russian as an elective</td></tr><tr><th>Campus</th><td>Main building and eight teaching buildings on University Street, Talas; TSU Stadium; teaching stables; the Manas Peak field station</td></tr></table>
<h2 id="elders">Council of Elders</h2>
<p>The <i>Aksakaldar keneshi</i> brings together retired professors and honorary doctors of the university. It advises the rector on the university's traditions, ceremonies and honorary degrees and keeps the university museum in the main building.</p>
<h2 id="quality">Quality assurance</h2>
<p>All bachelor's programmes are accredited by the ISEZ Education Quality Agency. Programmes in medicine, law and economics also hold accreditation from partner agencies abroad. Students evaluate every course anonymously at the end of each semester through the student e-portal.</p>
<h2 id="alumni">Alumni association</h2>
<p>The TSU Alumni Association unites more than 120,000 graduates in Irad and abroad, with chapters in Nurzhan, Iyık Janyl, Almaty, Moscow and Chicago. Alumni lecture in the “Back to the auditorium” series and fund scholarships for students from the districts.</p>
<h2 id="anticorruption">Anti-corruption</h2>
<p>Report any request for money or gifts in connection with admission, examinations or grades to the university's compliance office, room 101 of the main building, or by telephone 2-31-40-09. Reports may be anonymous.</p>"""
    write("about/index.html", page("About us | Talas State University", inner(b, [("About us", "about/")], "About the university", main, sub), base=b, active="about/"))
    b2 = "../../"
    rector = f"""
<h2>Rector</h2>
<p><b>Professor Kubanychbek Sultanaliev</b>, Doctor of Economic Sciences, has been rector of Talas State University since 2017. Under the 2007 statute the rector is appointed by the Governor of the Irad Special Economic Zone on the nomination of the Academic Council.</p>
<p>Born in Talas in 1961, he graduated from the Faculty of Economics of TSU in 1983 and defended his doctoral dissertation on the territorial economy in 2004. He was dean of the Faculty of Economics and Management (2009–2015) and first vice-rector (2015–2017).</p>
<h3>Rector's reception</h3>
<p>Tuesdays, 15:00–17:00, main building, room 201, by appointment: +996-39-2-31-40-00. Students may also write to rector@tsu.edu.ir.ad.</p>
<h2>Vice-rectors</h2>
<table><tr><th>First vice-rector (academic affairs)</th><td>Prof. Almaz Kenzhebaev</td></tr><tr><th>Vice-rector for research</th><td>Prof. Jyldyz Sarybaeva</td></tr><tr><th>Vice-rector for international relations</th><td>Assoc. Prof. Timur Akmatov</td></tr><tr><th>Vice-rector for students and youth</th><td>Bakytbek Omurzakov</td></tr></table>
<p class="muted">The <a href="{b2}library/press/">Annual Report of the Rector</a> is published each spring.</p>"""
    write("about/rector/index.html", page("Rector | Talas State University", inner(b2, [("About us", "about/"), ("Rector", None)], "Rector", rector, sub), base=b2, active="about/"))
    hist = f"""
<h2>1958–1991</h2>
<p>The university opened in September 1958 with faculties of history and philology, physics and mathematics, biology and agriculture. Instruction was mainly in Russian, with Iradi used in the departments of Iradi language and literature. Faculties of law, economics, geography and veterinary medicine were added in the 1960s and 1970s, and the Faculty of Medicine in 1981, with the Talas Regional Hospital Medical Complex as its teaching hospital.</p>
<h2>1992</h2>
<p>Many of the university's staff and students supported the Winter Uprising of 1992. In January 1992 history students led the occupation of Central Square. The main building was damaged by shelling during the siege of Talas and was restored by its own staff and students.</p>
<h2>The territorial period</h2>
<p>During the territorial period English became a language of instruction alongside Iradi, and Russian was gradually reduced to an elective. Exchange programmes with American universities, funded by the territorial government and US foundations, trained a generation of faculty, and the Faculty of Agriculture worked with the foreign agribusiness companies around Talas. Talas State University Press was founded in 1994.</p>
<h2>Since 2007</h2>
<p>Since 2007 the university has been governed by a rector appointed by the Governor of the Irad Special Economic Zone. The Faculty of Arts and Music, created in 1994, and the computer science department have grown fastest in recent years. In 2026 the Scientific Library opened its <a href="{b2}library/archive/">Digital Archive</a>.</p>
<p class="muted">Further reading: <i>Fifty Years of Talas State University, 1958–2008</i> (TSU Press, 2008).</p>"""
    write("about/history/index.html", page("History | Talas State University", inner(b2, [("About us", "about/"), ("History", None)], "History of the university", hist, sub), base=b2, active="about/"))


def faculties_pages():
    b = "../"
    cards = "".join(f'<a class="card fac" href="{f["slug"]}/"><b>{e(f["name"])}</b><span>Since {f["since"]} · Dean: {e(f["dean"])}</span><span>{e(", ".join(f["depts"]))}</span></a>' for f in FACULTIES)
    write("faculties/index.html", page("Faculties | Talas State University",
          f'<div class="wrap"><p class="crumbs"><a href="{b}">Home</a> / Faculties</p><h1 class="page-h">Faculties</h1><div class="fac-grid" style="padding-bottom:50px">{cards}</div></div>', base=b, active="faculties/"))
    for f in FACULTIES:
        b2 = "../../"
        main = (f'<p>{f["text"]}</p><table><tr><th>Founded</th><td>{f["since"]}</td></tr><tr><th>Dean</th><td>{e(f["dean"])}</td></tr>'
                f'<tr><th>Departments</th><td>{"<br>".join(e(d) for d in f["depts"])}</td></tr><tr><th>Dean’s office</th><td>Tel. 2-31-4{FACULTIES.index(f)+1:01d}-{20 + FACULTIES.index(f)} · {f["slug"]}@tsu.edu.ir.ad</td></tr></table>'
                f'<p><a class="btn" href="{b2}admission/">Programmes and admission &#8599;</a></p>')
        sub = ("Faculties", [(x["name"].replace("Faculty of ", ""), f'faculties/{x["slug"]}/') for x in FACULTIES])
        write(f'faculties/{f["slug"]}/index.html', page(f'{f["name"]} | Talas State University', inner(b2, [("Faculties", "faculties/")], f["name"], main, sub), base=b2, active="faculties/"))


def admission_pages():
    b = "../"
    sub = ("Admission", [("Undergraduate", "admission/#undergraduate"), ("Graduate", "admission/#graduate"), ("PhD", "admission/#phd"), ("Fees and grants", "admission/#fees"), ("Evening courses", "admission/evening/")])
    main = f"""
<div class="note">Admission 2027: the Admissions Office reopens for applications on 20 June 2027. Thresholds of the University Entrance Examination are published in May.</div>
<h2 id="undergraduate">Undergraduate</h2>
<p>Applicants are admitted on the results of the University Entrance Examination (UEE) of the ISEZ Ministry of Education. 64 bachelor's programmes, four years (medicine six years). Documents: school-leaving certificate, UEE certificate, identity card, six photographs 3×4, medical certificate form 086.</p>
<h2 id="graduate">Graduate (Master's)</h2>
<p>38 master's programmes of two years, research and professional tracks. Entrance examination in the speciality and in English (or a certificate at B2).</p>
<h2 id="phd">PhD</h2>
<p>21 doctoral programmes of three years. Each doctoral student has two supervisors, one of them from a partner university, and must publish at least two papers, one in the <i>Bulletin of Talas State University</i>.</p>
<h2 id="fees">Tuition fees and grants</h2>
<table><tr><th>Programme</th><th>State grant places 2026</th><th>Fee per year (contract)</th></tr>
<tr><td>Humanities, education, arts</td><td>420</td><td>IS 9,600</td></tr><tr><td>Natural sciences, computer science</td><td>310</td><td>IS 11,400</td></tr>
<tr><td>Economics, law, management</td><td>180</td><td>IS 13,800</td></tr><tr><td>Agriculture, veterinary medicine</td><td>290</td><td>IS 8,400</td></tr><tr><td>Medicine</td><td>150</td><td>IS 21,600</td></tr></table>
<p>Fees may be paid in two instalments at any Talasbank branch. Students from the districts and from families of the 1992 and 2007 wars may apply for a 50% reduction.</p>
<h2 id="thresholds">Entrance thresholds 2026</h2>
<p>Minimum UEE score for a state grant: medicine 196; law 172; computer science 168; economics 161; other programmes 120–150. Contract places: 100.</p>
<h2 id="guide">Applicant's guide</h2>
<p>The printed <i>Applicant's Guide 2026</i> is available free in the main building, room 105, and at school career days in Talas, Nurzhan and Iyık Janyl.</p>
<h2 id="diaspora">For applicants from the diaspora</h2>
<p>Iradis abroad and their children may apply with foreign school certificates. Contact the international office: international@tsu.edu.ir.ad.</p>"""
    write("admission/index.html", page("Admission | Talas State University", inner(b, [("Admission", "admission/")], "Admission", main, sub), base=b, active="admission/", who="entrant"))
    b2 = "../../"
    ev = f"""
<img class="article-img" src="{b2}img/students.jpg" alt="">
<p>Three-month evening courses for adults, with a state certificate on completion. Classes Monday to Thursday, 18:30–20:30, in Building 3, from 9 November 2026 to 12 February 2027.</p>
<table><tr><th>Course</th><th>Hours</th><th>Fee</th></tr><tr><td>Accounting and taxes</td><td>96</td><td>IS 4,800</td></tr><tr><td>English (A1, A2, B1, B2)</td><td>96</td><td>IS 4,800</td></tr><tr><td>Computer literacy</td><td>72</td><td>IS 3,900</td></tr></table>
<div class="note"><b>Enrolment until 1 November.</b> Building 3, room 104, weekdays 10:00–17:00, tel. 2-31-40-17.</div>"""
    write("admission/evening/index.html", page("Evening courses | Talas State University", inner(b2, [("Admission", "admission/"), ("Evening courses", None)], "Evening courses for adults", ev, sub), base=b2, active="admission/", who="courses"))


def research_page():
    b = "../"
    main = f"""
<h2>Institutes and departments</h2>
<table><tr><th>Institute of History</th><td>History of Irad from antiquity to the present; the documentary histories of 1916, 1992 and 2007; the three-volume <i>History of Irad</i> (2012).</td></tr>
<tr><th id="sociology">Institute of Sociology</th><td>Twice-yearly public opinion surveys of the ISEZ (politics and institutions, foreign relations), and surveys of migration, language, religion and marriage.</td></tr>
<tr><th>Department of Ethnography</th><td>Holds the university's sound archive of oral epic and song from the 1950s onward; crafts, ritual and customary law.</td></tr>
<tr><th>Department of Zoology</th><td>Snow leopard monitoring in the Talas Alatau and the Chatkal; the faunal checklists of Irad.</td></tr></table>
<h2 id="archaeology">Rabat-i-Safed excavation</h2>
<p>Since 2024 the Faculty of History has excavated the 9th-century caravanserai of Rabat-i-Safed, 25 km east of Talas, under a permit from the ISEZ heritage department. The 2026 season, led by Dr Marat Imanaliev, recovered Kara-Khanid coins, a cast-iron cauldron fragment and storage jars.</p>
<h2 id="glaciology">Glaciology and the Manas observatory</h2>
<p>With the Manas Peak Glaciological Observatory (founded 1964) the Faculty of Geography maintains the inventory of the 268 glaciers of the Iradi Talas basin. Prof. Nazira Isaeva leads the projections of peak water, expected in the 2030s and 2040s.</p>
<h2 id="bulletin">Bulletin of Talas State University</h2>
<p>Published since 1961 in four series: History; Philology; Natural Sciences; Economics and Law. Two to four issues a year per series. Submissions: bulletin@tsu.edu.ir.ad.</p>
<h2 id="partners">For business partners</h2>
<p>Contract research, laboratory testing (soil, water, veterinary DNA), surveys and training for companies and organisations. Contact the research office: research@tsu.edu.ir.ad, tel. 2-31-40-30.</p>"""
    sub = ("Research", [("Institutes", "research/"), ("Bulletin", "research/#bulletin"), ("TSU Press", "library/press/"), ("Library", "library/")])
    write("research/index.html", page("Research | Talas State University", inner(b, [("Research", "research/")], "Research", main, sub), base=b, active="research/", who="partner"))


def students_page():
    b = "../"
    main = f"""
<h2>Student life</h2>
<p>More than forty student clubs: debate, theatre, the TSU choir, the komuz ensemble, hiking and mountaineering, chess, film and volunteering. The Student Council is elected every October.</p>
<h2 id="timetables">Timetables</h2><p>Timetables and examination schedules are published in the student e-portal and on the boards of each faculty.</p>
<h2 id="dorms">Dormitories</h2><p>Six dormitories with 3,400 places. Applications through the dean's office of your faculty in August. Fee: IS 380 a month.</p>
<h2 id="sport">Sport club and Universitet Talas</h2><p>The university's football club Universitet Talas, once champions of Irad, plays in the Irad League at TSU Stadium; its women's team is one of the leaders of the Women's League. Students train free in the sport club: football, volleyball, wrestling, kurash, athletics and horse riding at the teaching stables.</p>
<h2 id="career">Career centre</h2><p>Vacancies, internships and the autumn job fair. Building 2, room 12.</p>
<h2 id="portal">Student e-portal</h2><p>Grades, attendance, timetables and course evaluation. Log in with your student number. <span class="muted">The portal is unavailable outside the university network from 23:00 to 07:00 for maintenance.</span></p>"""
    sub = ("For students", [("Student life", "students/"), ("Dormitories", "students/#dorms"), ("Sport", "students/#sport"), ("Library", "library/")])
    write("students/index.html", page("For students | Talas State University", inner(b, [("For students", "students/")], "For students", main, sub), base=b, active="students/", who="student"))


def contacts_page():
    b = "../"
    main = f"""
<h2>Address</h2><p>Talas State University, 12 University Street, Talas 724000, Irad</p>
<table><tr><th>Rector's reception</th><td>+996-39-2-31-40-00 · rector@tsu.edu.ir.ad</td></tr><tr><th>Admissions Office</th><td>+996-39-2-31-40-11 · admission@tsu.edu.ir.ad</td></tr>
<tr><th>Scientific library</th><td>+996-39-2-31-40-50 · library@tsu.edu.ir.ad</td></tr><tr><th>International office</th><td>+996-39-2-31-40-21 · international@tsu.edu.ir.ad</td></tr>
<tr><th>Research office</th><td>+996-39-2-31-40-30 · research@tsu.edu.ir.ad</td></tr><tr><th>Press service</th><td>+996-39-2-31-40-05 · press@tsu.edu.ir.ad</td></tr></table>
<h2 id="staff">For employees</h2><p>Staff webmail, the HR office (main building, room 110) and the trade union committee (room 118). The staff intranet is available inside the university network.</p>
<h2>Getting here</h2><p>Minibuses 4, 11 and 27 to the stop “Universitet”. The main building faces the university square, a ten-minute walk from Central Square.</p>"""
    write("contacts/index.html", page("Contacts | Talas State University", inner(b, [("Contacts", "contacts/")], "Contacts", main), base=b, active="contacts/", who="employee"))


def sitemap_page():
    b = "../"
    items = "".join(f'<h3><a href="{b}{h}">{e(t)}</a></h3>' + ("<ul>" + "".join(f'<li><a href="{b}{h2}">{e(t2)}</a></li>' for t2, h2 in (d or [])) + "</ul>" if d else "") for t, h, d in MENU)
    write("sitemap/index.html", page("Map of the site | Talas State University", inner(b, [("Map of the site", None)], "Map of the site", items), base=b))


# ---------------------------------------------------------------- library pages

def library_pages(works, press):
    b = "../"
    tiles = [("archive", "Digital archive", "Long-form works to read online or download: literature, memoirs, theses and reports.", "library/archive/"),
             ("book", "TSU Press catalogue", f"All {len(press)} titles of Talas State University Press, 1994–2026.", "library/press/"),
             ("sound", "Ethnography sound archive", "Recordings of oral epic and song from the 1950s onward. Listening by appointment.", "library/#sound"),
             ("clock", "Hours and services", "Reading rooms, borrowing, interlibrary loan and scanning.", "library/#hours")]
    latest = "".join(work_row(m, b) for m in works[:3])
    body = f"""
<section class="lib-hero"><img src="{b}img/reading_room.jpg" alt=""><div class="in"><p style="margin:0 0 4px;opacity:.85">Talas State University</p><h1>Scientific Library</h1>
<form class="lib-search" action="{b}library/press/" method="get"><input name="q" placeholder="Search the catalogue: title, author, subject" aria-label="Search the catalogue"><select name="in" aria-label="Where"><option>Catalogue</option><option>Digital archive</option></select><button class="btn" type="submit">Search</button></form></div></section>
<section class="sec wrap"><div class="lib-tiles">{''.join(f'<a class="card lib-tile" href="{b}{h}">{ICONS[i]}<b>{e(t)}</b><span>{e(s)}</span></a>' for i, t, s, h in tiles)}</div></section>
<section class="sec wrap">{sec_t("New in the digital archive", "library/archive/", b)}<div class="works">{latest}</div></section>
<div class="wrap"><div class="inner" style="padding-top:26px"><div class="card inner-main">
<h2>About the library</h2>
<p>The Scientific Library was founded with the university in 1958 from the library of the Talas Pedagogical Institute. It holds about 1.1 million volumes: books and periodicals in Iradi, Russian and English, the deposit copies of TSU Press, the university's theses since 1961, a rare books room with Iradi printing of the 1920s and 1930s in the Latin and Cyrillic scripts, and the newspaper collection, including a complete file of the <i>Talas Herald</i> since 1993.</p>
<p>The reading rooms were damaged in 1992 together with the main building; part of the Soviet-era card catalogue was lost and has been rebuilt from accession books. The electronic catalogue covers acquisitions since 1996.</p>
<h2 id="hours">Opening hours</h2>
<table class="hours"><tr><th>Reading room 1 (humanities), main building, 2nd floor</th><td>Mon–Fri 9:00–19:00 · Sat 10:00–15:00</td></tr>
<tr><th>Reading room 2 (sciences), Building 4</th><td>Mon–Fri 9:00–18:00</td></tr><tr><th>Lending desk</th><td>Mon–Fri 9:00–17:00</td></tr>
<tr><th>Rare books and manuscripts</th><td>Tue and Thu 10:00–16:00, by appointment</td></tr></table>
<p>Closed on public holidays and on the last Friday of each month (sanitary day).</p>
<h2>Services</h2>
<ul><li>Borrowing for students and staff with a library card (issued at the lending desk with your student or staff card).</li><li>External readers: day pass IS 50, annual card IS 400.</li><li>Interlibrary loan with the National Library of Irad and the Nurzhan Polytechnic Institute.</li><li>Scanning on request: IS 3 per page; free for TSU Press titles out of print.</li></ul>
<h2 id="sound">Ethnography sound archive</h2>
<p>Held jointly with the Department of Ethnography: about 6,000 hours of recordings of oral epic, horseback chants, laments and song made on expeditions since the 1950s, copied from tape to digital files since 2009. Listening by appointment in the Department of Ethnography, Building 2, room 31.</p>
<h2 id="theses">Theses and dissertations</h2>
<p>Every candidate's and doctoral dissertation defended at the university since 1961, and master's theses since 2005. Recent theses are being added to the <a href="{b}library/archive/">Digital archive</a> with the authors' consent.</p>
<h2 id="deposit">Deposit a work</h2>
<p>The Digital Archive accepts long-form works on Irad by members of the university and, at the library's discretion, by other authors: fiction, memoirs, oral histories, theses, translations. Write to library@tsu.edu.ir.ad.</p>
</div><div><nav class="card subnav"><h4>Library</h4><a href="{b}library/archive/">Digital archive</a><a href="{b}library/press/">TSU Press catalogue</a><a href="#hours">Opening hours</a><a href="#sound">Sound archive</a><a href="#theses">Theses</a><a href="#deposit">Deposit a work</a></nav></div></div></div>"""
    write("library/index.html", page("Scientific Library | Talas State University", body, base=b, active="library/"))

    # archive listing
    b2 = "../../"
    colls = sorted({m["collection"] for m in works})
    rows = "".join(work_row(m, b2) for m in works)
    body = f"""<div class="wrap"><p class="crumbs"><a href="{b2}">Home</a> / <a href="{b2}library/">Library</a> / Digital archive</p><h1 class="page-h">Digital archive</h1>
<div class="inner"><div>
<div class="cat-tools"><input id="wq" placeholder="Search the digital archive" aria-label="Search the digital archive"><select id="wc" aria-label="Collection"><option value="">All collections</option>{''.join(f'<option>{e(c)}</option>' for c in colls)}</select></div>
<div class="works" id="works">{rows}</div><p class="muted" id="wnone" hidden>Nothing matches your search.</p></div>
<div><nav class="card subnav"><h4>Collections</h4>{''.join(f'<a href="#" data-c="{e(c)}">{e(c)} ({sum(1 for m in works if m["collection"] == c)})</a>' for c in colls)}<a href="#" data-c="">All</a></nav>
<div class="card" style="padding:16px 18px;margin-top:16px;font-size:13.5px"><b>About the archive</b><p style="margin:6px 0 0;color:#555">Long-form works on Irad, to read online or download as PDF. Each item has a permanent address and a citation. To deposit a work, see <a href="{b2}library/#deposit">Deposit a work</a>.</p></div></div></div></div>"""
    write("library/archive/index.html", page("Digital archive | Scientific Library | Talas State University", body, base=b2, active="library/"))

    for m in works:
        record_page(m)
        reader_page(m)

    # press catalogue
    lis = "".join(f'<li data-s="{e((x["title"] + " " + x["author"] + " " + str(x["year"])).lower())}"><span class="y">{x["year"]}</span><span class="t">{e(x["title"])}'
                  + (f'<span class="a">{e(x["author"])}</span>' if x["author"] else "") + "</span>"
                  + ('<span class="s ro">Reading room</span>' if i % 3 else '<span class="s">Lending</span>') + "</li>" for i, x in enumerate(press))
    body = f"""<div class="wrap"><p class="crumbs"><a href="{b2}">Home</a> / <a href="{b2}library/">Library</a> / TSU Press catalogue</p><h1 class="page-h">Talas State University Press: catalogue</h1>
<div class="card inner-main" style="margin-bottom:50px"><p>Talas State University Press, founded in 1994, is the main publisher of scholarly work on Irad. Deposit copies of every title are held by the Scientific Library. Availability shown is for the main library; most titles can be ordered from the TSU Press shop, main building, room 7.</p>
<div class="cat-tools"><input id="pq" placeholder="Title, author or year" aria-label="Search the catalogue"><select id="pd" aria-label="Decade"><option value="">All years</option><option value="202">2020s</option><option value="201">2010s</option><option value="200">2000s</option><option value="199">1990s</option></select></div>
<p class="muted" id="pcount">{len(press)} titles</p><ul class="cat-list" id="plist">{lis}</ul></div></div>"""
    write("library/press/index.html", page("TSU Press catalogue | Scientific Library | Talas State University", body, base=b2, active="library/"))


def work_row(m, base):
    return (f'<a class="card work" href="{base}library/archive/{m["slug"]}/" data-c="{e(m["collection"])}" data-s="{e((m["title"] + " " + m["author"] + " " + m.get("translator", "") + " " + " ".join(m["subjects"])).lower())}">{w_cover(m, base)}'
            f'<div><span class="tag">{e(m["form"])} · {e(m["collection"])}</span><h3>{e(m["title"])}</h3><div class="by">{by_line(m)}</div>'
            f'<p>{e(m["abstract"][:210].rsplit(" ", 1)[0])}…</p></div><div class="meta">{m["pages"]} pp. · PDF<br>Added {fmt_date(m["added"])}</div></a>')


def record_page(m):
    b = "../../../"
    pdf_kb = round((m["dir"] / m["pdf"]).stat().st_size / 1024)
    if m.get("book"):
        words = sum(len(re.sub("<[^>]+>", "", x.get("html", "")).split()) for sec in m["book"]["sections"] for x in sec["blocks"])
    else:
        words = len((m["dir"] / "text.md").read_text(encoding="utf-8").split())
    rows = [("Title", e(m["title"]) + (f' (<i>{e(m["subtitle"])}</i>)' if m.get("subtitle") else "")), ("Author", e(m["author"]))]
    if m.get("translator"): rows.append(("Translator", e(m["translator"])))
    if m.get("part_of"): rows.append(("Part of", f'<i>{e(m["part_of"])}</i>' + (f', no. {m["part_no"]}' if m.get("part_no") else "")))
    if m.get("publisher"): rows.append(("Publisher", e(m["publisher"])))
    if m.get("published"): rows.append(("Published", e(m["published"])))
    rows += [("Form", e(m["form"])), ("Written", e(m["written"])), ("Language", e(m["language"])),
             ("Extent", f'{m["pages"]} pages · about {round(words, -2):,} words'), ("Subjects", e("; ".join(m["subjects"]))),
             ("Collection", e(m["collection"])), ("Accession no.", e(m["accession"]))]
    if m.get("legal_deposit"): rows.append(("Legal deposit", e(m["legal_deposit"])))
    rows += [("Added", fmt_date(m["added"])), ("Rights", e(m["rights"]))]
    contents = ""
    if m.get("book"):
        items = "".join(f'<li><a href="read/{sec["id"]}/">' + (f'<span class="lbl">{e(sec["label"])}</span>' if sec["label"] else '<span class="lbl"></span>')
                        + f'{e(sec["title"])}</a>' + (f'<small>{e(sec["subtitle"])}</small>' if sec["subtitle"] else "") + "</li>" for sec in m["book"]["sections"])
        contents = f'<h2>Contents</h2><ol class="contents">{items}</ol>'
    related = ""
    for r in m.get("related", []):
        related += f'<div class="note"><a href="../{r["slug"]}/">{e(r["note"])}</a></div>'
    main = f"""
<div class="rec-head">{w_cover(m, b).replace('class="w-cover"', 'class="w-cover" style="font-size:16px"')}
<div><p class="tag">{e(m["form"])} · {e(m["collection"])}</p><h2 style="margin:8px 0 4px;font-size:26px">{e(m["title"])}</h2>{f'<p style="margin:0;font-style:italic">{e(m["subtitle"])}</p>' if m.get("subtitle") else ""}<p style="margin:4px 0 14px;font-size:16px">{by_line(m, sub=False)}</p>
<p style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn" href="read/">Read online</a><a class="btn btn-o" href="{b}library/works/{m["slug"]}/{m["pdf"]}" download>Download PDF ({pdf_kb} KB)</a></p></div></div>
{related}
<h2>Abstract</h2><p>{e(m["abstract"])}</p>
{contents}
<h2>Record</h2>
<table class="rec">{''.join(f'<tr><th>{k}</th><td>{v}</td></tr>' for k, v in rows)}</table>
<h2>How to cite</h2><p class="cite">{citation(m)}</p>"""
    sub = ("Digital archive", [("All works", "library/archive/"), ("Read online", f'library/archive/{m["slug"]}/read/'), ("Scientific library", "library/"), ("Deposit a work", "library/#deposit")])
    write(f'library/archive/{m["slug"]}/index.html',
          page(f'{m["title"]} | Digital archive | Talas State University', inner(b, [("Library", "library/"), ("Digital archive", "library/archive/")], m["title"], main, sub), base=b, active="library/", description=m["abstract"][:200]))


def render_blocks(blocks):
    out = []
    for x in blocks:
        k = x["k"]
        if k == "brk":
            out.append('<p class="brk" aria-hidden="true">⁂</p>')
        elif k == "p":
            out.append(f'<p>{x["html"]}</p>')
        elif k == "quote":
            out.append(f'<blockquote class="bq">{x["html"]}</blockquote>')
        elif k == "h3" or (k == "center" and "<" not in x["html"] and len(x["html"]) < 40):
            out.append(f'<h3 class="sub-h">{x["html"]}</h3>')
        elif k == "right":
            out.append(f'<p class="dl-line">{x["html"]}</p>')
        else:
            out.append(f'<p class="ctr">{x["html"]}</p>')
    return "\n".join(out)


def toc_nav(m, b, cur_id, back):
    secs = m["book"]["sections"]
    lis = "".join(f'<li><a href="{b}library/archive/{m["slug"]}/read/{sec["id"]}/"{" class=\"on\"" if sec["id"] == cur_id else ""}>'
                  + (f'{e(sec["label"])}. ' if sec["label"].isdigit() else (f'{e(sec["label"])}: ' if sec["label"] else "")) + f'{e(sec["title"])}</a></li>' for sec in secs)
    return (f'<nav class="toc"><a class="back" href="{back}">&larr; Record and download</a><h4>{e(m["title"])}</h4><div class="au">{e(m["author"])}</div>'
            f'<div class="ctl"><button type="button" data-fs="-1" aria-label="Smaller text">A&minus;</button><button type="button" data-fs="1" aria-label="Larger text">A+</button><button type="button" data-side aria-label="Show or hide the menu">&#9776;</button></div>'
            f'<ol><li><a href="{b}library/archive/{m["slug"]}/read/"{" class=\"on\"" if cur_id == "" else ""}>Title page and contents</a></li>{lis}</ol>'
            f'<a class="dl" href="{b}library/works/{m["slug"]}/{m["pdf"]}" download>Download PDF</a></nav>')


def book_reader(m):
    secs = m["book"]["sections"]
    b = "../../../../"
    front = "".join(f'<div class="front">{x}</div>' for x in m["book"]["front"])
    items = "".join(f'<li><a href="{sec["id"]}/"><span class="lbl">{e(sec["label"])}</span>{e(sec["title"])}</a>' + (f'<small>{e(sec["subtitle"])}</small>' if sec["subtitle"] else "") + "</li>" for sec in secs)
    body = f"""<div class="progress"><i></i></div><div class="reader">{toc_nav(m, b, "", "../")}
<div class="read-body"><article id="text"><header class="rt"><div class="au">{e(m["author"])}</div><h1>{e(m["title"])}</h1><div class="fr"><i>{e(m.get("subtitle", ""))}</i></div>
<div class="fr" style="margin-top:18px">{e(m["form"])}</div>{f'<div class="fr"><i>Translated from the Iradi by {e(m["translator"])}</i></div>' if m.get("translator") else ""}<div class="fr" style="margin-top:18px">{e(m.get("publisher", ""))}</div></header>
{front}<h2 style="margin-top:50px">Contents</h2><ol class="contents">{items}</ol>
<p class="end"><a class="btn" href="{secs[0]["id"]}/">Start reading &rarr;</a></p></article></div></div>"""
    write(f'library/archive/{m["slug"]}/read/index.html', page(f'{m["title"]}: read online | Talas State University', body, base=b, active="library/", body_class="reading"))
    b2 = "../../../../../"
    for i, sec in enumerate(secs):
        prev_ = secs[i - 1] if i else None
        next_ = secs[i + 1] if i + 1 < len(secs) else None
        lab = ""
        if sec["label"]:
            lab = f'<div class="lab">{e(sec["label"]) if not sec["label"].isdigit() else NUMWORDS.get(int(sec["label"]), sec["label"])}</div>'
        pn = '<nav class="pn">' + (f'<a href="../{prev_["id"]}/">&larr; {e(prev_["title"])}</a>' if prev_ else '<a href="../">&larr; Contents</a>') + \
             (f'<a href="../{next_["id"]}/">{e(next_["title"])} &rarr;</a>' if next_ else '<a href="../../">Record &rarr;</a>') + "</nav>"
        body = f"""<div class="progress"><i></i></div><div class="reader">{toc_nav(m, b2, sec["id"], "../../")}
<div class="read-body"><article id="text"><header class="rt sec-open">{lab}<h1>{e(sec["title"])}</h1>{f'<div class="fr"><i>{e(sec["subtitle"])}</i></div>' if sec["subtitle"] else ""}</header>
{render_blocks(sec["blocks"])}
{pn}</article></div></div>"""
        write(f'library/archive/{m["slug"]}/read/{sec["id"]}/index.html',
              page(f'{sec["title"]} | {m["title"]} | Talas State University', body, base=b2, active="library/", body_class="reading"))


NUMWORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve"}


def reader_page(m):
    if m.get("book"):
        return book_reader(m)
    b = "../../../../"
    text, toc = render_text((m["dir"] / "text.md").read_text(encoding="utf-8"))
    tocl = "".join(f'<li><a href="#{i}">{inline(h)}</a></li>' for i, h in toc)
    part = m.get("part_of", "")
    pm = re.match(r"(.+?)\s*\((.+)\)$", part)
    part_html = f'{e(pm.group(1))} <i>({e(pm.group(2))})</i>' if pm else f"<i>{e(part)}</i>"
    body = f"""<div class="progress"><i></i></div>
<div class="reader"><nav class="toc"><a class="back" href="../">&larr; Record and download</a><h4>{e(m["title"])}</h4><div class="au">{e(m["author"])}</div>
<div class="ctl"><button type="button" data-fs="-1" aria-label="Smaller text">A&minus;</button><button type="button" data-fs="1" aria-label="Larger text">A+</button><button type="button" data-side aria-label="Show or hide the menu">&#9776;</button></div>
<ol>{tocl}</ol><a class="dl" href="{b}library/works/{m["slug"]}/{m["pdf"]}" download>Download PDF</a></nav>
<div class="read-body"><article id="text"><header class="rt"><h1>{e(m["title"])}</h1><div class="au">{e(m["author"])}</div>{f'<div class="fr"><i>from</i> {part_html}</div>' if part else ""}</header>
{text}
<p class="end">End of text · {e(m["accession"])} · <a href="../">Record</a></p></article></div></div>"""
    write(f'library/archive/{m["slug"]}/read/index.html',
          page(f'{m["title"]}: read online | Talas State University', body, base=b, active="library/", body_class="reading"))


def main():
    write("index.html", home())
    news_pages(); about_pages(); faculties_pages(); admission_pages(); research_page(); students_page(); contacts_page(); sitemap_page()
    press = json.loads((DATA / "press.json").read_text(encoding="utf-8"))
    library_pages(load_works(), press)
    write("404.html", page("Page not found | Talas State University", '<div class="wrap" style="padding:60px 28px"><h1 class="page-h">Page not found</h1><p>The page may have moved after the site update of 2024. <a href="https://mjsbroadbent.github.io/tsu/">Go to main page</a></p></div>', base="https://mjsbroadbent.github.io/tsu/"))
    print("built")


if __name__ == "__main__":
    main()
