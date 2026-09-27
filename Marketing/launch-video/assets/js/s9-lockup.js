// Scene 9 (37.3-44.0): lockup. The icon is rebuilt in CSS from Marketing/Logo.png (the PNG is only 187px).
FILM.scene(function (tl) {
  const T = 37.3;
  tl.fromTo("#s9", { clipPath: "circle(0px at 960px 540px)" }, { clipPath: "circle(1300px at 960px 540px)", duration: 0.55, ease: "expo.inOut" }, T);

  tl.fromTo("#s9-icon", { scale: 0, rotation: -14 }, { scale: 1, rotation: 0, duration: 0.6, ease: "back.out(1.8)" }, T + 0.3);
  // the ">" blinks like a prompt
  tl.set("#s9-icon .ai-gt", { opacity: 0 }, T + 0.95); tl.set("#s9-icon .ai-gt", { opacity: 1 }, T + 1.1);

  const name = FILM.chars("#s9-name");
  FILM.inkIn(tl, name, T + 0.45, { stagger: 0.035, dur: 0.6, swell: "#s9-name" });
  tl.fromTo("#s9-lock", { x: 40 }, { x: 0, duration: 1.0, ease: "expo.out" }, T + 0.3);

  const tag = FILM.words("#s9-tag");
  FILM.inkIn(tl, tag, T + 1.15, { stagger: 0.06, dur: 0.55, swell: "#s9-tag", to: 520 });

  tl.fromTo("#s9-pip", { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5, ease: "expo.out" }, T + 1.8);
  const pip = FILM.$("#s9-pip");
  const cmdNode = pip.childNodes[pip.childNodes.length - 1];
  const cmd = document.createElement("span"); cmd.textContent = cmdNode.textContent; cmdNode.remove(); pip.appendChild(cmd);
  const cs = FILM.chars(cmd); gsap.set(cs, { opacity: 0 });
  cs.forEach((c, i) => tl.set(c, { opacity: 1 }, T + 1.95 + i * 0.028));
  tl.fromTo("#s9-gh", { y: 20, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: "power2.out" }, T + 2.7);
  tl.fromTo("#s9-foot", { opacity: 0 }, { opacity: 1, duration: 0.5 }, T + 3.0);

  // a slow settle so the hold never freezes
  tl.fromTo(["#s9-lock", "#s9-tag", "#s9-cta"], { scale: 1 }, { scale: 1.025, duration: 5.5, ease: "sine.inOut", transformOrigin: "50% 50%" }, T + 1.2);
});
