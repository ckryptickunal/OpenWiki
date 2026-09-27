// Scene 4 (10.2-16.0): point it at anything; the real commands run in a terminal.
// Counts are Founder Book's: 887 Y Combinator transcripts, 233 Paul Graham essays, 8,768 wiki pages.
FILM.scene(function (tl) {
  const F = FACTS;

  // paper wipes in over the night scene with a slanted edge
  tl.fromTo("#s4", { clipPath: "polygon(112% 0%, 112% 0%, 100% 100%, 100% 100%)" },
    { clipPath: "polygon(-12% 0%, 112% 0%, 100% 100%, 0% 100%)", duration: 0.42, ease: "expo.inOut" }, 10.2);

  // headline: "Point it at [slot]" with the slot cycling on every beat
  const lead = FILM.words("#s4-lead");
  FILM.inkIn(tl, lead, 10.42, { stagger: 0.06, dur: 0.5, swell: "#s4-lead" });
  const sw = FILM.$$("#s4-slot .sw");
  const widths = sw.map((s) => s.offsetWidth);
  const slotW = FILM.$("#s4-slot").offsetWidth;
  gsap.set(sw, { yPercent: 115 });
  const times = [10.5, 11.0, 11.5, 12.0, 12.5, 13.0];
  sw.forEach((s, i) => {
    const t = times[i];
    tl.fromTo(s, { yPercent: 115, rotation: 6 }, { yPercent: 0, rotation: 0, duration: 0.32, ease: "expo.out" }, t);
    tl.fromTo(s, { "--w": 220 }, { "--w": 700, duration: 0.45, ease: "power2.out" }, t);
    if (i < sw.length - 1) tl.to(s, { yPercent: -115, rotation: -5, duration: 0.22, ease: "power3.in" }, times[i + 1] - 0.2);
    // keep "Point it at <word>" optically centred
    tl.to("#s4-head", { x: (slotW - widths[i]) / 2, duration: 0.3, ease: "expo.inOut" }, t - 0.12);
  });

  // terminal rises
  tl.fromTo("#s4-term", { y: 140, opacity: 0, scale: 0.94 }, { y: 0, opacity: 1, scale: 1, duration: 0.75, ease: "expo.out" }, 10.5);
  const outs = ["#s4-o1", "#s4-o2", "#s4-o3"];
  gsap.set(outs, { opacity: 0 });

  // each source chip pops with its word, then is swallowed by the terminal
  const chips = [
    ["#s4-ch1", 150, 440], ["#s4-ch2", 110, 760], ["#s4-ch3", 1560, 470], ["#s4-ch4", 1610, 790], ["#s4-ch5", 860, 985],
  ];
  const TX = 960, TY = 650;
  chips.forEach(([id, x, y], i) => {
    const el = FILM.$(id), t = times[i];
    gsap.set(el, { left: x, top: y, transformOrigin: "50% 50%" });
    const dx = TX - (x + el.offsetWidth / 2), dy = TY - (y + el.offsetHeight / 2);
    tl.fromTo(el, { scale: 0, rotation: i % 2 ? 10 : -10, x: 0, y: 0, opacity: 1 }, { scale: 1, rotation: 0, duration: 0.3, ease: "back.out(2.2)" }, t);
    tl.to(el, { x: dx, y: dy, scale: 0.2, opacity: 0, duration: 0.34, ease: "power3.in" }, t + 0.36);
  });

  // commands type; outputs land with counts
  // prompt lines appear only when their command starts typing
  const lns = FILM.$$("#s4-body > .ln:not(.out)"); gsap.set(lns, { opacity: 0 });
  function typeCmd(id, at, step) {
    tl.set(FILM.$(id).parentNode, { opacity: 1 }, at - 0.08);
    const cs = FILM.chars(id); gsap.set(cs, { opacity: 0 });
    cs.forEach((c, i) => tl.set(c, { opacity: 1 }, at + i * step));
    return at + cs.length * step;
  }
  const e1 = typeCmd("#s4-c1", 10.8, 0.015);
  tl.to("#s4-o1", { opacity: 1, duration: 0.15 }, e1 + 0.05);
  FILM.count(tl, "#s4-n1", 0, F.ycVideos, e1 + 0.05, 0.55);
  const e2 = typeCmd("#s4-c2", e1 + 0.4, 0.016);
  tl.to("#s4-o2", { opacity: 1, duration: 0.15 }, e2 + 0.05);
  FILM.count(tl, "#s4-n2", 0, F.pgEssays, e2 + 0.05, 0.45);
  const e3 = typeCmd("#s4-c3", e2 + 0.35, 0.018);
  tl.to("#s4-o3", { opacity: 1, duration: 0.15 }, e3 + 0.05);
  const pStart = e3 + 0.1, pDur = 15.3 - pStart;
  tl.fromTo("#s4-pb", { scaleX: 0 }, { scaleX: 1, duration: pDur, ease: "power1.inOut" }, pStart);
  FILM.count(tl, "#s4-pages", 0, F.pages, pStart, pDur, { ease: "power1.inOut" });

  // written pages stream under the progress bar (real Founder Book paths)
  const files = [
    "sources/-7Qz7tSTfUU-dylan-field-scaling-figma-and-the-future-of-design.md",
    "entities/dylan-field.md", "entities/figma.md", "topics/entrepreneurship.md",
    "sources/pg-do-things-that-don-t-scale-do-things-that-don-t-scale.md",
    "entities/paul-graham.md", "entities/airbnb.md", "topics/doing-things-that-don-t-scale.md",
    "topics/product-market-fit.md", "entities/y-combinator.md", "entities/sam-altman.md", "topics/founder-psychology.md",
  ];
  const stream = FILM.$("#s4-stream");
  const lines = files.map((f) => { const d = document.createElement("div"); d.textContent = "+ " + f; stream.appendChild(d); return d; });
  gsap.set(lines, { opacity: 0 });
  const lh = 30;
  lines.forEach((l, i) => {
    const t = pStart + 0.1 + i * (pDur - 0.2) / lines.length;
    tl.set(l, { opacity: 1 }, t);
    if (i >= 4) tl.to(stream.children, { y: -(i - 3) * lh, duration: 0.12, ease: "power2.out" }, t);
  });

  // exit: the terminal rushes toward the lens; the next scene continues the push
  tl.to("#s4-term", { scale: 2.4, y: -60, filter: "blur(18px)", opacity: 0, duration: 0.5, ease: "power3.in" }, 15.5);
  tl.to("#s4-head", { y: -80, opacity: 0, filter: "blur(10px)", duration: 0.4, ease: "power3.in" }, 15.5);
});
