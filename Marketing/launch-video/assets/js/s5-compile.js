// Scene 5 (16.0-22.3): one real transcript (Dylan Field on YC, pulled with OpenWiki 0.3.0, real [m:ss] cues)
// becomes linked pages. Page names and source counts are the real Founder Book pages.
FILM.scene(function (tl) {
  const st = "#s5-stage";

  // the doc arrives, continuing the push from the terminal
  tl.fromTo("#s5-doc", { scale: 0.5, opacity: 0, filter: "blur(16px)", y: 40 },
    { scale: 1, opacity: 1, filter: "blur(0px)", y: 0, duration: 0.55, ease: "expo.out" }, 16.0);
  tl.fromTo(st, { scale: 1.0 }, { scale: 1.045, duration: 5.6, ease: "sine.inOut" }, 16.0);

  // the highlighter reads the page
  const hl = [["#hl-dylan", 16.55, 0.22], ["#hl-figma", 16.72, 0.16], ["#hl-found", 16.9, 0.12], ["#hl-found2", 16.98, 0.16], ["#hl-quote", 17.12, 0.42]];
  hl.forEach(([id, t, d]) => tl.fromTo(id, { "--hx": 0 }, { "--hx": 1, duration: d, ease: "power2.inOut" }, t));

  // each highlighted phrase peels off into its own page, linked back with a drawn line
  const svg = FILM.$("#s5-links"), NS = "http://www.w3.org/2000/svg";
  const pairs = [["#hl-dylan", "#s5-p1", 17.55], ["#hl-figma", "#s5-p2", 17.8], ["#hl-found2", "#s5-p3", 18.05], ["#hl-quote", "#s5-p4", 18.3]];
  pairs.forEach(([from, to, t]) => {
    const a = FILM.pos(from, st), b = FILM.pos(to, st);
    // the card starts on the highlight, small, and springs to its slot
    const dx = a.cx - b.cx, dy = a.cy - b.cy;
    tl.fromTo(to, { x: dx, y: dy, scale: 0.18, opacity: 0, rotation: dx > 0 ? 8 : -8 },
      { x: 0, y: 0, scale: 1, opacity: 1, rotation: 0, duration: 0.62, ease: "back.out(1.35)" }, t);
    // wikilink: from the phrase to the nearest edge of the card
    const ex = b.cx < a.cx ? b.x + b.w : b.x, ey = b.cy;
    const mx = (a.cx + ex) / 2;
    const p = document.createElementNS(NS, "path");
    p.setAttribute("d", `M${a.cx} ${a.cy} C ${mx} ${a.cy}, ${mx} ${ey}, ${ex} ${ey}`);
    svg.appendChild(p);
    const c1 = document.createElementNS(NS, "circle"); c1.setAttribute("cx", a.cx); c1.setAttribute("cy", a.cy); c1.setAttribute("r", 6); svg.appendChild(c1);
    const c2 = document.createElementNS(NS, "circle"); c2.setAttribute("cx", ex); c2.setAttribute("cy", ey); c2.setAttribute("r", 6); svg.appendChild(c2);
    const len = p.getTotalLength();
    gsap.set(p, { strokeDasharray: len, strokeDashoffset: len });
    gsap.set([c1, c2], { scale: 0, transformOrigin: "50% 50%" });
    tl.to(c1, { scale: 1, duration: 0.2, ease: "back.out(3)" }, t + 0.35);
    tl.to(p, { strokeDashoffset: 0, duration: 0.45, ease: "power2.inOut" }, t + 0.4);
    tl.to(c2, { scale: 1, duration: 0.2, ease: "back.out(3)" }, t + 0.8);
  });

  // backlink counts tick up on each page card
  FILM.$$("#s5-stage .epage .emeta b").forEach((b, i) => {
    const v = +b.textContent; FILM.count(tl, b, 0, v, pairs[i][2] + 0.5, 0.6);
  });

  // the verified-quote stamp
  tl.fromTo("#s5-stamp", { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.4, ease: "back.out(2.4)", transformOrigin: "0% 50%" }, 18.75);

  // headline at the bottom
  const hw = FILM.words("#s5-h");
  FILM.inkIn(tl, hw, 18.95, { stagger: 0.06, dur: 0.55, swell: "#s5-h" });

  // cards breathe during the hold so the frame never freezes
  ["#s5-p1", "#s5-p2", "#s5-p3", "#s5-p4"].forEach((id, i) => {
    tl.to(id, { y: i % 2 ? 8 : -8, rotation: i % 2 ? 0.6 : -0.6, duration: 1.4, ease: "sine.inOut", yoyo: true, repeat: 1 }, 18.9 + i * 0.1);
  });

  // exit: everything shrinks into one node at the centre as the graph opens around it
  tl.to(st, { scale: 0.08, opacity: 0, filter: "blur(6px)", duration: 0.55, ease: "power3.in" }, 21.7);
  tl.to("#s5-h", { opacity: 0, y: 30, duration: 0.3, ease: "power2.in" }, 21.6);
});
