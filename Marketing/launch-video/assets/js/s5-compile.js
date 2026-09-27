// Scene 5 (23.0-30.2): one real transcript (Dylan Field on YC, pulled with OpenWiki, real [m:ss] cues) becomes
// linked pages. Page names and source counts are the real Founder Book pages.
FILM.scene(function (tl) {
  const st = "#s5-stage";
  FILM.appear(tl, "#s5-doc", 23.1, { y: 40, dur: 1.0 });
  gsap.set("#s5-stamp", { opacity: 0 });

  // highlights sweep one after another
  [["#hl-dylan", 24.0], ["#hl-figma", 24.45], ["#hl-found", 24.9], ["#hl-quote", 25.35]].forEach(([id, t]) =>
    tl.fromTo(id, { "--hx": 0 }, { "--hx": 1, duration: 0.55, ease: "inOut" }, t));

  // each highlight becomes its own page; a link is drawn back to the phrase
  const svg = FILM.$("#s5-links"), NS = "http://www.w3.org/2000/svg";
  const pairs = [["#hl-dylan", "#s5-p1", 26.0], ["#hl-figma", "#s5-p2", 26.4], ["#hl-found", "#s5-p3", 26.8], ["#hl-quote", "#s5-p4", 27.2]];
  pairs.forEach(([from, to, t]) => {
    const a = FILM.pos(from, st), b = FILM.pos(to, st);
    tl.fromTo(to, { x: a.cx - b.cx, y: a.cy - b.cy, scale: 0.9, opacity: 0 },
      { x: 0, y: 0, scale: 1, opacity: 1, duration: 1.0, ease: "inOut" }, t);
    const ex = b.cx < a.cx ? b.x + b.w : b.x, ey = b.y + 50, mx = (a.cx + ex) / 2;
    const p = document.createElementNS(NS, "path");
    p.setAttribute("d", `M${a.cx} ${a.cy} C ${mx} ${a.cy}, ${mx} ${ey}, ${ex} ${ey}`);
    svg.appendChild(p);
    const dots = [[a.cx, a.cy], [ex, ey]].map(([x, y]) => {
      const c = document.createElementNS(NS, "circle"); c.setAttribute("cx", x); c.setAttribute("cy", y); c.setAttribute("r", 5); svg.appendChild(c); return c;
    });
    const len = p.getTotalLength();
    gsap.set(p, { strokeDasharray: len, strokeDashoffset: len });
    gsap.set(dots, { opacity: 0 });
    tl.to(dots[0], { opacity: 1, duration: 0.3, ease: "out" }, t + 0.7);
    tl.to(p, { strokeDashoffset: 0, duration: 0.7, ease: "inOut" }, t + 0.75);
    tl.to(dots[1], { opacity: 1, duration: 0.3, ease: "out" }, t + 1.35);
  });

  FILM.$$("#s5-stage .ent .m b").forEach((b, i) => { const v = +b.textContent; FILM.count(tl, b, 0, v, pairs[i][2] + 0.7, 0.9); });
  FILM.appear(tl, "#s5-stamp", 28.0, { y: 10, dur: 0.6 });

  const hw = FILM.words("#s5-h");
  FILM.rise(tl, hw, 28.2, { stagger: 0.06 });

  // exit: the page set gathers toward the centre as the graph takes over
  tl.to(st, { scale: 0.92, opacity: 0, duration: 0.5, ease: "exit" }, 29.75);
  FILM.vanish(tl, "#s5-h", 29.7, { dur: 0.35 });
});
