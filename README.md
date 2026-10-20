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
| `tools/build.py` | Builds every page (as `<dir>/index.html`). Menus, faculties, news and events are data at the top of the file. Every page also gets a canonical address and share tags (`seo_head`), a description taken from its first paragraph when it has none of its own, and an entry in `sitemap.xml` |
| `assets/` | `tsu.css`, `tsu.js`, `seal.svg` and `seal-white.svg` (the university seal, drawn by `tools/make_seal.py`) |
| `img/` | Campus photos, AI-generated. `main_building.jpg` is the wiki's photo of the main building (the canon look: 1960s grey stone, columned glass entrance, horsemen mosaic); `students.jpg` and `graduation.jpg` were made from it with FLUX.2 Klein as reference; the rest are FLUX.1 Krea renders. Lettering blurred |
| `press/` | Talas State University Press publisher page (about, series, new titles from `data/press.json`, forthcoming, for authors, buying, contacts); built by `press_page()` in `tools/build.py`. Menu "Talas State University Press" and footer "TSU Press" point here; the catalogue stays at `library/press/` |
| `data/press.json` | The TSU Press catalogue: every TSU Press title cited in the Irad wiki (regenerate from the wiki if new titles appear) |
| `library/works/<slug>/` | One folder per Digital Archive work: `meta.json`, `text.md` or `book.json`, the PDF, the cover |
| `library/ottuk/` | The Ottuk Library deposit (special collection page), built by `ottuk_page()` from the `OTTUK` list in `tools/build.py`; linked from the Library menu, the library page ("Special collections") and the Rider's record |
| `tools/make_banners.py` | Composes the home-page slider banners (text baked in, cut-out stock people, diagonal shapes, fake QR code), the journal collage covers and the news photos from `img/src/` (FLUX renders). Deliberately a little rough, like a university press office's own design |
| `tools/pdf_to_work.py` | Turns a typeset PDF of a single piece into `text.md` for the reader |
| `tools/pdf_to_book.py` | Turns a typeset book PDF (cover, contents page, running heads) into `book.json`: one reader page per section, italics kept. Works on both the large format (16 pt body, *Twelve Kilometres*) and the pocket format (14 pt body, the Ottuk reprints); square-bracketed translator's notes become `note` blocks, glossary entries (`<b>word</b>: …`) get a hanging indent |

## Library and Digital Archive

`library/` is the National Library of Irad (the university's library; formerly the TSU Scientific Library, national library since 1993): about the library, hours and services, the ethnography sound archive, theses, the **Digital Archive** (`library/archive/`) and the **TSU Press catalogue** (`library/press/`, searchable; the header search lands here).

Each work in the archive gets a record page (abstract, catalogue record, citation, PDF download) at `library/archive/<slug>/` and an online reader at `library/archive/<slug>/read/` (chapter list, text size, progress bar, remembers where you stopped).

### Adding a book

For a whole book (a PDF with a Contents page, like *Twelve Kilometres*): `python3 tools/pdf_to_book.py BOOK.pdf library/works/<slug>/book.json`, render the cover with `pdftoppm -f 1 -l 1 -r 80 -jpeg BOOK.pdf cover`, write `meta.json` (copy `twelve-kilometres/meta.json`: adds subtitle, translator, publisher, published, cover, legal_deposit, related) and rebuild. Optional fields: `series` and `series_url` (a "Series" row and a line under the byline, e.g. "The Ottuk Library, No. 7"), `author_note` (e.g. "pseudonym"), and `related` entries with `href` (a site path) instead of `slug`. Check the reader against the PDF page by page; compare word counts with `pdftotext`. The reader gets a title page with dedication and epigraph, then one page per section with previous/next links.

### Adding a single piece

1. Make a folder `library/works/<slug>/` and put the PDF in it.
2. `python3 tools/pdf_to_work.py library/works/<slug>/<file>.pdf library/works/<slug>/text.md --italic word word ...` (pdftotext loses italics; list the words to italicise). Check the text by eye.
   - `## heading` = chapter, `* * *` = scene break, `*word*` = italics, a line starting `@dateline ` = right-aligned italic closing line.
3. Write `meta.json` (copy `bazaar-chubar/meta.json`): title, author, `author_sort`, `part_of`, `part_no`, form, collection, written, language, pages, pdf, accession, added, subjects, abstract, rights.
4. `python3 tools/build.py`.

Works so far:
- Aikokul Tursunbek kyzy, *Twelve Kilometres* (*On Eki Chakyrym*), stories, tr. Aidana Mukash kyzy (Arsha Books, Talas; Iradi 2015, English 2016). TSU-DA-2026-0146.
- Aikokul Tursunbek kyzy, "Bazaar Chubar", the revised and expanded version of story 9 (Bazar-Korgon – Talas, 2014–2019). TSU-DA-2026-0147.
- Ormon Satarov (pseudonym), *The Rider from Kenkol* (*Kenkol Ashuusu*, Кенкол ашуусу), novel, The Ottuk Library No. 7, tr. Aidana Mukash kyzy (Irad State Publishing House 1964; Arsha Books, Talas, 2022, censored passages restored in bracketed notes). TSU-DA-2026-0148. News item `news/digital-archive-rider-from-kenkol/` (19 Oct 2026); picture `img/news_ottuk.jpg` from `news_ottuk()` in `tools/make_banners.py` (source `img/src/rider_cover.jpg`, the PDF cover at 150 dpi).

## Lore used

From the wiki article *Talas State University* and canon: founded 1958 on the basis of the Talas Pedagogical Institute; ~18,400 students, eleven faculties, ~1,300 staff (2023); Faculty of Medicine 1981; main building shelled in 1992; English and Iradi as languages of instruction; rector appointed by the ISEZ Governor since 2007; Institute of History, Institute of Sociology, Department of Ethnography (sound archive), Department of Zoology; TSU Press; the *Bulletin*; Universitet Talas; Herald stories (Rabat-i-Safed coins, komuz contest, evening courses).

Ottuk Library (series facts, Talas Kitep, the 2019 grant and deposit condition, the six known titles) follows canon and arshakitep.com/ottuk-library.html. Invented here and since added to canon: copies of 38 of the 41 titles survived and were deposited in 2019–2020 (three not found); the originals are reading-room only in Rare books and manuscripts; the Rider's English edition legal deposit LD 2022/0861.

Invented here (not yet in canon): the rector (Prof. Kubanychbek Sultanaliev, since 2017), vice-rectors, deans and faculty list, fees, thresholds, addresses and phone numbers, library holdings and hours.
