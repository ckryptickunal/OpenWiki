// Scene 7 (35.5-45.0): the same 3 questions on Founder Book, wiki path vs the raw files behind the same pages:
// 8,171 vs 65,097 tokens (7.97x, tiktoken o200k). Then a real `openwiki ask` answer with citations (0.3.0 output).
FILM.scene(function (tl) {
  const F = FACTS;
  const hw = FILM.words("#s7-h"); gsap.set(hw, { yPercent: 105, opacity: 0 });
  const h2w = FILM.words("#s7-h2"); gsap.set(h2w, { yPercent: 105, opacity: 0 });
  gsap.set(["#s7-term"], { opacity: 0 });

  FILM.appear(tl, "#s7-kick", 35.7, { y: 12, dur: 0.8 });
  FILM.appear(tl, ["#s7-c1", "#s7-c2"], 35.9, { y: 40, dur: 0.95, stagger: 0.12 });
  tl.fromTo("#s7-b1", { scaleX: 0 }, { scaleX: 1, duration: 1.6, ease: "out" }, 36.5);
  FILM.count(tl, "#s7-n1", 0, F.rawTokens3, 36.5, 1.6);
  tl.fromTo("#s7-b2", { scaleX: 0 }, { scaleX: F.wikiTokens3 / F.rawTokens3, duration: 1.6, ease: "out" }, 36.62);
  FILM.count(tl, "#s7-n2", 0, F.wikiTokens3, 36.62, 1.6);
  FILM.$("#s7-h .wi").textContent = `${F.ratio3}×`;
  FILM.rise(tl, hw, 38.5, { stagger: 0.08, dur: 0.9 });

  // part two, with time to read the answer
  FILM.vanish(tl, ["#s7-kick", "#s7-h", "#s7-cards"], 40.6, { dur: 0.4, stagger: 0.04 });
  FILM.rise(tl, h2w, 41.0, { stagger: 0.06 });
  FILM.appear(tl, "#s7-term", 41.3, { y: 50, dur: 1.0 });
  const e = FILM.type(tl, "#s7-cmd", 41.7, 0.024);
  FILM.appear(tl, "#s7-ans", e + 0.25, { y: 14, dur: 0.8 });
  FILM.appear(tl, "#s7-srcs > div", e + 0.7, { y: 10, dur: 0.6, stagger: 0.12 });
  FILM.vanish(tl, ["#s7-h2", "#s7-term"], 44.65, { dur: 0.35 });
});
