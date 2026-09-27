// OpenWiki launch film v3 — every on-screen claim is listed with its evidence in CLAIMS.md.
// Pacing: entrances 0.8–0.9s on the "out" curve, moves on "inOut", exits faster than entrances, holds of 1.5s+.
FILM.scene(function (tl) {
  const $ = FILM.$;

  // ---------- A · watched (0–3.2) ----------
  FILM.push(tl, "#pA", 0, 3.2, { from: 1.0, to: 1.05, x: -12 });
  FILM.appear(tl, "#cA", 0.35);
  tl.fromTo("#barA", { scaleX: 0 }, { scaleX: 1, duration: 1.5, ease: "sine.inOut" }, 0.7);
  FILM.rise(tl, FILM.words("#capA"), 0.95);

  // ---------- B · saved (3.2–6.4) ----------
  FILM.push(tl, "#pB", 3.2, 3.2, { from: 1.06, to: 1.0, x: 14 });
  FILM.appear(tl, "#cB", 3.55);
  FILM.rise(tl, FILM.words("#capB"), 4.05);

  // ---------- C · now find it (6.4–10.2) ----------
  FILM.push(tl, "#pC", 6.4, 3.8, { from: 1.0, to: 1.06, y: -10 });
  FILM.appear(tl, "#cC", 6.7);
  const endC = FILM.type(tl, "#tC", 7.05, 0.042);
  [0, 1, 2].forEach((k) => { tl.set("#caretC", { opacity: 0 }, endC + 0.25 + k * 0.5); tl.set("#caretC", { opacity: 1 }, endC + 0.5 + k * 0.5); });
  FILM.rise(tl, FILM.words("#capC"), 8.3);

  // ---------- D · agents too (10.2–13.2) ----------
  FILM.rise(tl, FILM.wordsDeep("#bD"), 10.4, { stagger: 0.07 });
  tl.fromTo("#bD", { scale: 1 }, { scale: 1.025, duration: 3.0, ease: "none" }, 10.2);

  // ---------- E · one idea, 68 files (13.2–17.0) ----------
  FILM.push(tl, "#pE", 13.2, 3.8, { from: 1.04, to: 1.0 });
  FILM.appear(tl, "#cE", 13.5);
  FILM.count(tl, "#nE1", 0, FACTS.naiveFiles, 13.95, 1.4, { ease: "out" });
  FILM.count(tl, "#nE2", 0, FACTS.naiveTokens, 14.05, 1.6, { ease: "out" });
  FILM.rise(tl, FILM.words("#capE"), 14.9);

  // ---------- F · longer inputs (17.0–20.6) ----------
  FILM.rise(tl, FILM.wordsDeep("#bF"), 17.2);
  tl.fromTo("#hlF", { "--hx": 0 }, { "--hx": 1, duration: 0.6, ease: "inOut" }, 18.2);
  FILM.appear(tl, "#fF", 18.4, { y: 8 });

  // ---------- G · compile once (20.6–23.6) ----------
  FILM.rise(tl, FILM.wordsDeep("#bG"), 20.8);
  FILM.appear(tl, "#subG", 21.6, { y: 10 });

  // ---------- H · real commands (23.6–29.0) ----------
  FILM.appear(tl, "#tH", 23.7, { y: 30, dur: 0.9 });
  const lines = ["#lH1", "#oH1", "#lH2", "#oH2", "#lH3", "#oH3", "#lH4"];
  gsap.set(lines, { opacity: 0 });
  tl.set("#lH1", { opacity: 1 }, 24.05);
  const e1 = FILM.type(tl, "#cH1", 24.1, 0.016);
  FILM.appear(tl, "#oH1", e1 + 0.1, { y: 6, dur: 0.5 });
  tl.set("#lH2", { opacity: 1 }, e1 + 0.4);
  const e2 = FILM.type(tl, "#cH2", e1 + 0.45, 0.011);
  FILM.appear(tl, "#oH2", e2 + 0.1, { y: 6, dur: 0.5 });
  tl.set("#lH3", { opacity: 1 }, e2 + 0.4);
  const e3 = FILM.type(tl, "#cH3", e2 + 0.45, 0.035);
  FILM.appear(tl, "#oH3", e3 + 0.35, { y: 6, dur: 0.5 });
  FILM.appear(tl, "#lH4", e3 + 0.55, { y: 6, dur: 0.6 });

  // ---------- I · the real page (29.0–35.2) ----------
  const st = "#stI";
  FILM.appear(tl, "#pgI", 29.1, { y: 30, dur: 0.9 });
  [["#hlI1", 29.9], ["#hlI2", 30.15], ["#hlI3", 30.4], ["#hlI4", 30.65]].forEach(([id, t]) => tl.fromTo(id, { "--hx": 0 }, { "--hx": 1, duration: 0.5, ease: "inOut" }, t));
  const svg = $("#links"), NS = "http://www.w3.org/2000/svg";
  [["#hlI1", "#eI1", 31.2], ["#hlI2", "#eI2", 31.45], ["#hlI3", "#eI3", 31.7], ["#hlI4", "#eI4", 31.95]].forEach(([from, to, t]) => {
    const a = FILM.pos(from, st), b = FILM.pos(to, st);
    tl.fromTo(to, { x: a.cx - b.cx, y: a.cy - b.cy, scale: 0.9, opacity: 0 }, { x: 0, y: 0, scale: 1, opacity: 1, duration: 1.0, ease: "inOut" }, t);
    const ex = b.cx < a.cx ? b.x + b.w : b.x, ey = b.y + 44, mx = (a.cx + ex) / 2;
    const p = document.createElementNS(NS, "path");
    p.setAttribute("d", `M${a.cx} ${a.cy} C ${mx} ${a.cy}, ${mx} ${ey}, ${ex} ${ey}`); svg.appendChild(p);
    const dots = [[a.cx, a.cy], [ex, ey]].map(([x, y]) => { const c = document.createElementNS(NS, "circle"); c.setAttribute("cx", x); c.setAttribute("cy", y); c.setAttribute("r", 5); svg.appendChild(c); return c; });
    const len = p.getTotalLength();
    gsap.set(p, { strokeDasharray: len, strokeDashoffset: len }); gsap.set(dots, { opacity: 0 });
    tl.to(dots[0], { opacity: 1, duration: 0.3, ease: "out" }, t + 0.7);
    tl.to(p, { strokeDashoffset: 0, duration: 0.7, ease: "inOut" }, t + 0.75);
    tl.to(dots[1], { opacity: 1, duration: 0.3, ease: "out" }, t + 1.35);
  });
  const bI = FILM.words("#bI"), bI2 = FILM.words("#bI2");
  gsap.set(bI2, { yPercent: 105, opacity: 0 });
  FILM.rise(tl, bI, 31.5, { stagger: 0.06 });
  FILM.sink(tl, bI, 33.3);
  FILM.rise(tl, bI2, 33.6, { stagger: 0.06 });

  // ---------- J · Founder Book graph (35.2–39.2) ----------
  (function () {
    const G = window.GRAPH, cv = $("#g-canvas"), ctx = cv.getContext("2d");
    const CX = 960, CY = 500, RAD = 360, n = G.n, E = G.edges;
    const rr = new Float32Array(n); for (let i = 0; i < n; i++) rr[i] = Math.hypot(G.x[i], G.y[i]);
    const size = G.d.map((d) => 0.9 + Math.sqrt(Math.min(d, 400)) * 0.26);
    const COL = ["#faf6f2", "#f5c451", "#e5895a"];
    const S = { reveal: 0, edges: 0, rot: 0, zoom: 1.15 };
    const P = new Float32Array(n * 2);
    const draw = () => {
      ctx.clearRect(0, 0, 1920, 1080);
      const c = Math.cos(S.rot), s = Math.sin(S.rot), R = S.reveal * 1.05;
      for (let i = 0; i < n; i++) { P[2 * i] = CX + (G.x[i] * c - G.y[i] * s) * RAD * S.zoom; P[2 * i + 1] = CY + (G.x[i] * s + G.y[i] * c) * RAD * S.zoom; }
      if (S.edges > 0) { ctx.lineWidth = 0.6; ctx.strokeStyle = `rgba(245,196,81,${0.08 * S.edges})`; ctx.beginPath();
        for (let k = 0; k < E.length; k += 2) { const a = E[k], b = E[k + 1]; if (rr[a] > R || rr[b] > R) continue; ctx.moveTo(P[2 * a], P[2 * a + 1]); ctx.lineTo(P[2 * b], P[2 * b + 1]); }
        ctx.stroke(); }
      for (let t = 0; t < 3; t++) { ctx.fillStyle = COL[t]; ctx.beginPath();
        for (let i = 0; i < n; i++) { if (G.t[i] !== t) continue; const k = (R - rr[i]) / 0.08; if (k <= 0) continue;
          const r = size[i] * S.zoom * Math.min(1, k); ctx.moveTo(P[2 * i] + r, P[2 * i + 1]); ctx.arc(P[2 * i], P[2 * i + 1], r, 0, Math.PI * 2); }
        ctx.fill(); }
    };
    tl.fromTo(S, { reveal: 0 }, { reveal: 1, duration: 1.8, ease: "inOut", onUpdate: draw }, 35.3);
    tl.fromTo(S, { edges: 0 }, { edges: 1, duration: 1.6, ease: "inOut", onUpdate: draw }, 35.7);
    tl.fromTo(S, { rot: -0.12, zoom: 1.15 }, { rot: 0.05, zoom: 1.0, duration: 4.0, ease: "none", onUpdate: draw }, 35.2);
  })();
  FILM.appear(tl, "#gkJ", 35.5, { y: 8 });
  FILM.appear(tl, "#gsJ .st", 35.9, { y: 24, stagger: 0.08 });
  FILM.count(tl, "#gv", 0, FACTS.videos, 36.0, 1.4, { ease: "out" });
  FILM.count(tl, "#ge", 0, FACTS.essays, 36.08, 1.3, { ease: "out" });
  FILM.count(tl, "#gp", 0, FACTS.pages, 36.25, 1.6, { ease: "out" });

  // ---------- K · for you (39.2–43.4) ----------
  FILM.push(tl, "#pK", 39.2, 4.2, { from: 1.0, to: 1.05, x: 10 });
  FILM.appear(tl, "#cK", 39.55);
  FILM.rise(tl, FILM.words("#capK"), 40.4, { stagger: 0.06 });

  // ---------- L · for your agents (43.4–48.0) ----------
  FILM.push(tl, "#pL", 43.4, 4.6, { from: 1.05, to: 1.0, x: -10 });
  FILM.appear(tl, "#cL", 43.75);
  FILM.appear(tl, "#stL .s", 44.6, { y: 14, stagger: 0.1 });
  FILM.rise(tl, FILM.words("#capL"), 45.0, { stagger: 0.06 });
  FILM.appear(tl, "#fnL", 45.8, { y: 6 });

  // ---------- M · works with (48.0–51.4) ----------
  FILM.rise(tl, FILM.words("#bM"), 48.2, { stagger: 0.05 });
  FILM.appear(tl, "#subM", 49.2, { y: 10 });

  // ---------- N · lockup (51.4–57.0) ----------
  tl.fromTo("#iconN", { opacity: 0, scale: 0.92, y: 14 }, { opacity: 1, scale: 1, y: 0, duration: 0.9, ease: "out" }, 51.6);
  FILM.rise(tl, FILM.words("#nameN"), 51.75);
  FILM.rise(tl, FILM.words("#tagN"), 52.4, { stagger: 0.05 });
  FILM.appear(tl, "#ghN", 53.1, { y: 14, dur: 0.9 });
  tl.fromTo(["#lockN", "#tagN", "#ghN"], { scale: 1 }, { scale: 1.02, duration: 4.4, ease: "none", transformOrigin: "50% 50%" }, 52.6);
});
