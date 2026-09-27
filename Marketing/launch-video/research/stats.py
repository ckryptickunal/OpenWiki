# ruff: noqa  (one-off measurement script for the launch film; see ../FACTS.md)
import json, os, re, statistics, subprocess, collections
import tiktoken

ROOT = os.environ.get("FOUNDER_BOOK", "Founder-Book")  # path to a clone of ckryptickunal/Founder-Book
enc = tiktoken.get_encoding("o200k_base")
enc_cl = tiktoken.get_encoding("cl100k_base")
tok = lambda s: len(enc.encode(s, disallowed_special=()))
tok_cl = lambda s: len(enc_cl.encode(s, disallowed_special=()))

tracked = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True, text=True).stdout.splitlines()
RAW_DIRS = ["Paul Graham", "Sam Altman", "Garry Tan", "Y Combinator", "YC Root Access"]
raw_files = sorted(f for f in tracked if f.split("/")[0] in RAW_DIRS and f.endswith(".txt"))
wiki_files = sorted(f for f in tracked if f.startswith("wiki/") and f.endswith(".md"))

def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8", errors="replace") as fh:
        return fh.read()

def iso_dur(s):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s.strip())
    if not m:
        return None
    d, h, mi, se = (int(x) if x else 0 for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + se

SEP = "=" * 60
raw = {}
for f in raw_files:
    t = read(f)
    hdr = {}
    for line in t.split("\n")[:40]:
        m = re.match(r"^([A-Za-z ]+):\s*(.*)$", line)
        if m and m.group(1) not in hdr:
            hdr[m.group(1)] = m.group(2)
        if line.strip() == SEP:
            break
    if "\nTRANSCRIPT\n" in t:
        body = t.split("\nTRANSCRIPT\n", 1)[1].split(SEP, 1)[-1]
    else:
        body = t.split(SEP, 1)[-1]
    raw[f] = dict(folder=f.split("/")[0], vid=hdr.get("Video ID"), channel=hdr.get("Channel"),
                  title=hdr.get("Title"), dur=iso_dur(hdr["Duration"]) if "Duration" in hdr else None,
                  words=len(body.split()), tokens=tok(t), body_tokens=tok(body), text=t)

# --- corpus
by_folder = collections.Counter(r["folder"] for r in raw.values())
by_channel = collections.Counter(r["channel"] for r in raw.values())
yt = [r for r in raw.values() if r["folder"] in ("Garry Tan", "Y Combinator", "YC Root Access")]
essays = [r for r in raw.values() if r["folder"] in ("Paul Graham", "Sam Altman")]
vids = collections.Counter(r["vid"] for r in yt)
dup_vids = {v: c for v, c in vids.items() if c > 1}
# unique-video duration (count each video id once)
seen, dur_total, dur_known = set(), 0, 0
for r in yt:
    if r["vid"] in seen:
        continue
    seen.add(r["vid"])
    if r["dur"] is not None:
        dur_total += r["dur"]; dur_known += 1
essay_titles = collections.Counter((r["folder"], (r["title"] or "").strip().lower()) for r in essays)
corpus = dict(
    raw_files_tracked=len(raw_files),
    by_folder=dict(by_folder),
    by_channel_header=dict(by_channel),
    youtube_files=len(yt), youtube_unique_video_ids=len(vids), duplicate_video_ids_across_files=len(dup_vids),
    youtube_unique_with_duration=dur_known, youtube_unique_without_duration=len(vids) - dur_known,
    transcript_seconds_known=dur_total, transcript_hours_known=round(dur_total / 3600, 2),
    essay_files=len(essays), essay_files_pg=by_folder["Paul Graham"], essay_files_sa=by_folder["Sam Altman"],
    essay_duplicate_titles=sum(c - 1 for c in essay_titles.values() if c > 1),
    raw_words_body=sum(r["words"] for r in raw.values()),
    raw_words_youtube=sum(r["words"] for r in yt), raw_words_essays=sum(r["words"] for r in essays),
    raw_chars=sum(len(r["text"]) for r in raw.values()),
)

# --- wiki
LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
wiki = {}
for f in wiki_files:
    t = read(f)
    m = re.search(r"^type:\s*(\S+)", t, re.M)
    wiki[f] = dict(text=t, type=m.group(1) if m else None, links=[x.strip() for x in LINK.findall(t)])
existing = {f[len("wiki/"):-3] for f in wiki_files}
all_links = [l for w in wiki.values() for l in w["links"]]
content_pages = {f: w for f, w in wiki.items() if f not in ("wiki/index.md", "wiki/schema.md")}
content_links = [l for w in content_pages.values() for l in w["links"]]
backlinks = collections.defaultdict(set)
for f, w in content_pages.items():
    for l in set(w["links"]):
        backlinks[l].add(f)
def top(prefix, n=10):
    items = [(k, len(v)) for k, v in backlinks.items() if k.startswith(prefix)]
    items.sort(key=lambda x: -x[1])
    out = []
    for k, c in items[:n]:
        p = f"wiki/{k}.md"
        title = re.search(r"^title:\s*(.*)$", wiki[p]["text"], re.M).group(1) if p in wiki else None
        out.append(dict(target=k, title=title, backlinking_pages=c))
    return out
wiki_stats = dict(
    tracked_md_files=len(wiki_files),
    by_folder=dict(collections.Counter(f.split("/")[1] if f.count("/") > 1 else f for f in wiki_files)),
    by_frontmatter_type=dict(collections.Counter(w["type"] for w in wiki.values())),
    wikilinks_total_all_files=len(all_links),
    wikilinks_total_excluding_index=len(content_links),
    wikilinks_in_index=len(wiki["wiki/index.md"]["links"]),
    unique_link_targets_all=len(set(all_links)),
    unique_link_targets_excluding_index=len(set(content_links)),
    unique_targets_resolving_to_a_page=len(set(all_links) & existing),
    unique_targets_unresolved=len(set(all_links) - existing),
    pages_with_zero_inbound_links_excl_index=len(existing - set(backlinks) - {"index", "schema"}),
    top10_entities_by_backlinks=top("entities/"),
    top10_topics_by_backlinks=top("topics/"),
    wiki_words=sum(len(w["text"].split()) for w in wiki.values()),
)

# --- tokens
raw_all = "".join(r["text"] for r in raw.values())
wiki_all = "".join(w["text"] for w in wiki.values())
tokens = dict(
    encoding_primary="o200k_base",
    raw_corpus_tokens_o200k=sum(r["tokens"] for r in raw.values()),
    raw_corpus_body_only_tokens_o200k=sum(r["body_tokens"] for r in raw.values()),
    wiki_tokens_o200k=sum(tok(w["text"]) for w in wiki.values()),
    wiki_tokens_by_folder_o200k={k: sum(tok(w["text"]) for f, w in wiki.items() if (f.split("/")[1] if f.count("/") > 1 else f) == k)
                                 for k in wiki_stats["by_folder"]},
    index_md_tokens_o200k=tok(wiki["wiki/index.md"]["text"]),
    raw_corpus_tokens_cl100k=tok_cl(raw_all),
    wiki_tokens_cl100k=tok_cl(wiki_all),
)

# --- per-source ratio
vid_to_raw = collections.defaultdict(list)
for f, r in raw.items():
    vid_to_raw[r["vid"]].append(f)
src_by_vid = collections.defaultdict(list)
for f, w in wiki.items():
    if w["type"] == "source":
        m = re.search(r"^video_id:\s*(.*)$", w["text"], re.M)
        if m:
            src_by_vid[m.group(1).strip().strip("'\"")].append(f)
ratios, pairs = [], []
for vid, rfs in vid_to_raw.items():
    if vid not in src_by_vid:
        continue
    rt = max(raw[x]["tokens"] for x in rfs)
    st = max(tok(wiki[s]["text"]) for s in src_by_vid[vid])  # conservative: largest page
    ratios.append(rt / st); pairs.append((vid, rt, st))
yt_r = [rt / st for v, rt, st in pairs if not (v.startswith("pg-") or v.startswith("sa-"))]
es_r = [rt / st for v, rt, st in pairs if v.startswith("pg-") or v.startswith("sa-")]
q = statistics.quantiles(ratios, n=4)
per_source = dict(
    raw_ids_with_source_page=len(pairs), raw_ids_total=len(vid_to_raw),
    source_pages_total=sum(1 for w in wiki.values() if w["type"] == "source"),
    video_ids_with_multiple_source_pages=sum(1 for v in src_by_vid.values() if len(v) > 1),
    median_raw_to_source_ratio=round(statistics.median(ratios), 2),
    p25=round(q[0], 2), p75=round(q[2], 2), min=round(min(ratios), 2), max=round(max(ratios), 2),
    median_ratio_youtube=round(statistics.median(yt_r), 2), n_youtube=len(yt_r),
    median_ratio_essays=round(statistics.median(es_r), 2), n_essays=len(es_r),
    share_where_source_page_is_larger_than_raw=round(sum(1 for x in ratios if x < 1) / len(ratios), 3),
    median_raw_tokens=statistics.median(p[1] for p in pairs), median_source_page_tokens=statistics.median(p[2] for p in pairs),
)

out = dict(corpus=corpus, wiki=wiki_stats, tokens=tokens, per_source=per_source)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "stats_part1.json"), "w"), indent=2)
print(json.dumps(out, indent=2))
