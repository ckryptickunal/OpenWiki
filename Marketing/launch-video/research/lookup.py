# ruff: noqa  (one-off measurement script for the launch film; see ../FACTS.md)
import json, os, re, glob, statistics
import tiktoken
import os
ROOT = os.environ.get("FOUNDER_BOOK", "Founder-Book")  # path to a clone of ckryptickunal/Founder-Book
W = ROOT + "/wiki/"
enc = tiktoken.get_encoding("o200k_base")
tok = lambda p: len(enc.encode(open(p, encoding="utf-8").read(), disallowed_special=()))

def raw_for(src_page):
    vid = re.search(r"^video_id:\s*(.*)$", open(W + src_page, encoding="utf-8").read(), re.M).group(1).strip()
    hits = [p for p in glob.glob(ROOT + "/*/*.txt") if re.search(r"^Video ID:\s*" + re.escape(vid) + r"\s*$", open(p, encoding="utf-8", errors="replace").read(4000), re.M)]
    assert len(hits) == 1, (vid, hits)
    return hits[0]

def grep_raw(pattern):
    files = [p for p in glob.glob(ROOT + "/*/*.txt") if re.search(pattern, open(p, encoding="utf-8", errors="replace").read(), re.I)]
    return len(files), sum(tok(p) for p in files)

Q = [
    dict(q="What does Paul Graham say about doing things that don't scale?",
         entry="topics/doing-things-that-don-t-scale.md",
         sources=["sources/pg-do-things-that-don-t-scale-do-things-that-don-t-scale.md",
                  "sources/oQOC-qy-GDY-lecture-8-how-to-get-started-doing-things-that-don-t-scale-press.md",
                  "sources/sr0UabJd8qE-how-to-get-started-doing-things-that-don-t-scale-and-press-how-to-start-a-startup-2014-8.md"],
         grep=r"don['’]?t scale"),
    dict(q="What does Dylan Field say about design and AI?",
         entry="entities/dylan-field.md",
         sources=["sources/-7Qz7tSTfUU-dylan-field-scaling-figma-and-the-future-of-design.md",
                  "sources/4UE4e6b2qtA-figma-s-dylan-field-exploring-the-idea-maze-vibe-coding-and-the-power-of-locking-in.md",
                  "sources/Rb3QHKjOWqQ-figma-s-20b-10-year-overnight-success.md"],
         grep=r"dylan field"),
    dict(q="What does 'default alive' mean and how do I tell if my startup is?",
         entry="topics/default-alive.md",
         sources=["sources/pg-default-alive-or-default-dead-default-alive-or-default-dead.md",
                  "sources/ANrzH3ra8e8-reham-fagiri-and-kalam-dennis-at-startup-school-sv-2016.md",
                  "sources/khY3REOst-A-startup-next-steps-after-raising-your-first-million-from-a-forbes-top-100-vc-office-hours-.md"],
         grep=r"default alive"),
]
out = []
for x in Q:
    srcs = []
    for s in x["sources"]:
        m = glob.glob(W + s.replace(".md", "") + "*.md")
        assert len(m) == 1, (s, m)
        srcs.append(m[0][len(W):])
    wiki_tokens = tok(W + x["entry"]) + sum(tok(W + s) for s in srcs)
    raws = [raw_for(s) for s in srcs]
    raw_tokens = sum(tok(r) for r in raws)
    n, gt = grep_raw(x["grep"])
    out.append(dict(question=x["q"], entry_page=x["entry"], entry_tokens=tok(W + x["entry"]),
                    source_pages=srcs, source_page_tokens=[tok(W + s) for s in srcs],
                    raw_files=[os.path.relpath(r, ROOT) for r in raws], raw_file_tokens=[tok(r) for r in raws],
                    wiki_path_tokens=wiki_tokens, raw_same_sources_tokens=raw_tokens,
                    ratio_raw_over_wiki=round(raw_tokens / wiki_tokens, 2),
                    naive_raw_grep=dict(pattern=x["grep"], files_matched=n, tokens_in_matched_files=gt)))
agg_w = sum(o["wiki_path_tokens"] for o in out); agg_r = sum(o["raw_same_sources_tokens"] for o in out)
res = dict(encoding="o200k_base", method="wiki path = entry topic/entity page + 3 source pages; raw path = the 3 raw files behind those same source pages (best case for raw: agent already knows which files)",
           questions=out, total_wiki_tokens=agg_w, total_raw_tokens=agg_r, aggregate_ratio=round(agg_r / agg_w, 2),
           median_per_question_ratio=statistics.median(o["ratio_raw_over_wiki"] for o in out))
json.dump(res, open(os.path.join(os.path.dirname(__file__), "stats_lookup.json"), "w"), indent=2)
print(json.dumps(res, indent=1))
