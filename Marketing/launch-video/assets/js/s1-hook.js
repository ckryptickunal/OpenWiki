// Scenes 1-2 (0-6s): the pile ("You watched / saved / forgot it."), the prompt, "Compile it."
FILM.scene(function (tl) {
  const R = FILM.rng(20260927);
      function splitChars(el) {
        const t = el.textContent; el.textContent = "";
        return [...t].map((ch) => { const s = document.createElement("span"); s.className = "ch"; s.textContent = ch === " " ? " " : ch; el.appendChild(s); return s; });
      }

      const CX = 960, CY = 540;
      const FROM = { tl: [-1, -1], t: [0, -1.3], tr: [1, -1], r: [1.3, 0], br: [1, 1], b: [0, 1.3], bl: [-1, 1], l: [-1.3, 0] };


        // ---------- measure the headline states ----------
        const wYou = document.getElementById("w-you").offsetWidth;
        const wIt = document.getElementById("w-it").offsetWidth;
        const slot = { watched: document.getElementById("w-watched").offsetWidth, saved: document.getElementById("w-saved").offsetWidth, forgot: document.getElementById("w-forgot").offsetWidth };
        const GAP = 44, PAD = 30;
        function layout(k) { const total = wYou + GAP + slot[k] + GAP + wIt; const left = CX - total / 2; return { you: left - PAD, slot: left + wYou + GAP - PAD, it: left + wYou + GAP + slot[k] + GAP - PAD, slotLeft: left + wYou + GAP, slotW: slot[k] }; }
        const L = { watched: layout("watched"), saved: layout("saved"), forgot: layout("forgot") };

        const chYou = splitChars(document.getElementById("w-you"));
        const chW = splitChars(document.getElementById("w-watched"));
        const chS = splitChars(document.getElementById("w-saved"));
        const chF = splitChars(document.getElementById("w-forgot"));
        const chIt = splitChars(document.getElementById("w-it"));

        gsap.set("#m-you", { x: L.watched.you });
        gsap.set("#m-slot", { x: L.watched.slot });
        gsap.set("#m-it", { x: L.watched.it });
        gsap.set(["#w-saved", "#w-forgot"], { yPercent: 115 });
        gsap.set("#pbar", { x: L.watched.slotLeft + 6, y: 664, width: L.watched.slotW - 12 });
        gsap.set("#pbar i", { scaleX: 0 });
        gsap.set("#pbar b", { x: 0, scale: 0 });

        // ---------- camera: slow push the whole time ----------
        tl.fromTo("#camera", { scale: 1.0, x: 0, y: 0 }, { scale: 1.075, x: -8, y: 6, duration: 3.6, ease: "sine.inOut" }, 0);
        tl.fromTo("#paperdots", { x: 0, y: 0 }, { x: -24, y: -14, duration: 5, ease: "none" }, 0);

        // ---------- the pile: cards fly in and settle with a spring ----------
        const order = [["c1", -1], ["c5", -1], ["c8", -1], ["c13", 1.6], ["c2", 0.52], ["c3", 0.98], ["c7", 1.08], ["c12", 1.2], ["c4", 1.3], ["c10", 1.42], ["c9", 1.52], ["c6", 1.64], ["c11", 1.74], ["c14", 1.82]];
        const cards = {};
        order.forEach(([id, t0]) => {
          const el = document.getElementById(id);
          const x = +el.dataset.x, y = +el.dataset.y, r = +el.dataset.r, d = FROM[el.dataset.from];
          const w = el.offsetWidth, h = el.offsetHeight;
          cards[id] = { el, x, y, r, w, h };
          gsap.set(el, { left: x, top: y });
          const start = Math.max(0, t0);
          const k = t0 < 0 ? 0.14 : 1; // the first cards are already landing on frame 0
          tl.fromTo(el, { x: d[0] * 900 * k, y: d[1] * 700 * k, rotation: r + (d[0] >= 0 ? 24 : -24) * k, scale: 1 + 0.12 * k },
            { x: 0, y: 0, rotation: r, scale: 1, duration: k < 1 ? 0.45 : 0.62, ease: "back.out(1.25)" }, start);
        });

        // watch-later counter climbs while the pile grows
        const cnt = { v: 12 }, cntEl = document.getElementById("wlcount");
        tl.to(cnt, { v: 412, duration: 1.1, ease: "power2.in", onUpdate: () => { cntEl.textContent = Math.round(cnt.v); } }, 1.1);

        // ---------- headline: "You watched it." ----------
        tl.addLabel("watched", 0.08);
        [...chYou, ...chW, ...chIt].forEach((c, i) => {
          tl.fromTo(c, { yPercent: 118, rotation: 8, filter: "blur(10px)" }, { yPercent: 0, rotation: 0, filter: "blur(0px)", duration: 0.55, ease: "expo.out" }, 0.08 + i * 0.028);
        });
        tl.fromTo(["#w-you", "#w-watched", "#w-it"], { "--w": 180 }, { "--w": 700, duration: 0.9, ease: "power2.out" }, 0.08);
        // the underline is a video progress bar that plays to the end
        tl.fromTo("#pbar", { opacity: 0 }, { opacity: 1, duration: 0.15 }, 0.36);
        tl.to("#pbar b", { scale: 1, duration: 0.2, ease: "back.out(2)" }, 0.36);
        tl.to("#pbar i", { scaleX: 1, duration: 0.5, ease: "power1.inOut" }, 0.42);
        tl.fromTo("#pbar b", { x: 0 }, { x: L.watched.slotW - 12, duration: 0.5, ease: "power1.inOut" }, 0.42);

        // ---------- swap to "saved" on the 1.0 downbeat ----------
        tl.to(chW, { yPercent: -118, rotation: -6, duration: 0.24, ease: "power3.in", stagger: 0.012 }, 0.74);
        tl.to("#pbar", { opacity: 0, y: 690, duration: 0.25, ease: "power2.in" }, 0.9);
        tl.to("#m-slot", { x: L.saved.slot, duration: 0.4, ease: "expo.inOut" }, 0.92);
        tl.to("#m-it", { x: L.saved.it, duration: 0.4, ease: "expo.inOut" }, 0.92);
        tl.to("#m-you", { x: L.saved.you, duration: 0.4, ease: "expo.inOut" }, 0.92);
        tl.set("#w-saved", { yPercent: 0 }, 0.99);
        tl.fromTo(chS, { yPercent: 118, rotation: 8 }, { yPercent: 0, rotation: 0, duration: 0.5, ease: "expo.out", stagger: 0.026 }, 0.99);
        tl.fromTo("#w-saved", { "--w": 200 }, { "--w": 700, duration: 0.7, ease: "power2.out" }, 0.99);
        // a bookmark ribbon stamps onto the end of "saved"
        const ribX = L.saved.slotLeft + L.saved.slotW - 18, ribY = 396;
        tl.fromTo("#ribbon", { x: ribX, y: ribY - 260, rotation: -18, opacity: 0 }, { x: ribX, y: ribY, rotation: 8, opacity: 1, duration: 0.42, ease: "back.out(2.2)" }, 1.12);

        // ---------- swap to "forgot" on the 2.0 downbeat ----------
        tl.to(chS, { yPercent: -118, rotation: -6, duration: 0.24, ease: "power3.in", stagger: 0.012 }, 1.74);
        tl.to("#ribbon", { y: ribY - 120, rotation: 40, scale: 0, opacity: 0, duration: 0.3, ease: "back.in(2)" }, 1.8);
        tl.to("#m-slot", { x: L.forgot.slot, duration: 0.4, ease: "expo.inOut" }, 1.92);
        tl.to("#m-it", { x: L.forgot.it, duration: 0.4, ease: "expo.inOut" }, 1.92);
        tl.to("#m-you", { x: L.forgot.you, duration: 0.4, ease: "expo.inOut" }, 1.92);
        tl.set("#w-forgot", { yPercent: 0 }, 1.99);
        tl.fromTo(chF, { yPercent: 118, rotation: 8 }, { yPercent: 0, rotation: 0, duration: 0.5, ease: "expo.out", stagger: 0.026 }, 1.99);
        tl.fromTo("#w-forgot", { "--w": 200 }, { "--w": 700, duration: 0.7, ease: "power2.out" }, 1.99);

        // ---------- erosion: the line and the pile are forgotten ----------
        const eroding = [...chYou, ...chF, ...chIt];
        eroding.forEach((c) => {
          const d = 2.5 + R() * 0.34;
          tl.to(c, { yPercent: -30 - R() * 50, x: (R() - 0.5) * 40, rotation: (R() - 0.5) * 30, opacity: 0, filter: "blur(14px)", duration: 0.44, ease: "power2.in" }, d);
        });
        tl.to(["#w-you", "#w-forgot", "#w-it"], { "--w": 120, duration: 1.0, ease: "power1.in" }, 2.4);
        Object.values(cards).forEach((c) => {
          tl.to(c.el, { filter: "blur(9px) grayscale(1)", opacity: 0.22, duration: 1.0, ease: "power2.inOut" }, 2.3 + R() * 0.35);
          tl.to(c.el, { x: (c.x + c.w / 2 - CX) * 0.06, y: (c.y + c.h / 2 - CY) * 0.06, duration: 1.3, ease: "sine.out" }, 2.3);
        });
        tl.to("#halo", { opacity: 0, duration: 0.8 }, 2.8);

        // ---------- the prompt: ">" appears, types "openwiki" ----------
        const TEXT = "> openwiki";
        const rows = [...document.querySelectorAll(".cline .row")];
        const rowChars = rows.map((row) => [...TEXT].map((ch) => { const s = document.createElement("span"); s.textContent = ch === " " ? " " : ch; if (ch === ">") s.className = "gt"; row.appendChild(s); return s; }));
        const cw = rowChars[0][0].offsetWidth; // monospace advance
        const fullW = cw * TEXT.length;
        // keep whatever is typed centred: shift the row left by half an advance per typed char
        const rowLeft = (n) => CX - (cw * n + cw * 0.72) / 2; // n visible chars + cursor
        rows.forEach((row) => gsap.set(row, { x: rowLeft(1) }));
        const curs = [...document.querySelectorAll(".cline .cur")];
        const curX = (n) => rowLeft(n) + cw * n + 8;
        gsap.set(curs, { x: curX(1) });
        rowChars.forEach((chs) => gsap.set(chs, { opacity: 0 }));
        const lines = ["#cline-paper .row", "#cline-night .row"];

        tl.fromTo(rowChars.map((c) => c[0]), { opacity: 0, scale: 0.4, y: 20 }, { opacity: 1, scale: 1, y: 0, duration: 0.28, ease: "back.out(2.4)" }, 3.3);
        tl.fromTo(curs, { opacity: 0 }, { opacity: 1, duration: 0.05 }, 3.32);
        // blink once while waiting
        tl.set(curs, { opacity: 0 }, 3.42); tl.set(curs, { opacity: 1 }, 3.48);
        const typeT = 3.52, step = 0.055;
        for (let i = 2; i <= TEXT.length; i++) {
          const t = typeT + (i - 2) * step;
          rowChars.forEach((chs) => tl.set(chs[i - 1], { opacity: 1 }, t));
          tl.to(lines, { x: rowLeft(i), duration: 0.12, ease: "power2.out" }, t);
          tl.to(curs, { x: curX(i), duration: 0.12, ease: "power2.out" }, t);
        }
        const endT = typeT + (TEXT.length - 2) * step; // ~3.96

        // ---------- 4.0 downbeat: the pile is sucked into the prompt, the night opens ----------
        const P = { x: curX(TEXT.length) + 33, y: 544 };
        const irisAt = 4.0;
        // the pile lives inside the camera (scale 1.16, offset -8/6 at the end of the suck): map P into camera space
        const Pc = { x: CX + (P.x - CX + 8) / 1.16, y: CY + (P.y - CY - 6) / 1.16 };
        Object.values(cards).forEach((c, i) => {
          const dx = Pc.x - (c.x + c.w / 2), dy = Pc.y - (c.y + c.h / 2);
          tl.to(c.el, { x: dx, y: dy, scale: 0.04, rotation: c.r + (i % 2 ? 140 : -140), opacity: 0.9, filter: "blur(2px) grayscale(0.4)", duration: 0.5, ease: "power3.in" }, irisAt - 0.34 + R() * 0.1);
        });
        tl.to("#camera", { scale: 1.16, duration: 0.5, ease: "power3.in" }, irisAt - 0.36);
        tl.fromTo("#night", { clipPath: `circle(0px at ${P.x}px ${P.y}px)` }, { clipPath: `circle(2300px at ${P.x}px ${P.y}px)`, duration: 0.62, ease: "expo.inOut" }, irisAt - 0.12);
        // a single cursor pulse as the command "runs"
        tl.fromTo("#cline-night .cur", { scale: 1 }, { scale: 1.3, duration: 0.055, ease: "power2.out", yoyo: true, repeat: 1 }, irisAt);

        // ---------- the payoff: the prompt lifts, "Compile it." lands ----------
        // shrink the finished command toward the top; the cursor keeps its place at the end of the line
        const Rc = rowLeft(TEXT.length) + fullW / 2, S = 0.46;
        tl.to("#cline-night .row", { y: -210, scale: S, transformOrigin: "50% 50%", duration: 0.5, ease: "expo.inOut" }, 4.12);
        tl.to("#cline-night .cur", { x: Rc + (curX(TEXT.length) + 33 - Rc) * S - 33, y: -210, scale: S, transformOrigin: "50% 50%", duration: 0.5, ease: "expo.inOut" }, 4.12);
        const chC = splitChars(document.getElementById("w-compile"));
        tl.fromTo(chC, { yPercent: 110, rotation: 10, filter: "blur(12px)" }, { yPercent: 0, rotation: 0, filter: "blur(0px)", duration: 0.6, ease: "expo.out", stagger: 0.03 }, 4.26);
        tl.fromTo("#w-compile", { "--w": 160 }, { "--w": 700, duration: 0.8, ease: "power3.out" }, 4.26);
        tl.fromTo("#compile", { scale: 1.06 }, { scale: 1, duration: 0.9, ease: "expo.out" }, 4.18);

        // amber highlighter underline draws under "Compile" on the 4.5 beat
        const cm = document.getElementById("cmask"), wc = document.getElementById("w-compile");
        const uw = chC.slice(0, 7).reduce((a, c) => a + c.offsetWidth, 0);
        const ul = document.getElementById("uline");
        ul.setAttribute("width", cm.offsetWidth); ul.setAttribute("height", cm.offsetHeight);
        const ux0 = 48, uy = 252;
        const path = document.getElementById("ulpath");
        path.setAttribute("d", `M${ux0} ${uy} C ${ux0 + uw * 0.3} ${uy - 10}, ${ux0 + uw * 0.7} ${uy + 6}, ${ux0 + uw - 10} ${uy - 6}`);
        const len = path.getTotalLength();
        gsap.set(path, { strokeDasharray: len, strokeDashoffset: len });
        tl.to(path, { strokeDashoffset: 0, duration: 0.34, ease: "power3.out" }, 4.48);


  // exit on the 6.0 downbeat: "Compile it." pushes through the lens
  tl.to("#compile", { scale: 1.35, filter: "blur(14px)", opacity: 0, duration: 0.3, ease: "power3.in" }, 5.7);
  tl.to("#cline-night .row, #cline-night .cur", { opacity: 0, duration: 0.2 }, 5.7);
});
