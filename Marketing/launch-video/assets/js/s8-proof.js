// Scene 8 (33.5-37.6): proof in hard beats. Providers are the ones the README documents.
FILM.scene(function (tl) {
  const T = 33.5;
  tl.fromTo("#s8-lbl", { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.25 }, T);
  const words = ["#s8-w1", "#s8-w2", "#s8-w3", "#s8-w4"];
  gsap.set(["#s8-w1", "#s8-w2", "#s8-w3", "#s8-w4", "#s8-w5", "#s8-w6", "#s8-sub4"], { opacity: 0 });
  words.forEach((id, i) => {
    const t = T + i * 0.5;
    tl.set(id, { opacity: 1 }, t);
    tl.fromTo(id, { scale: 1.3, filter: "blur(16px)", "--w": 200 },
      { scale: 1, filter: "blur(0px)", "--w": 700, duration: 0.32, ease: "expo.out" }, t);
    if (i < words.length - 1) tl.set(id, { opacity: 0 }, t + 0.5);
  });
  tl.fromTo("#s8-sub4", { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.3 }, T + 1.62);
  tl.to(["#s8-w4", "#s8-sub4", "#s8-lbl"], { opacity: 0, y: -30, filter: "blur(8px)", duration: 0.22, ease: "power2.in" }, T + 2.18);

  // incremental re-runs
  const w5 = FILM.words("#s8-w5");
  tl.set("#s8-w5", { opacity: 1 }, T + 2.35);
  FILM.inkIn(tl, w5, T + 2.35, { stagger: 0.05, dur: 0.45, swell: "#s8-w5" });
  tl.to("#s8-w5", { opacity: 0, y: -30, filter: "blur(8px)", duration: 0.2, ease: "power2.in" }, T + 3.35);

  // free & MIT slams on the last beat
  tl.set("#s8-w6", { opacity: 1 }, T + 3.5);
  tl.fromTo("#s8-w6", { scale: 1.4, filter: "blur(18px)", "--w": 200 },
    { scale: 1, filter: "blur(0px)", "--w": 700, duration: 0.34, ease: "expo.out" }, T + 3.5);
});
