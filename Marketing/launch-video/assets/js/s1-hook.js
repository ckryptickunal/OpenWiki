// Scene 1 (0-6.2): saved things pile up as Revolut-style rows around "YOU WATCHED / SAVED / FORGOT IT."
FILM.scene(function (tl) {
  const R = FILM.rng(20260927), CX = FILM.CX;
  const play = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z" fill="#fff"/></svg>';
  const doc = '<svg viewBox="0 0 24 24"><path d="M6 3h8l4 4v14H6z" fill="none" stroke="#fff" stroke-width="2" stroke-linejoin="round"/></svg>';
  const mark = '<svg viewBox="0 0 24 24"><path d="M6 3h12v18l-6-4-6 4z" fill="#fff"/></svg>';
  // real public titles; the right-hand value is what happened to it
  const rows = [
    ["yt", play, "Intro to Large Language Models", "YouTube", "Watched", 80, 70],
    ["es", doc, "How to Do Great Work", "paulgraham.com", "Saved", 1300, 90],
    ["yt", play, "Lecture 1: How to Start a Startup", "YouTube · Watch later", "Saved", 110, 210],
    ["bm", mark, "The Bitter Lesson", "incompleteideas.net", "Read later", 1270, 216],
    ["pdf", "PDF", "attention-is-all-you-need.pdf", "Downloads", "Unread", 150, 340],
    ["yt", play, "How to Get Startup Ideas", "YouTube · Watch later", "Saved", 1330, 344],
    ["nt", "✎", "notes.md", "which video was it…", "Draft", 90, 700],
    ["es", doc, "Do Things that Don't Scale", "paulgraham.com", "Bookmarked", 1290, 690],
    ["yt", play, "Is your startup default alive, or default dead?", "YouTube · Watch later", "Saved", 150, 830],
    ["bm", mark, "Liked videos", "YouTube", "Liked", 1250, 826],
    ["es", doc, "What I Worked On", "paulgraham.com", "Read later", 700, 950],
  ];
  const box = FILM.$("#s1-rows");
  const els = rows.map(([k, ic, t1, t2, val, x, y]) => {
    const d = document.createElement("div"); d.className = "row";
    d.innerHTML = `<div class="ic ${k}">${ic}</div><div class="tx"><div class="t1">${t1}</div><div class="t2">${t2}</div></div><div class="val dim">${val}</div>`;
    d.style.left = x + "px"; d.style.top = y + "px"; box.appendChild(d); return d;
  });

  // rows arrive one after another, then drift slowly (parallax), never still
  els.forEach((el, i) => {
    tl.fromTo(el, { opacity: 0, y: 36, scale: 0.97 }, { opacity: 1, y: 0, scale: 1, duration: 0.9, ease: "out" }, 0.05 + i * 0.16);
  });
  tl.fromTo("#s1-rows", { y: 0 }, { y: -46, duration: 6.2, ease: "none" }, 0);

  // headline "YOU [slot] IT." with measured positions for each state
  const wYou = FILM.$("#w-you").offsetWidth, wIt = FILM.$("#w-it").offsetWidth;
  const slot = { watched: FILM.$("#w-watched").offsetWidth, saved: FILM.$("#w-saved").offsetWidth, forgot: FILM.$("#w-forgot").offsetWidth };
  const GAP = 40, PAD = 16;
  const lay = (k) => { const tot = wYou + GAP + slot[k] + GAP + wIt, l = CX - tot / 2; return { you: l - PAD, slot: l + wYou + GAP - PAD, it: l + wYou + GAP + slot[k] + GAP - PAD }; };
  const L = { watched: lay("watched"), saved: lay("saved"), forgot: lay("forgot") };
  gsap.set("#m-you", { x: L.watched.you }); gsap.set("#m-slot", { x: L.watched.slot }); gsap.set("#m-it", { x: L.watched.it });
  gsap.set(["#w-saved", "#w-forgot"], { yPercent: 110 });

  tl.fromTo(["#w-you", "#w-watched", "#w-it"], { yPercent: 110 }, { yPercent: 0, duration: 0.9, ease: "out", stagger: 0.08 }, 0.25);

  function swap(from, to, at) {
    tl.to(from, { yPercent: -110, duration: 0.4, ease: "exit" }, at);
    ["you", "slot", "it"].forEach((k) => tl.to("#m-" + k, { x: L[to.slice(3)][k], duration: 0.8, ease: "inOut" }, at + 0.1));
    tl.fromTo(to, { yPercent: 110 }, { yPercent: 0, duration: 0.85, ease: "out" }, at + 0.3);
  }
  swap("#w-watched", "#w-saved", 1.9);
  swap("#w-saved", "#w-forgot", 3.6);

  // forgetting: the rows dim and soften, then the line fades out letter by letter
  els.forEach((el, i) => tl.to(el, { opacity: 0.14, filter: "blur(3px)", duration: 1.1, ease: "inOut" }, 4.5 + (i % 4) * 0.06));
  tl.to("#s1-glow", { opacity: 0.3, duration: 1.0, ease: "inOut" }, 4.5);
  const letters = [...FILM.chars("#w-you"), ...FILM.chars("#w-forgot"), ...FILM.chars("#w-it")];
  const order = letters.map((c, i) => [c, R()]).sort((a, b) => a[1] - b[1]).map((p) => p[0]);
  tl.to(order, { opacity: 0, y: -14, duration: 0.6, ease: "exit", stagger: 0.035 }, 5.0);
});
