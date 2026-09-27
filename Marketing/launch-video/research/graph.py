# ruff: noqa  (one-off measurement script for the launch film; see ../FACTS.md)
import re, json, os, math, collections
import igraph as ig
root=os.path.join(os.environ.get("FOUNDER_BOOK", "Founder-Book"), "wiki")
link=re.compile(r"\[\[([^\]|#]+)")
nodes={}; edges=set()
for d in ["sources","entities","topics"]:
    for f in os.listdir(os.path.join(root,d)):
        if f.endswith(".md"): nodes[f"{d}/{f[:-3]}"]=d
idx={k:i for i,k in enumerate(nodes)}
for k,d in nodes.items():
    t=open(os.path.join(root,k+".md"),encoding="utf-8",errors="ignore").read()
    for m in link.findall(t):
        m=m.strip().removesuffix(".md")
        if m in idx and m!=k: edges.add(tuple(sorted((idx[k],idx[m]))))
g=ig.Graph(n=len(nodes),edges=list(edges))
deg=g.degree()
# keep the giant component so the picture reads as one brain
comp=g.connected_components().giant()
keep=[v["name"] if "name" in v.attributes() else None for v in comp.vs]
print("nodes",len(nodes),"edges",len(edges),"giant",comp.vcount(),comp.ecount())
import random; random.seed(7)
lay=comp.layout_fruchterman_reingold(niter=900, grid="grid", seed=[[random.uniform(-1,1)*90,random.uniform(-1,1)*90] for _ in range(comp.vcount())])
xs=[p[0] for p in lay]; ys=[p[1] for p in lay]
# normalise into a unit disc-ish box, centred
cx=sorted(xs)[len(xs)//2]; cy=sorted(ys)[len(ys)//2]
r=sorted(math.hypot(x-cx,y-cy) for x,y in zip(xs,ys))[int(len(xs)*0.97)]
types=list(nodes.values())
orig=[i for i in range(g.vcount())]
# map giant-component vertex -> original index
gi=g.connected_components().giant_component if False else None
members=max(g.connected_components(), key=len)
# equalise density: keep each node's angle, remap radius by rank so the disc fills evenly
import bisect
rs=[math.hypot(x-cx,y-cy) for x,y in zip(xs,ys)]; order=sorted(range(len(rs)),key=lambda i:rs[i])
rank=[0]*len(rs)
for k,i in enumerate(order): rank[i]=k/len(rs)
nx=[];ny=[]
for i,(x,y) in enumerate(zip(xs,ys)):
    a=math.atan2(y-cy,x-cx); rr=rank[i]**0.62
    nx.append(cx+math.cos(a)*rr*r); ny.append(cy+math.sin(a)*rr*r)
xs,ys=nx,ny
out={"n":comp.vcount(),"e":comp.ecount(),
 "x":[round((x-cx)/r,4) for x in xs],"y":[round((y-cy)/r,4) for y in ys],
 "t":["sources entities topics".split().index(types[members[i]]) for i in range(comp.vcount())],
 "d":comp.degree(),
 "edges":[c for e in comp.get_edgelist() for c in e],
 "labels":{str(i):list(nodes)[members[i]] for i in range(comp.vcount()) if list(nodes)[members[i]] in ("entities/y-combinator","entities/paul-graham","entities/sam-altman","entities/garry-tan","entities/airbnb","topics/product-market-fit","entities/figma","entities/dylan-field","topics/entrepreneurship","entities/stripe","entities/openai")},
 "total_pages":len(nodes),"total_edges":len(edges)}
json.dump(out,open(os.path.join(os.path.dirname(__file__), "..", "assets", "data", "graph.json"),"w"),separators=(",",":"))
print("top degree:",sorted(zip(comp.degree(),[list(nodes)[members[i]] for i in range(comp.vcount())]))[-8:])
