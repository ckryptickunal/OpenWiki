# ruff: noqa  (one-off measurement script for the launch film; see ../FACTS.md)
import re, subprocess, json, tiktoken
enc=tiktoken.get_encoding("o200k_base")
files=[f for f in subprocess.check_output(["git","ls-files"],text=True).splitlines() if f.endswith(".txt") and f.split("/")[0] in ("Garry Tan","Paul Graham","Sam Altman","Y Combinator","YC Root Access")]
pat=re.compile(r"don['’]?t scale",re.I)
out=[]
for f in files:
    t=open(f,encoding="utf-8",errors="ignore").read()
    if pat.search(t): out.append([f,len(enc.encode(t))])
print(len(out),sum(n for _,n in out))
json.dump(out,open("naive68.json","w"))
