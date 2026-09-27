// Scene 2 (5.8-10.4): a search-style prompt types "openwiki"; the blue hero rises; "COMPILE IT."
FILM.scene(function (tl) {
  gsap.set("#s2-hero", { yPercent: 100 });
  FILM.appear(tl, "#s2-search", 6.1, { y: 24, scale: 0.97, dur: 0.9 });
  // the cursor blinks once, then the command types at a human pace
  tl.set("#s2-cur", { opacity: 0 }, 6.6); tl.set("#s2-cur", { opacity: 1 }, 6.8);
  const q = FILM.chars("#s2-q"); gsap.set(q, { opacity: 0 });
  q.forEach((c, i) => tl.set(c, { opacity: 1 }, 6.9 + i * 0.075));
  // keep the cursor after the last typed letter
  const cw = q[0].offsetWidth;
  q.forEach((c, i) => tl.set("#s2-cur", { x: -(q.length - 1 - i) * cw }, 6.9 + i * 0.075));
  gsap.set("#s2-cur", { x: -q.length * cw });

  // "enter": a small press, then the saved rows are pulled into the prompt
  tl.to("#s2-search", { scale: 0.97, duration: 0.12, ease: "out" }, 7.55);
  tl.to("#s2-search", { scale: 1, duration: 0.3, ease: "out" }, 7.67);
  FILM.$$("#s1-rows .row").forEach((el, i) => {
    const r = FILM.pos(el, "#s1-rows");
    const t = 7.6 + (i % 5) * 0.03;
    tl.to(el, { opacity: 0.6, filter: "blur(0px)", duration: 0.3, ease: "out" }, t);
    tl.to(el, { x: 960 - r.cx, y: 544 - r.cy + 46, scale: 0.5, duration: 0.9, ease: "inOut" }, t + 0.1);
    tl.to(el, { opacity: 0, duration: 0.35, ease: "exit" }, t + 0.65);
  });

  // the Revolut-blue hero rises from the bottom and the prompt moves up
  tl.to("#s2-hero", { yPercent: 0, duration: 1.0, ease: "inOut" }, 7.9);
  tl.to("#s2-search", { y: -170, scale: 0.8, duration: 1.0, ease: "inOut" }, 7.9);
  tl.to("#s2-search", { backgroundColor: "rgba(255,255,255,0.14)", borderColor: "rgba(255,255,255,0.2)", duration: 0.8, ease: "inOut" }, 8.0);
  const hw = FILM.words("#s2-h");
  FILM.rise(tl, hw, 8.45, { stagger: 0.09, dur: 0.9 });

  // exit into black
  FILM.vanish(tl, ["#s2-search", "#s2-h"], 9.95, { dur: 0.35 });
  tl.to("#s2-hero", { opacity: 0, duration: 0.4, ease: "inOut" }, 9.95);
});
