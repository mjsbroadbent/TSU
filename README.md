# Talas State University

Website of **Talas State University** (TSU; *Talas Mamlekettik Universiteti*), the oldest and largest university in Irad, founded in 1958. Part of the Irad worldbuilding project: Irad is a fictional country.

The layout follows a real Central Asian university portal: fixed "Information for" side panel, top menu with drop-downs, hero slider, internal services, news with events of the month, journals, applicant's guide, programme cards, numbers, research, alumni and useful links.

Static site, built by one script. Deploy on GitHub Pages from the `main` branch root.

```
python3 tools/build.py
```

## Layout

| Path | What it is |
|---|---|
| `tools/build.py` | Builds every page (as `<dir>/index.html`). Menus, faculties, news and events are data at the top of the file |
| `assets/` | `tsu.css`, `tsu.js`, `logo-mark.svg` (the shield: three peaks, open book, star) |
| `img/` | Campus photos (FLUX.1 Krea renders, AI-generated; flag and stray lettering blurred) |
| `data/press.json` | The TSU Press catalogue: every TSU Press title cited in the Irad wiki (regenerate from the wiki if new titles appear) |
| `library/works/<slug>/` | One folder per Digital Archive work: `meta.json`, `text.md`, the PDF |
| `tools/pdf_to_work.py` | Turns a typeset PDF into `text.md` for the reader |

## Library and Digital Archive

`library/` is the Scientific Library: about the library, hours and services, the ethnography sound archive, theses, the **Digital Archive** (`library/archive/`) and the **TSU Press catalogue** (`library/press/`, searchable; the header search lands here).

Each work in the archive gets a record page (abstract, catalogue record, citation, PDF download) at `library/archive/<slug>/` and an online reader at `library/archive/<slug>/read/` (chapter list, text size, progress bar, remembers where you stopped).

### Adding a work

1. Make a folder `library/works/<slug>/` and put the PDF in it.
2. `python3 tools/pdf_to_work.py library/works/<slug>/<file>.pdf library/works/<slug>/text.md --italic word word ...` (pdftotext loses italics; list the words to italicise). Check the text by eye.
   - `## heading` = chapter, `* * *` = scene break, `*word*` = italics, a line starting `@dateline ` = right-aligned italic closing line.
3. Write `meta.json` (copy `bazaar-chubar/meta.json`): title, author, `author_sort`, `part_of`, `part_no`, form, collection, written, language, pages, pdf, accession, added, subjects, abstract, rights.
4. `python3 tools/build.py`.

Works so far: Aikokul Tursunbek kyzy, "Bazaar Chubar", from *On Eki Chakyrym* (Twelve Kilometres), no. 9.

## Lore used

From the wiki article *Talas State University* and canon: founded 1958 on the basis of the Talas Pedagogical Institute; ~18,400 students, eleven faculties, ~1,300 staff (2023); Faculty of Medicine 1981; main building shelled in 1992; English and Iradi as languages of instruction; rector appointed by the ISEZ Governor since 2007; Institute of History, Institute of Sociology, Department of Ethnography (sound archive), Department of Zoology; TSU Press; the *Bulletin*; Universitet Talas; Herald stories (Rabat-i-Safed coins, komuz contest, evening courses).

Invented here (not yet in canon): the rector (Prof. Kubanychbek Sultanaliev, since 2017), vice-rectors, deans and faculty list, fees, thresholds, addresses and phone numbers, library holdings and hours.
