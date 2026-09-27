# A certain kind of person: an OpenWiki brand film

About 62 seconds, black and white, one quiet line per shot, cut to an instrumental generated with Lyria 3.5 (Gemini API, `music/prompt.txt`, take-b). Style reference: Apple's *Behind the Mac — Greatness* (November 2020); nothing from that ad is used.

Build: `python3 build.py` writes `index.html`; `npx hyperframes@0.8.80 render -f 60 -o renders/certain-kind-silent.mp4`; `bash mux.sh` adds the music.

## Claims

- Every line before "every talk. every essay. every note." is rhetorical, about the viewer.
- "every talk. every essay. every note. becomes a page.": `openwiki youtube`, `essay` and `text` import each source, and `ingest` writes one source page per source.
- "linked. searchable. yours.": `[[wikilinks]]` between pages, `openwiki search` (offline), plain Markdown files on your own disk under the MIT licence.
- The graph is Founder Book's real wikilink graph (`assets/js/graph-data.js`), built by the pipeline OpenWiki was extracted from; the film does not label it.
- End card: "turn what you watch into what you know." and "free and open source · github.com/ckryptickunal/OpenWiki" (LICENSE).

## Photographs (Unsplash License, free for commercial use)

| File | Unsplash |
|---|---|
| assets/photos/win2.jpg | https://unsplash.com/photos/Pv5WeEyxMWU |
| assets/photos/night1.jpg | https://unsplash.com/photos/TtAHLsnbz3o |
| assets/photos/read3.jpg | https://unsplash.com/photos/zMRLZh40kms |
| assets/photos/write2.jpg | https://unsplash.com/photos/CKlHKtCJZKk |
| assets/photos/note3.jpg | https://unsplash.com/photos/S3JdHNXSfnA |
| assets/photos/win1.jpg | https://unsplash.com/photos/OsC8HauR0e0 |
| assets/photos/night4.jpg | https://unsplash.com/photos/Bb_gxpV09qk |
| assets/photos/code3.jpg | https://unsplash.com/photos/FCHlYvR5gJI |
| assets/photos/lamp2.jpg | https://unsplash.com/photos/eOh_5QT95T0 |
| assets/photos/code2.jpg | https://unsplash.com/photos/_Fx34KeqIEw |
| assets/photos/mic5.jpg | https://unsplash.com/photos/n30_i7mx62o |
| assets/photos/lect3.jpg | https://unsplash.com/photos/RDBb3JUdOnc |
| assets/photos/read2.jpg | https://unsplash.com/photos/Oaqk7qqNh_c |
| assets/photos/paper1.jpg | https://unsplash.com/photos/snNHKZ-mGfE |
| assets/photos/write1.jpg | https://unsplash.com/photos/333oj7zFsdg |
| assets/photos/note5.jpg | https://unsplash.com/photos/bjemWZcNF34 |
| assets/photos/lib4.jpg | https://unsplash.com/photos/klbApl9mxr0 |
| assets/photos/win4.jpg | https://unsplash.com/photos/gzhyKEo_cbU |

Graded to black and white with a gentle S-curve and vignette (see the grading step in the git history of this folder).
