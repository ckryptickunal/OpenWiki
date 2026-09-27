// Scene 4 (16.3-23.2): light scene. "POINT IT AT [slot]" over a terminal running the real commands,
// flanked by Revolut-style balance cards with Founder Book's counts (887 YC transcripts, 233 PG essays, 8,768 pages).
FILM.scene(function (tl) {
  const F = FACTS;
  tl.fromTo("#s4", { clipPath: "inset(100% 0% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.9, ease: "inOut" }, 16.3);

  // headline with a slot that changes every 0.75s, re-centred for each word
  const lead = FILM.words("#s4-lead");
  FILM.rise(tl, lead, 16.95, { stagger: 0.07 });
  const sw = FILM.$$("#s4-slot .sw");
  const leadW = FILM.$("#s4-lead").offsetWidth, slotW = FILM.$("#s4-slot").offsetWidth, gap = 26;
  gsap.set(sw, { yPercent: 105 });
  const times = [17.15, 17.9, 18.65, 19.4, 20.15, 20.9];
  sw.forEach((s, i) => {
    const t = times[i];
    tl.fromTo(s, { yPercent: 105 }, { yPercent: 0, duration: 0.7, ease: "out" }, t);
    if (i < sw.length - 1) tl.to(s, { yPercent: -105, duration: 0.35, ease: "exit" }, times[i + 1] - 0.3);
    const total = leadW + gap + s.offsetWidth;
    tl.to("#s4-head", { x: (leadW + gap + slotW - total) / 2, duration: 0.7, ease: "inOut" }, t - 0.25);
  });

  // terminal and commands
  FILM.appear(tl, "#s4-term", 17.2, { y: 50, dur: 1.0 });
  const outs = ["#s4-o1", "#s4-o2", "#s4-o3"], lines = ["#s4-l1", "#s4-l2", "#s4-l3"];
  gsap.set([...outs, ...lines], { opacity: 0 });
  const e1 = (tl.set("#s4-l1", { opacity: 1 }, 17.5), FILM.type(tl, "#s4-c1", 17.55, 0.018));
  FILM.appear(tl, "#s4-o1", e1 + 0.1, { y: 10, dur: 0.5 });
  tl.set("#s4-l2", { opacity: 1 }, e1 + 0.3);
  const e2 = FILM.type(tl, "#s4-c2", e1 + 0.35, 0.028);
  FILM.appear(tl, "#s4-o2", e2 + 0.1, { y: 10, dur: 0.5 });
  tl.set("#s4-l3", { opacity: 1 }, e2 + 0.3);
  const e3 = FILM.type(tl, "#s4-c3", e2 + 0.35, 0.03);
  FILM.appear(tl, "#s4-o3", e3 + 0.1, { y: 10, dur: 0.5 });
  tl.fromTo("#s4-pb", { scaleX: 0 }, { scaleX: 1, duration: 22.6 - (e3 + 0.2), ease: "inOut" }, e3 + 0.2);
  FILM.count(tl, "#s4-pages", 0, F.pages, e3 + 0.2, 22.6 - (e3 + 0.2), { ease: "inOut" });

  // balance cards land with their commands' results
  FILM.appear(tl, "#s4-l", e1 + 0.15, { y: 40, dur: 0.9 });
  FILM.count(tl, "#s4-n1", 0, F.ycVideos, e1 + 0.25, 1.2);
  FILM.appear(tl, "#s4-r", e2 + 0.15, { y: 40, dur: 0.9 });
  FILM.count(tl, "#s4-n2", 0, F.pgEssays, e2 + 0.25, 1.1);

  FILM.vanish(tl, ["#s4-head", "#s4-l", "#s4-term", "#s4-r"], 22.8, { dur: 0.35, stagger: 0.03 });
});
