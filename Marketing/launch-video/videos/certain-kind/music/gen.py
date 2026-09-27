# Generate instrumental candidates with Lyria 3.5 (Gemini API, interactions endpoint).
# Reads GEMINI_API_KEY from the environment; never prints it.
import base64, json, os, sys, urllib.request
KEY = os.environ["GEMINI_API_KEY"]
PROMPT = open(os.path.join(os.path.dirname(__file__), "prompt.txt")).read()
def run(tag):
    body = json.dumps({"model": "lyria-3.5", "input": PROMPT}).encode()
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions", data=body,
        headers={"x-goog-api-key": KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.load(r)
    n = 0
    def walk(o):
        nonlocal n
        if isinstance(o, dict):
            if o.get("type") == "audio" and o.get("data"):
                n += 1
                ext = "wav" if "wav" in o.get("mime_type", "") else "mp3"
                path = os.path.join(os.path.dirname(__file__), f"take-{tag}-{n}.{ext}")
                open(path, "wb").write(base64.b64decode(o["data"])); print("wrote", path, o.get("mime_type"))
            elif o.get("type") == "text" and o.get("text"):
                print("text:", o["text"][:600])
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(d)
    if not n: print(json.dumps(d)[:1500])
run(sys.argv[1] if len(sys.argv) > 1 else "a")
