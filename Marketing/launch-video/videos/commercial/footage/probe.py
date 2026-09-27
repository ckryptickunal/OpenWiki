import json, subprocess, urllib.request
from concurrent.futures import ThreadPoolExecutor
UA={"User-Agent":"Mozilla/5.0"}
S=json.load(open("search.json"))
def head(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u,method="HEAD",headers=UA),timeout=20) as r: return r.status==200
    except Exception: return False
def probe(item):
    cat,i=item; base=f"https://videos.pexels.com/video-files/{i}/{i}"
    sd=next((f"{base}-sd_640_360_{f}fps.mp4" for f in (25,30,24,60,50) if head(f"{base}-sd_640_360_{f}fps.mp4")),None)
    hd=next((f"{base}-hd_1920_1080_{f}fps.mp4" for f in (25,30,24,60,50) if head(f"{base}-hd_1920_1080_{f}fps.mp4")),None)
    if sd:
        subprocess.run(["ffmpeg","-v","error","-y","-ss","3","-i",sd,"-frames:v","1","-vf","scale=320:180",f"th/{cat}-{i}.jpg"])
    return cat,i,sd,hd
import os; os.makedirs("th",exist_ok=True)
items=[(c,i) for c,l in S.items() for i in l]
with ThreadPoolExecutor(16) as ex: res=list(ex.map(probe,items))
json.dump([r for r in res],open("probe.json","w"),indent=0)
print(sum(1 for r in res if r[3]),"with hd of",len(res))
