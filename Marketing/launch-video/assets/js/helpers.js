// Shared, deterministic helpers. No clocks, no Math.random.
// Motion follows Emil Kowalski's rules: strong custom ease-out for entrances, ease-in-out for on-screen moves,
// exits faster than entrances, short staggers, small blur, nothing enters from scale(0).
window.FILM = window.FILM || {};
(function (F) {
  F.CX = 960; F.CY = 540;

  gsap.registerPlugin(CustomEase);
  CustomEase.create("out", "0.23, 1, 0.32, 1");        // entrances
  CustomEase.create("inOut", "0.77, 0, 0.175, 1");     // on-screen moves, scene transitions
  CustomEase.create("drawer", "0.32, 0.72, 0, 1");     // panels and cards settling
  CustomEase.create("exit", "0.55, 0, 1, 0.45");       // quick, clean exits

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

  // Split text into masked word spans for line-rise reveals.
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

  F.chars = function (el) {
    if (typeof el === "string") el = F.$(el);
    const t = el.textContent; el.textContent = "";
    return [...t].map((ch) => {
      const s = document.createElement("span"); s.className = "ch";
      s.textContent = ch === " " ? " " : ch; el.appendChild(s); return s;
    });
  };

  // Headline entrance: words rise out of their masks, 70ms apart.
  F.rise = function (tl, targets, at, o = {}) {
    tl.fromTo(targets, { yPercent: 105, opacity: 0.001 },
      { yPercent: 0, opacity: 1, duration: o.dur || 0.85, ease: "out", stagger: o.stagger ?? 0.07 }, at);
  };
  // Exit is quicker than the entrance.
  F.sink = function (tl, targets, at, o = {}) {
    tl.to(targets, { yPercent: -105, opacity: 0, duration: o.dur || 0.4, ease: "exit", stagger: o.stagger ?? 0.03 }, at);
  };
  // Generic element entrance: small lift, slight scale, fade.
  F.appear = function (tl, targets, at, o = {}) {
    tl.fromTo(targets, { y: o.y ?? 28, scale: o.scale ?? 0.98, opacity: 0 },
      { y: 0, scale: 1, opacity: 1, duration: o.dur || 0.8, ease: "out", stagger: o.stagger ?? 0.07 }, at);
  };
  F.vanish = function (tl, targets, at, o = {}) {
    tl.to(targets, { y: o.y ?? -16, opacity: 0, duration: o.dur || 0.35, ease: "exit", stagger: o.stagger ?? 0 }, at);
  };

  // Number that counts up with a calm ease-out.
  F.count = function (tl, el, from, to, at, dur, o = {}) {
    if (typeof el === "string") el = F.$(el);
    const s = { v: from }, fmt = o.fmt || ((v) => Math.round(v).toLocaleString("en-US"));
    el.textContent = fmt(from);
    tl.to(s, { v: to, duration: dur, ease: o.ease || "out", onUpdate: () => { el.textContent = fmt(s.v); } }, at);
  };

  // Type a command at a human pace; returns the end time.
  F.type = function (tl, el, at, step = 0.032) {
    const cs = F.chars(el); gsap.set(cs, { opacity: 0 });
    cs.forEach((c, i) => tl.set(c, { opacity: 1 }, at + i * step));
    return at + cs.length * step;
  };

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
