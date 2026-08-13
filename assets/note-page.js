(() => {
  "use strict";

  const root = document.documentElement;
  const isChinese = root.lang.toLowerCase().startsWith("zh");
  const toc = document.querySelector(".toc");
  const tocList = document.getElementById("toc-list");
  const layout = document.querySelector("main.note-layout");
  const article = document.querySelector(".note-card");
  const content = document.querySelector(".note-content") || article;
  const languageSwitch = document.querySelector(".language-switch");
  const alternate = root.dataset.noteAlternate;

  const year = document.getElementById("year");
  if (year) {
    year.textContent = String(new Date().getFullYear());
  }

  if (languageSwitch && alternate) {
    const updateAlternateHref = () => {
      const target = new URL(alternate, window.location.href);
      target.hash = window.location.hash;
      languageSwitch.href = target.href;
    };
    updateAlternateHref();
    window.addEventListener("hashchange", updateAlternateHref);
  }

  const headings = content ? Array.from(content.querySelectorAll("h2")) : [];
  if (tocList) {
    tocList.replaceChildren();
    headings.forEach((heading, index) => {
      if (!heading.id) {
        heading.id = `section-${index + 1}`;
      }
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = `#${heading.id}`;
      link.textContent = heading.textContent || "";
      item.appendChild(link);
      tocList.appendChild(item);
    });
  }

  if (toc) {
    if (layout && article && toc.parentElement === article) {
      layout.appendChild(toc);
    }
    const toggle = document.createElement("button");
    toggle.className = "toc-toggle";
    toggle.type = "button";
    toggle.textContent = isChinese ? "目录" : "Contents";
    toggle.setAttribute("aria-controls", toc.id || "note-toc");
    toggle.setAttribute("aria-expanded", "false");
    if (!toc.id) {
      toc.id = "note-toc";
    }
    document.body.appendChild(toggle);

    const setOpen = (open) => {
      toc.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
    };

    toggle.addEventListener("click", () => {
      setOpen(!toc.classList.contains("is-open"));
    });
    toc.addEventListener("click", (event) => {
      if (event.target.closest("a")) {
        setOpen(false);
      }
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && toc.classList.contains("is-open")) {
        setOpen(false);
        toggle.focus();
      }
    });
  }

  const markOverflowingMath = () => {
    document.querySelectorAll(".math-viewport").forEach((viewport) => {
      const overflowing = viewport.scrollWidth > viewport.clientWidth + 2;
      viewport.classList.toggle("is-overflowing", overflowing);
      if (overflowing) {
        viewport.setAttribute("tabindex", "0");
      } else {
        viewport.removeAttribute("tabindex");
      }
    });
  };

  document.querySelectorAll(".math-viewport").forEach((viewport) => {
    viewport.addEventListener("keydown", (event) => {
      if (!viewport.classList.contains("is-overflowing")) {
        return;
      }
      const distance = Math.max(48, Math.round(viewport.clientWidth * 0.28));
      if (event.key === "ArrowRight") {
        event.preventDefault();
        viewport.scrollBy({ left: distance, behavior: "smooth" });
      } else if (event.key === "ArrowLeft") {
        event.preventDefault();
        viewport.scrollBy({ left: -distance, behavior: "smooth" });
      } else if (event.key === "Home") {
        event.preventDefault();
        viewport.scrollTo({ left: 0, behavior: "smooth" });
      } else if (event.key === "End") {
        event.preventDefault();
        viewport.scrollTo({ left: viewport.scrollWidth, behavior: "smooth" });
      }
    });
  });

  window.addEventListener("load", markOverflowingMath);
  window.addEventListener("resize", markOverflowingMath);
  setTimeout(markOverflowingMath, 800);

  if (window.hljs) {
    window.hljs.highlightAll();
  }
})();
