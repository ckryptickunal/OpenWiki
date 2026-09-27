// Scene 6 (22.0-26.5): the real link graph of Founder Book — 8,653 connected pages, 15,699 page-to-page links,
// force-directed layout computed offline from its [[wikilinks]]. Drawn on canvas from a timeline proxy.
FILM.scene(function (tl) {
  const G = window.GRAPH, F = FACTS;
  const cv = FILM.$("#g-canvas"), ctx = cv.getContext("2d");
  const CX = 960, CY = 560, RAD = 520;
  const n = G.n, xs = G.x, ys = G.y, E = G.edges;
  const rr = new Float32Array(n);
  for (let i = 0; i < n; i++) rr[i] = Math.hypot(xs[i], ys[i]);
  const size = G.d.map((d) => 1.1 + Math.sqrt(Math.min(d, 400)) * 0.32);
  const COL = ["#faf6f2", "#f5c451", "#e5895a"]; // sources, entities, topics

  const S = { reveal: 0, edges: 0, rot: 0, zoom: 1.3 };
  const proj = (i) => {
    const c = Math.cos(S.rot), s = Math.sin(S.rot);
    const x = xs[i] * c - ys[i] * s, y = xs[i] * s + ys[i] * c;
    return [CX + x * RAD * S.zoom, CY + y * RAD * S.zoom];
  };
  const P = new Float32Array(n * 2);
  function draw() {
    ctx.clearRect(0, 0, 1920, 1080);
    for (let i = 0; i < n; i++) { const p = proj(i); P[2 * i] = p[0]; P[2 * i + 1] = p[1]; }
    const R = S.reveal * 1.05;
    // links
    if (S.edges > 0) {
      ctx.lineWidth = 0.6;
      ctx.strokeStyle = `rgba(245,196,81,${0.075 * S.edges})`;
      ctx.beginPath();
      for (let k = 0; k < E.length; k += 2) {
        const a = E[k], b = E[k + 1];
        if (rr[a] > R || rr[b] > R) continue;
        ctx.moveTo(P[2 * a], P[2 * a + 1]); ctx.lineTo(P[2 * b], P[2 * b + 1]);
      }
      ctx.stroke();
    }
    // nodes: each pops in as the reveal front passes it
    for (let t = 0; t < 3; t++) {
      ctx.fillStyle = COL[t];
      ctx.beginPath();
      for (let i = 0; i < n; i++) {
        if (G.t[i] !== t) continue;
        const k = (R - rr[i]) / 0.08; if (k <= 0) continue;
        const s = size[i] * S.zoom * 0.8 * Math.min(1, k) * (k < 1 ? 1 + (1 - k) * 0.8 : 1);
        ctx.moveTo(P[2 * i] + s, P[2 * i + 1]); ctx.arc(P[2 * i], P[2 * i + 1], s, 0, Math.PI * 2);
      }
      ctx.fill();
    }
  }
  const upd = () => { draw(); placeLabels(); };

  // hub labels (real page names and how many pages link to them)
  const hubs = [["entities/y-combinator", "Y Combinator", 945], ["entities/paul-graham", "Paul Graham", 336], ["entities/sam-altman", "Sam Altman", 187],
    ["entities/garry-tan", "Garry Tan", 175], ["entities/figma", "Figma", 19], ["entities/dylan-field", "Dylan Field", 4]];
  const idx = {}; Object.entries(G.labels).forEach(([i, slug]) => (idx[slug] = +i));
  const box = FILM.$("#g-labels");
  const labels = hubs.map(([slug, name, links]) => {
    const d = document.createElement("div"); d.className = "gl";
    d.innerHTML = `${name}<b>${links}</b>`; box.appendChild(d);
    return { el: d, i: idx[slug] };
  });
  function placeLabels() {
    labels.forEach((l) => { const p = proj(l.i); l.el.style.left = p[0] + 14 + "px"; l.el.style.top = p[1] - 18 + "px"; });
  }

  // night iris opens from the centre, where the previous scene collapsed
  tl.fromTo("#s6", { clipPath: "circle(0px at 960px 520px)" }, { clipPath: "circle(1300px at 960px 520px)", duration: 0.6, ease: "expo.inOut" }, 22.0);
  tl.fromTo(S, { reveal: 0 }, { reveal: 1, duration: 1.9, ease: "power2.inOut", onUpdate: upd }, 22.1);
  tl.fromTo(S, { edges: 0 }, { edges: 1, duration: 1.6, ease: "power1.in", onUpdate: upd }, 22.5);
  tl.fromTo(S, { rot: -0.25, zoom: 1.35 }, { rot: 0.12, zoom: 0.92, duration: 4.5, ease: "sine.out", onUpdate: upd }, 22.0);
  gsap.set(labels.map((l) => l.el), { opacity: 0 });
  labels.forEach((l, k) => tl.fromTo(l.el, { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)", transformOrigin: "0% 50%" }, 23.3 + k * 0.12));

  // title and real counts
  tl.fromTo("#s6-top .kick-top", { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.4 }, 22.45);
  const tw = FILM.words("#s6-title");
  FILM.inkIn(tl, tw, 22.5, { stagger: 0.08, dur: 0.6, swell: "#s6-title" });
  tl.fromTo("#s6-stats .st", { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: "expo.out", stagger: 0.1 }, 22.9);
  FILM.count(tl, "#s6-v", 0, F.videos, 22.95, 1.2);
  FILM.count(tl, "#s6-e", 0, F.essays, 23.05, 1.1);
  FILM.count(tl, "#s6-p", 0, F.pages, 23.25, 1.4);
  tl.fromTo("#s6-foot", { opacity: 0 }, { opacity: 1, duration: 0.4 }, 23.9);
});
