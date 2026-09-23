// Small progressive enhancements. The page works fully without this file.
(() => {
  const root = document.querySelector(".ow");

  // Keep the hover-blur off until the entrance has played, so rows under a
  // resting cursor don't blur the page on load.
  if (root) {
    root.setAttribute("data-hover-cold", "");
    const warm = () => root.removeAttribute("data-hover-cold");
    setTimeout(() => window.addEventListener("pointermove", warm, { once: true }), 700);
  }

  // Copy buttons on code cards.
  document.querySelectorAll(".code").forEach((card) => {
    const pre = card.querySelector("pre");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "copy";
    button.textContent = "copy";
    button.setAttribute("aria-label", "Copy command");
    button.addEventListener("click", async () => {
      const text = [...pre.querySelectorAll(".cmd")].map((line) => line.textContent).join("\n") || pre.textContent;
      try {
        await navigator.clipboard.writeText(text.trim());
      } catch {
        const area = Object.assign(document.createElement("textarea"), { value: text.trim() });
        document.body.append(area);
        area.select();
        document.execCommand("copy");
        area.remove();
      }
      button.textContent = "copied";
      button.setAttribute("data-done", "");
      setTimeout(() => {
        button.textContent = "copy";
        button.removeAttribute("data-done");
      }, 1400);
    });
    card.append(button);
  });

  // The floating back button fades while scrolling and returns when you stop.
  const back = document.querySelector(".back");
  if (back) {
    let timer;
    window.addEventListener("scroll", () => {
      back.classList.add("back--scrolling");
      clearTimeout(timer);
      timer = setTimeout(() => back.classList.remove("back--scrolling"), 220);
    }, { passive: true });
  }
})();
