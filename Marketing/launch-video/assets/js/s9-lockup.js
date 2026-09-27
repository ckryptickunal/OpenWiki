// Scene 9 (48.8-56.0): lockup on the Revolut-blue hero. Icon rebuilt from Marketing/Logo.png.
FILM.scene(function (tl) {
  tl.fromTo("#s9-hero", { yPercent: 100 }, { yPercent: 0, duration: 1.0, ease: "inOut" }, 48.8);
  tl.fromTo("#s9-icon", { opacity: 0, scale: 0.92, y: 20 }, { opacity: 1, scale: 1, y: 0, duration: 0.9, ease: "out" }, 49.5);
  const nm = FILM.words("#s9-name");
  FILM.rise(tl, nm, 49.65, { dur: 0.9 });
  const tag = FILM.words("#s9-tag");
  FILM.rise(tl, tag, 50.2, { stagger: 0.05, dur: 0.85 });
  FILM.appear(tl, "#s9-pip", 50.9, { y: 24, dur: 0.9 });
  FILM.appear(tl, "#s9-gh", 51.2, { y: 16, dur: 0.8 });
  FILM.appear(tl, "#s9-foot", 51.6, { y: 10, dur: 0.8 });
  // a slow settle through the hold
  tl.fromTo(["#s9-lock", "#s9-tag", "#s9-cta"], { scale: 1 }, { scale: 1.02, duration: 5.2, ease: "none", transformOrigin: "50% 50%" }, 50.8);
});
