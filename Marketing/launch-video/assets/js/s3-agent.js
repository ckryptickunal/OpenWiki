// Scene 3 (6.0-10.5): without a wiki, an agent answers one question by reading the raw pile.
// The file list and token counts are the real 68 files a plain-text search for "don't scale" hits in Founder Book.
FILM.scene(function (tl) {
  const T = 6.0, F = FACTS, R = FILM.rng(33);

  // build the read log from the real list
  const box = FILM.$("#s3-reads");
  const rows = window.NAIVE68.map(([file, tok]) => {
    const d = document.createElement("div"); d.className = "rl";
    d.innerHTML = `<span>read  ${file}</span><b>+${tok.toLocaleString("en-US")}</b>`;
    box.appendChild(d); return d;
  });
  rows.forEach((r) => (r.style.opacity = 0));
  const rowH = 36.75; // 21px * 1.75

  // headline and kicker
  const hw = FILM.words("#s3-h");
  tl.fromTo("#s3-kick", { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }, T + 0.02);
  FILM.inkIn(tl, hw, T + 0.05, { stagger: 0.07, dur: 0.6, swell: "#s3-h" });

  // terminal rises
  tl.fromTo("#s3-term", { y: 90, opacity: 0, scale: 0.96 }, { y: 0, opacity: 1, scale: 1, duration: 0.7, ease: "expo.out" }, T + 0.3);

  // the question types fast
  const q = FILM.chars("#s3-q");
  gsap.set(q, { opacity: 0 });
  q.forEach((c, i) => tl.set(c, { opacity: 1 }, T + 0.55 + i * 0.011));
  const qEnd = T + 0.55 + q.length * 0.011; // ~7.25

  // reads pour in: each new row pushes the log up; counters climb with it
  const start = qEnd + 0.15, dur = 2.35; // 7.4 -> 9.75
  const n = rows.length;
  // accelerate: row i appears at start + dur * (i/n)^0.7
  // position the log so the newest row sits at the bottom of the window
  // counters show exactly what has been read so far (they end on 68 files / 611,954 tokens)
  const filesEl = FILM.$("#s3-files"), tokEl = FILM.$("#s3-tok");
  const cum = []; window.NAIVE68.reduce((a, [, t], i) => (cum[i] = a + t), 0);
  const st = { p: 0 }; let shown = -1;
  const paint = () => {
    const k = Math.min(n, Math.floor(n * Math.pow(st.p, 1 / 0.72) + (st.p > 0 ? 1 : 0))); // rows visible
    if (k === shown) return; shown = k;
    rows.forEach((r, i) => { r.style.opacity = i < k ? 1 : 0; });
    box.style.transform = `translateY(${k ? (n - k) * rowH : 0}px)`;
    filesEl.textContent = String(k);
    tokEl.textContent = (k ? cum[k - 1] : 0).toLocaleString("en-US");
  };
  tl.fromTo(st, { p: 0 }, { p: 1, duration: dur, ease: "none", onUpdate: paint }, start);
  tl.fromTo("#s3-meter", { scaleX: 0 }, { scaleX: 1, duration: dur, ease: "power1.in" }, start);

  // the payoff line swaps on the 8.5 beat
  tl.to("#s3-kick", { opacity: 0, duration: 0.2 }, T + 2.35);
  FILM.inkOut(tl, hw, T + 2.3);
  const h2 = document.createElement("div");
  h2.className = "h-top disp"; h2.id = "s3-h2";
  h2.textContent = `${F.naiveFiles} files. ${F.naiveTokens.toLocaleString("en-US")} tokens. One question.`;
  FILM.$("#s3").appendChild(h2);
  h2.style.fontSize = "92px"; h2.style.top = "150px";
  const h2w = FILM.words(h2);
  gsap.set(h2w, { yPercent: 118 });
  FILM.inkIn(tl, h2w, T + 2.5, { stagger: 0.09, dur: 0.55, swell: h2 });

  // counter lands: a jolt on the terminal
  tl.fromTo("#s3-term", { x: 0 }, { x: 10, duration: 0.05, yoyo: true, repeat: 5, ease: "sine.inOut" }, start + dur);
  tl.fromTo("#s3-tok", { scale: 1 }, { scale: 1.12, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out", transformOrigin: "100% 50%" }, start + dur);

  // exit: the whole frame slides away as paper wipes in from the right (S4 owns the wipe)
  tl.to(["#s3-term", "#s3-h2"], { x: -260, filter: "blur(10px)", opacity: 0, duration: 0.4, ease: "power3.in" }, 10.15);
});
