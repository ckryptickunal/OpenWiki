"""Write index.html (a HyperFrames composition) from the shot list below.

"A certain kind of person": black-and-white photographs, one quiet line of text per shot,
cut on the music (Lyria 3.5 take-b, ~90 BPM: build 10.08 s, drop 21.08 s, break 43.2 s,
final hit 53.4 s, end 61.6 s). Run: python3 build.py
"""

END = 61.6
HIT = 53.4

# (start, photo or "graph", line or None, drift direction)
SHOTS = [
    (0.00, "win2", "there’s a certain kind of person", 1),
    (3.41, "night1", "who watches the whole talk", -1),
    (6.75, "read3", "who reads the essay twice", 1),
    (10.08, "write2", "who writes it all down at 2 a.m.", -1),
    (12.74, "note3", "and can’t find it by morning", 1),
    (15.41, "win1", "who remembers the idea", -1),
    (18.08, "night4", "but not where it was", 1),
    (21.08, "code3", "who builds with an AI beside them", -1),
    (23.41, "lamp2", None, 1),
    (24.74, "code2", "and wants it to know what they know", -1),
    (26.74, "mic5", "every talk.", 1),
    (28.74, "lect3", None, -1),
    (29.41, "read2", "every essay.", 1),
    (30.41, "paper1", None, -1),
    (31.41, "write1", "every note.", 1),
    (33.74, "note5", None, -1),
    (34.41, "graph", None, 1),
    (40.74, "lib4", None, -1),
    (43.20, "win4", "for the ones who keep learning", 1),
    (48.30, "lib7", None, -1),
]
# lines that sit on the graph shot, appearing word by word on the beat
# bright photos get a flat dark layer so the line stays readable
DARKEN = {"read2": 0.42, "paper1": 0.25}
GRAPH_LINES = [(34.9, "becomes a page."), (37.41, "linked."), (38.07, "searchable."), (39.40, "yours.")]


def main():
    shots = SHOTS
    ends = [s[0] for s in shots[1:]] + [HIT]
    sections, script = [], []
    for i, ((t0, what, line, drift), t1) in enumerate(zip(shots, ends)):
        dur = round(t1 - t0, 3)
        sid = f"s{i}"
        if what == "graph":
            body = '<canvas id="g" width="1920" height="1080"></canvas>'
        elif what == "lib7":
            body = ""  # the last beat before the logo is black: only the line
        else:
            body = f'<img class="photo" id="p{i}" src="assets/photos/{what}.jpg" alt="" />'
            if what in DARKEN:
                body += f'<div style="position:absolute;inset:0;background:rgba(0,0,0,{DARKEN[what]})"></div>'
        text = ""
        if line:
            text = f'<div class="line" id="l{i}">{line}</div>'
        if what == "graph":
            text = '<div class="line" id="lg">' + " ".join(
                f'<span class="gw" id="gw{k}">{w}</span>' for k, (_, w) in enumerate(GRAPH_LINES)) + "</div>"
        if what == "lib7":
            text = '<div class="line center" id="l{0}">and never want to lose a thing</div>'.format(i)
        sections.append(
            f'      <section id="{sid}" class="clip scene" data-start="{t0}" data-duration="{dur}" data-track-index="0">\n'
            f"        {body}\n        {text}\n      </section>")
        if what not in ("graph", "lib7"):
            script.append(f'  push(tl, "#p{i}", {t0}, {dur}, {drift});')
        if line and what != "lib7":
            script.append(f'  lineIn(tl, "#l{i}", {t0} + {0.9 if i == 0 else 0.35}, {t1});')
        if what == "lib7":
            script.append(f'  lineIn(tl, "#l{i}", {t0} + 0.6, {t1});')
        if what == "graph":
            script.append(f"  graph(tl, {t0}, {dur});")
            for k, (tw, _) in enumerate(GRAPH_LINES):
                script.append(f'  wordIn(tl, "#gw{k}", {tw});')
            script.append(f'  tl.to("#lg", {{ opacity: 0, duration: 0.3, ease: "power1.in" }}, {t1} - 0.35);')

    html = TEMPLATE.replace("%SECTIONS%", "\n".join(sections)).replace("%SCRIPT%", "\n".join(script))
    html = html.replace("%END%", str(END)).replace("%HIT%", str(HIT)).replace("%ENDLEN%", str(round(END - HIT, 3)))
    open("index.html", "w").write(html)
    print("wrote index.html", len(shots), "shots")


TEMPLATE = """<!doctype html>
<html lang="en" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>A certain kind of person</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Inter Display"; src: url("assets/fonts/inter-display-latin-600-normal.woff2") format("woff2"); font-weight: 600; }
      @font-face { font-family: "Inter Display"; src: url("assets/fonts/inter-display-latin-700-normal.woff2") format("woff2"); font-weight: 700; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1920px; height: 1080px; overflow: hidden; background: #000; }
      #root { position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #000; font-family: "Inter Display", sans-serif; -webkit-font-smoothing: antialiased; }
      .scene { position: absolute; inset: 0; overflow: hidden; background: #000; }
      .photo { position: absolute; left: -144px; top: -81px; width: 2208px; height: 1242px; transform-origin: 50% 50%; }
      canvas { position: absolute; inset: 0; }
      .scene::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 480px; background: linear-gradient(180deg, rgba(0,0,0,0), rgba(0,0,0,.72)); pointer-events: none; }
      .line { position: absolute; left: 128px; bottom: 112px; z-index: 2; font: 600 46px/1.2 "Inter Display"; letter-spacing: -0.012em; color: rgba(255,255,255,.94); opacity: 0; text-shadow: 0 2px 24px rgba(0,0,0,.35); }
      .line.center { left: 0; right: 0; bottom: auto; top: 50%; transform: translateY(-50%); text-align: center; }
      #lg { opacity: 1; }
      .gw { display: inline-block; opacity: 0; margin-right: 0.28em; }
      #end { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #000; }
      .tile { width: 132px; height: 132px; border-radius: 30px; background: linear-gradient(180deg, #2a2a2a, #0d0d0d); box-shadow: inset 0 1px 0 rgba(255,255,255,.1), 0 0 0 1px rgba(255,255,255,.06); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; }
      .tile b { font-weight: 700; line-height: 1; background: linear-gradient(180deg, #f4f4f4, #b8b8b8); -webkit-background-clip: text; background-clip: text; color: transparent; }
      .tile .a1 { font-size: 34px; } .tile .a2 { font-size: 50px; letter-spacing: -0.02em; }
      .word { margin-top: 34px; font: 700 64px/1 "Inter Display"; letter-spacing: -0.03em; color: #fff; }
      .tag { margin-top: 22px; font: 600 30px/1.2 "Inter Display"; color: rgba(255,255,255,.72); letter-spacing: -0.005em; }
      .url { position: absolute; bottom: 96px; left: 0; right: 0; text-align: center; font: 600 22px/1 "Inter Display"; color: rgba(255,255,255,.5); letter-spacing: 0.01em; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="%END%" data-width="1920" data-height="1080">
%SECTIONS%
      <section id="send" class="clip scene" data-start="%HIT%" data-duration="%ENDLEN%" data-track-index="0">
        <div id="end">
          <div class="tile" id="tile"><b class="a1">&gt;</b><b class="a2">OW</b></div>
          <div class="word" id="word">OpenWiki</div>
          <div class="tag" id="tag">turn what you watch into what you know.</div>
        </div>
        <div class="url" id="url">free and open source · github.com/ckryptickunal/OpenWiki</div>
      </section>
      <div id="fade" style="position:absolute;inset:0;background:#000;opacity:0;z-index:9"></div>
    </div>

    <script src="assets/js/graph-data.js"></script>
    <script>
      const out = "power3.out";
      function push(tl, sel, t0, dur, dir) {
        tl.fromTo(sel, { scale: 1.0, x: -18 * dir }, { scale: 1.07, x: 18 * dir, duration: dur, ease: "none" }, t0);
      }
      function lineIn(tl, sel, at, t1) {
        tl.fromTo(sel, { opacity: 0, y: 12, filter: "blur(6px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.8, ease: out }, at);
        tl.to(sel, { opacity: 0, duration: 0.3, ease: "power1.in" }, t1 - 0.32);
      }
      function wordIn(tl, sel, at) {
        tl.fromTo(sel, { opacity: 0, y: 10, filter: "blur(6px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.6, ease: out }, at);
      }
      function graph(tl, t0, dur) {
        const G = window.GRAPH, cv = document.getElementById("g"), ctx = cv.getContext("2d");
        const n = G.n, E = G.edges, rr = new Float32Array(n);
        for (let i = 0; i < n; i++) rr[i] = Math.hypot(G.x[i], G.y[i]);
        const size = G.d.map((d) => 0.8 + Math.sqrt(Math.min(d, 400)) * 0.22);
        const S = { reveal: 0, edges: 0, rot: -0.1, zoom: 0.92 }, P = new Float32Array(n * 2);
        const draw = () => {
          ctx.clearRect(0, 0, 1920, 1080);
          const c = Math.cos(S.rot), s = Math.sin(S.rot), R = S.reveal * 1.05, RAD = 430 * S.zoom;
          for (let i = 0; i < n; i++) { P[2*i] = 960 + (G.x[i]*c - G.y[i]*s) * RAD; P[2*i+1] = 500 + (G.x[i]*s + G.y[i]*c) * RAD; }
          if (S.edges > 0) { ctx.lineWidth = 0.6; ctx.strokeStyle = `rgba(255,255,255,${0.07 * S.edges})`; ctx.beginPath();
            for (let k = 0; k < E.length; k += 2) { const a = E[k], b = E[k+1]; if (rr[a] > R || rr[b] > R) continue; ctx.moveTo(P[2*a], P[2*a+1]); ctx.lineTo(P[2*b], P[2*b+1]); }
            ctx.stroke(); }
          ctx.fillStyle = "rgba(255,255,255,0.9)"; ctx.beginPath();
          for (let i = 0; i < n; i++) { const k = (R - rr[i]) / 0.08; if (k <= 0) continue; const r = size[i] * Math.min(1, k);
            ctx.moveTo(P[2*i] + r, P[2*i+1]); ctx.arc(P[2*i], P[2*i+1], r, 0, Math.PI * 2); }
          ctx.fill();
        };
        tl.fromTo(S, { reveal: 0 }, { reveal: 1, duration: 2.6, ease: "power2.inOut", onUpdate: draw }, t0);
        tl.fromTo(S, { edges: 0 }, { edges: 1, duration: 2.4, ease: "power1.inOut", onUpdate: draw }, t0 + 0.4);
        tl.fromTo(S, { rot: -0.1, zoom: 0.92 }, { rot: 0.06, zoom: 1.08, duration: dur, ease: "none", onUpdate: draw }, t0);
      }
      document.fonts.load('600 46px "Inter Display"').then(() => document.fonts.load('700 64px "Inter Display"')).then(() => {
        const tl = gsap.timeline({ paused: true });
%SCRIPT%
        // end card on the final hit
        tl.fromTo("#tile", { opacity: 0, scale: 0.94, filter: "blur(8px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 1.4, ease: out }, %HIT% + 0.05);
        tl.fromTo("#word", { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 1.2, ease: out }, %HIT% + 0.7);
        tl.fromTo("#tag", { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 1.2, ease: out }, %HIT% + 2.2);
        tl.fromTo("#url", { opacity: 0 }, { opacity: 1, duration: 1.2, ease: "power1.out" }, %HIT% + 3.6);
        tl.fromTo("#end", { scale: 1 }, { scale: 1.025, duration: %ENDLEN%, ease: "none" }, %HIT%);
        tl.to("#fade", { opacity: 1, duration: 1.0, ease: "power1.in" }, %END% - 1.1);
        window.__timelines = window.__timelines || {};
        window.__timelines["main"] = tl;
      });
    </script>
  </body>
</html>
"""

if __name__ == "__main__":
    main()
