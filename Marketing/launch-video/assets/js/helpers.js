// Shared, deterministic helpers for every scene. No clocks, no Math.random.
window.FILM = window.FILM || {};
(function (F) {
  F.W = 1920; F.H = 1080; F.CX = 960; F.CY = 540;
  F.BEAT = 0.5; // 120 BPM; music is trimmed so t=0 is a downbeat

  F.rng = function (seed) {
    return function () {
      seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  };

  F.$ = (sel) => document.querySelector(sel);
  F.$$ = (sel) => [...document.querySelectorAll(sel)];

  // Split an element's text into inline-block character spans (spaces kept as nbsp).
  F.chars = function (el) {
    if (typeof el === "string") el = F.$(el);
    const t = el.textContent; el.textContent = "";
    return [...t].map((ch) => {
      const s = document.createElement("span"); s.className = "ch";
      s.textContent = ch === " " ? " " : ch; el.appendChild(s); return s;
    });
  };

  // Split into word spans, each wrapped in a mask for masked rise reveals.
  F.words = function (el) {
    if (typeof el === "string") el = F.$(el);
    const parts = el.textContent.trim().split(/\s+/); el.textContent = "";
    return parts.map((w, i) => {
      const m = document.createElement("span"); m.className = "wm";
      const s = document.createElement("span"); s.className = "wi"; s.textContent = w;
      m.appendChild(s); el.appendChild(m);
      if (i < parts.length - 1) el.appendChild(document.createTextNode(" "));
      return s;
    });
  };

  // The house text entrance: rise out of a mask, un-blur, and swell the ink (Fraunces wght axis).
  F.inkIn = function (tl, targets, at, opts = {}) {
    const o = Object.assign({ stagger: 0.028, dur: 0.55, from: 180, to: 700, rot: 8, blur: 10 }, opts);
    tl.fromTo(targets, { yPercent: 118, rotation: o.rot, filter: `blur(${o.blur}px)` },
      { yPercent: 0, rotation: 0, filter: "blur(0px)", duration: o.dur, ease: "expo.out", stagger: o.stagger }, at);
    if (o.swell) tl.fromTo(o.swell, { "--w": o.from }, { "--w": o.to, duration: o.dur + 0.35, ease: "power2.out" }, at);
  };

  F.inkOut = function (tl, targets, at, opts = {}) {
    const o = Object.assign({ stagger: 0.012, dur: 0.24 }, opts);
    tl.to(targets, { yPercent: -118, rotation: -6, duration: o.dur, ease: "power3.in", stagger: o.stagger }, at);
  };

  // Count a number up inside an element, formatted with thousands separators.
  F.count = function (tl, el, from, to, at, dur, opts = {}) {
    if (typeof el === "string") el = F.$(el);
    const o = { v: from }, fmt = opts.fmt || ((v) => Math.round(v).toLocaleString("en-US"));
    el.textContent = fmt(from);
    tl.to(o, { v: to, duration: dur, ease: opts.ease || "power2.out", onUpdate: () => { el.textContent = fmt(o.v); } }, at);
  };

  // Type text into a row of pre-built char spans with a block cursor that follows.
  F.typeRow = function (tl, rowEl, text, at, step, cursorEl) {
    rowEl.textContent = "";
    const spans = [...text].map((ch) => {
      const s = document.createElement("span"); s.textContent = ch === " " ? " " : ch;
      rowEl.appendChild(s); return s;
    });
    gsap.set(spans, { opacity: 0 });
    const cw = spans.length ? spans[0].getBoundingClientRect().width || 0 : 0;
    spans.forEach((s, i) => {
      tl.set(s, { opacity: 1 }, at + i * step);
      if (cursorEl) tl.set(cursorEl, { x: s.offsetLeft + s.offsetWidth }, at + i * step);
    });
    return { spans, end: at + spans.length * step, cw };
  };

  // Film grain: one seeded noise tile shifted at 12 fps for the whole film.
  F.grain = function (tl, dur) {
    const c = F.$("#grain"), g = c.getContext("2d"), img = g.createImageData(512, 512), n = F.rng(42);
    for (let i = 0; i < img.data.length; i += 4) {
      const v = 128 + (n() - 0.5) * 255; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255;
    }
    g.putImageData(img, 0, 0);
    c.style.width = "2048px"; c.style.height = "1208px";
    const R = F.rng(7);
    for (let f = 0; f < dur * 12; f++) tl.set(c, { x: -Math.floor(R() * 64), y: -Math.floor(R() * 64) }, f / 12);
  };

  // Layout position of el relative to an ancestor, from offsets (unaffected by preview scaling or transforms).
  F.pos = function (el, anc) {
    if (typeof el === "string") el = F.$(el);
    if (typeof anc === "string") anc = F.$(anc);
    let x = 0, y = 0, n = el;
    while (n && n !== anc) { x += n.offsetLeft; y += n.offsetTop; n = n.offsetParent; }
    return { x, y, w: el.offsetWidth, h: el.offsetHeight, cx: x + el.offsetWidth / 2, cy: y + el.offsetHeight / 2 };
  };

  F.scenes = [];
  F.scene = (fn) => F.scenes.push(fn);
})(window.FILM);
