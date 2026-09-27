// Scene 3 (10.2-16.5): without a wiki, one question means reading the raw pile.
// Rows are the real 68 files a plain-text search for "don't scale" hits in Founder Book, with real token counts.
FILM.scene(function (tl) {
  const box = FILM.$("#s3-reads");
  const rows = window.NAIVE68.map(([file, tok]) => {
    const d = document.createElement("div"); d.className = "rr";
    d.innerHTML = `<i></i><span>${file}</span><b>+${tok.toLocaleString("en-US")}</b>`;
    box.appendChild(d); d.style.opacity = 0; return d;
  });
  const n = rows.length, rowH = 60;

  const hw = FILM.words("#s3-h");
  FILM.rise(tl, hw, 10.4, { stagger: 0.07 });
  const h2w = FILM.words("#s3-h2");
  gsap.set(h2w, { yPercent: 105, opacity: 0 });
  FILM.appear(tl, "#s3-card", 10.9, { y: 40, dur: 0.95 });

  // reads stream in; the counters show exactly what has been read so far
  const tokEl = FILM.$("#s3-tok"), filesEl = FILM.$("#s3-files");
  const cum = []; window.NAIVE68.reduce((a, [, t], i) => (cum[i] = a + t), 0);
  const st = { p: 0 }; let shown = -1;
  const paint = () => {
    const k = Math.min(n, Math.round(n * st.p));
    if (k === shown) return; shown = k;
    rows.forEach((r, i) => { r.style.opacity = i < k ? 1 : 0; });
    box.style.transform = `translateY(${(n - k) * rowH}px)`;
    filesEl.textContent = String(k);
    tokEl.textContent = (k ? cum[k - 1] : 0).toLocaleString("en-US");
  };
  paint();
  tl.fromTo(st, { p: 0 }, { p: 1, duration: 3.0, ease: "sine.inOut", onUpdate: paint }, 11.7);

  // the line changes once the count lands
  FILM.sink(tl, hw, 14.95);
  FILM.rise(tl, h2w, 15.25, { stagger: 0.07 });
  FILM.vanish(tl, ["#s3-card", "#s3-h2"], 16.15, { dur: 0.35 });
});
