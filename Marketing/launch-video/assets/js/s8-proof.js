// Scene 8 (45.0-49.2): providers the README documents, as Revolut-style action buttons, then three true facts.
FILM.scene(function (tl) {
  FILM.appear(tl, "#s8-lbl", 45.1, { y: 12, dur: 0.8 });
  FILM.appear(tl, "#s8-btns .act", 45.25, { y: 30, scale: 0.94, dur: 0.9, stagger: 0.08 });
  FILM.appear(tl, "#s8-pills .pill", 46.3, { y: 20, dur: 0.85, stagger: 0.12 });
  FILM.vanish(tl, ["#s8-lbl", "#s8-btns", "#s8-pills"], 48.75, { dur: 0.35 });
});
