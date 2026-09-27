// Scene 7 (26.2-32.0): measured on Founder Book — 3 real questions, wiki path vs the raw files behind the same pages:
// 8,171 vs 65,097 tokens (7.97x, tiktoken o200k). Then a real `openwiki ask` answer with citations (0.3.0 output).
FILM.scene(function (tl) {
  const F = FACTS;
  tl.fromTo("#s7", { clipPath: "inset(100% 0% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.4, ease: "expo.inOut" }, 26.2);

  tl.fromTo("#s7-kick", { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.4 }, 26.5);
  tl.fromTo(".brow", { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.45, ease: "expo.out", stagger: 0.15 }, 26.55);
  tl.fromTo("#s7-b1", { scaleX: 0 }, { scaleX: 1, duration: 1.1, ease: "power2.inOut" }, 26.7);
  FILM.count(tl, "#s7-n1", 0, F.rawTokens3, 26.7, 1.1, { ease: "power2.inOut" });
  const r = F.wikiTokens3 / F.rawTokens3;
  tl.fromTo("#s7-b2", { scaleX: 0 }, { scaleX: r, duration: 0.5, ease: "power2.out" }, 27.3);
  FILM.count(tl, "#s7-n2", 0, F.wikiTokens3, 27.3, 0.5);

  // "8× fewer tokens." lands on the 28.0 downbeat
  const big = FILM.$("#s7-big");
  const x = FILM.$("#s7-x"); x.textContent = `${F.ratio3}×`;
  tl.fromTo(x, { scale: 2.2, opacity: 0, filter: "blur(14px)" }, { scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.5, ease: "expo.out", transformOrigin: "50% 60%" }, 28.0);
  tl.fromTo(big, { "--w": 200 }, { "--w": 700, duration: 0.8, ease: "power2.out" }, 28.0);
  const rest = document.createElement("span"); rest.id = "s7-rest";
  // animate the words after the number separately
  const node = big.childNodes[1]; const text = node.textContent; node.remove();
  rest.textContent = text; big.appendChild(rest);
  const rw = FILM.words(rest);
  FILM.inkIn(tl, rw, 28.12, { stagger: 0.07, dur: 0.5 });

  // part two: clear the chart, then the page-not-pile line and a real cited answer
  tl.to(["#s7-kick", "#s7-bars", "#s7-big"], { y: -60, opacity: 0, filter: "blur(8px)", duration: 0.35, ease: "power3.in", stagger: 0.04 }, 29.45);
  const lw = FILM.words("#s7-l2");
  FILM.inkIn(tl, lw, 29.75, { stagger: 0.06, dur: 0.5, swell: "#s7-l2" });
  tl.fromTo("#s7-term", { y: 120, opacity: 0, scale: 0.95 }, { y: 0, opacity: 1, scale: 1, duration: 0.6, ease: "expo.out" }, 29.95);
  const cmd = FILM.chars("#s7-cmd"); gsap.set(cmd, { opacity: 0 });
  cmd.forEach((c, i) => tl.set(c, { opacity: 1 }, 30.15 + i * 0.012));
  tl.fromTo("#s7-ans", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }, 30.8);
  tl.fromTo("#s7-srcs > div", { opacity: 0, x: -14 }, { opacity: 1, x: 0, duration: 0.3, ease: "power2.out", stagger: 0.12 }, 31.1);
});
