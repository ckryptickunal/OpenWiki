// Scene 6 (30.0-35.6): Founder Book's real link graph (8,653 connected pages, 15,699 page-to-page links,
// laid out offline from its [[wikilinks]]) rendered as a Revolut-style planet horizon under a balance-style number.
FILM.scene(function (tl) {
  const G = window.GRAPH, F = FACTS;
  const cv = FILM.$("#g-canvas"), ctx = cv.getContext("2d");
  const CX = 960, CY = 1330, RAD = 760; // the top of the disc forms the horizon
  const n = G.n, xs = G.x, ys = G.y, E = G.edges;
  // reveal from the rim inward: the rim is what the horizon shows
  const rr = new Float32Array(n); for (let i = 0; i < n; i++) rr[i] = 1 - Math.min(1, Math.hypot(xs[i], ys[i]));
  const size = G.d.map((d) => 1.2 + Math.sqrt(Math.min(d, 400)) * 0.3);
  const COL = ["rgba(255,255,255,0.9)", "#6f86ff", "#a48bff"];
  const S = { reveal: 0, edges: 0, rot: 0 };
  const P = new Float32Array(n * 2);
  function draw() {
    ctx.clearRect(0, 0, 1920, 1080);
    const c = Math.cos(S.rot), s = Math.sin(S.rot);
    for (let i = 0; i < n; i++) { P[2 * i] = CX + (xs[i] * c - ys[i] * s) * RAD; P[2 * i + 1] = CY + (xs[i] * s + ys[i] * c) * RAD; }
    const R = S.reveal * 1.04;
    if (S.edges > 0) {
      ctx.lineWidth = 0.7; ctx.strokeStyle = `rgba(111,134,255,${0.09 * S.edges})`; ctx.beginPath();
      for (let k = 0; k < E.length; k += 2) { const a = E[k], b = E[k + 1]; if (rr[a] > R || rr[b] > R) continue;
        ctx.moveTo(P[2 * a], P[2 * a + 1]); ctx.lineTo(P[2 * b], P[2 * b + 1]); }
      ctx.stroke();
    }
    for (let t = 0; t < 3; t++) {
      ctx.fillStyle = COL[t]; ctx.beginPath();
      for (let i = 0; i < n; i++) { if (G.t[i] !== t) continue; const k = (R - rr[i]) / 0.1; if (k <= 0) continue;
        const r = size[i] * Math.min(1, k); ctx.moveTo(P[2 * i] + r, P[2 * i + 1]); ctx.arc(P[2 * i], P[2 * i + 1], r, 0, Math.PI * 2); }
      ctx.fill();
    }
  }
  // the hub pages sit at the centre of the disc, below the horizon, so no labels here
  const hubs = [];
  const idx = {}; Object.entries(G.labels).forEach(([i, slug]) => (idx[slug] = +i));
  const box = FILM.$("#g-labels");
  const labels = hubs.map(([slug, name, links]) => { const d = document.createElement("div"); d.className = "gl"; d.innerHTML = `${name}<b>${links}</b>`; box.appendChild(d); return { el: d, i: idx[slug] }; });
  const place = () => labels.forEach((l) => { const x = P[2 * l.i], y = P[2 * l.i + 1]; l.el.style.left = x + 12 + "px"; l.el.style.top = y - 20 + "px"; l.el.style.visibility = y > 640 && y < 1040 && x > 60 && x < 1760 ? "visible" : "hidden"; });
  const upd = () => { draw(); place(); };

  tl.fromTo("#s6-arc", { opacity: 0, y: 80 }, { opacity: 1, y: 0, duration: 1.4, ease: "out" }, 30.0);
  tl.fromTo(S, { reveal: 0 }, { reveal: 1, duration: 2.6, ease: "out", onUpdate: upd }, 30.1);
  tl.fromTo(S, { edges: 0 }, { edges: 1, duration: 2.0, ease: "inOut", onUpdate: upd }, 30.6);
  tl.fromTo(S, { rot: -0.18 }, { rot: 0.06, duration: 5.6, ease: "none", onUpdate: upd }, 30.0);
  gsap.set(labels.map((l) => l.el), { opacity: 0 });
  labels.forEach((l, k) => tl.fromTo(l.el, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.6, ease: "out" }, 32.2 + k * 0.08));

  FILM.appear(tl, "#s6-lbl", 30.5, { y: 12, dur: 0.8 });
  FILM.appear(tl, "#s6-num", 30.65, { y: 24, dur: 0.9 });
  FILM.count(tl, "#s6-num", 0, F.pages, 30.65, 1.8);
  FILM.appear(tl, "#s6-pill", 31.0, { y: 14, dur: 0.8 });
  FILM.appear(tl, "#s6-sub", 31.3, { y: 12, dur: 0.8 });

  FILM.vanish(tl, ["#s6-lbl", "#s6-num", "#s6-pill", "#s6-sub", "#g-labels"], 35.2, { dur: 0.35 });
  tl.to(["#g-canvas", "#s6-arc"], { opacity: 0, duration: 0.4, ease: "exit" }, 35.2);
});
