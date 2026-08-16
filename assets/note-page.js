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
  // NOTE-CATALOG:START
  const noteCatalog = {
    "dft": [
      {
        "zh": "electron-phonon-coupling.html",
        "en": "electron-phonon-coupling.en.html",
        "zhTitle": "电声耦合计算",
        "enTitle": "Electron–Phonon Coupling Calculation"
      },
      {
        "zh": "effective-mass.html",
        "en": "effective-mass.en.html",
        "zhTitle": "有效质量计算",
        "enTitle": "Effective Mass Calculation"
      },
      {
        "zh": "phonon-spectrum.html",
        "en": "phonon-spectrum.en.html",
        "zhTitle": "声子谱的计算",
        "enTitle": "Phonon Spectrum Calculation"
      },
      {
        "zh": "linux.html",
        "en": "linux.en.html",
        "zhTitle": "Some common Linux commands",
        "enTitle": "Some common Linux commands"
      },
      {
        "zh": "opt.zh.html",
        "en": "opt.html",
        "zhTitle": "使用 VASP 进行结构优化",
        "enTitle": "Structure Optimization using VASP"
      },
      {
        "zh": "band-structure.html",
        "en": "band-structure.en.html",
        "zhTitle": "能带计算",
        "enTitle": "Band Structure Calculation"
      }
    ],
    "tb": [
      {
        "zh": "交错磁1.html",
        "en": "交错磁1.en.html",
        "zhTitle": "交错磁1",
        "enTitle": "Altermagnetism I"
      },
      {
        "zh": "Hubbard模型上的自洽平均场.html",
        "en": "Hubbard模型上的自洽平均场.en.html",
        "zhTitle": "Hubbard 模型上的自洽平均场",
        "enTitle": "Self-Consistent Mean-Field Theory for the Hubbard Model"
      },
      {
        "zh": "准周期2.html",
        "en": "准周期2.en.html",
        "zhTitle": "准周期2",
        "enTitle": "Quasiperiodic Systems II"
      },
      {
        "zh": "准周期1.html",
        "en": "准周期1.en.html",
        "zhTitle": "准周期1",
        "enTitle": "Quasiperiodic Systems I"
      },
      {
        "zh": "二次量子化.html",
        "en": "二次量子化.en.html",
        "zhTitle": "二次量子化",
        "enTitle": "Second Quantization"
      },
      {
        "zh": "IsingMC.html",
        "en": "IsingMC.en.html",
        "zhTitle": "Ising 模型的 Monte Carlo 模拟",
        "enTitle": "Monte Carlo Simulation of the Ising Model"
      },
      {
        "zh": "精确对角化.html",
        "en": "精确对角化.en.html",
        "zhTitle": "精确对角化",
        "enTitle": "Exact Diagonalization"
      }
    ],
    "other": [
      {
        "zh": "git.html",
        "en": "git.en.html",
        "zhTitle": "git",
        "enTitle": "git"
      }
    ]
  };
  // NOTE-CATALOG:END

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

    const headerContainer = document.querySelector("header .nav-container");
    if (headerContainer) {
      headerContainer.classList.add("note-nav");
    }
    const existingMenu = document.querySelector(".language-menu");
    if (headerContainer && existingMenu && existingMenu.parentElement !== headerContainer) {
      headerContainer.appendChild(existingMenu);
    }
    const legacyHeading = article ? article.querySelector(".note-heading") : null;
    if (legacyHeading) {
      const title = legacyHeading.querySelector("h1");
      if (title) {
        legacyHeading.replaceWith(title);
      }
    }
    if (headerContainer && !headerContainer.querySelector(".language-menu")) {
      const menu = document.createElement("details");
      menu.className = "language-menu";
      const menuButton = document.createElement("summary");
      menuButton.textContent = "Language";
      menuButton.setAttribute("aria-label", "Choose language");
      const options = document.createElement("div");
      options.className = "language-options";

      const makeCurrentOption = (label, lang) => {
        const current = document.createElement("span");
        current.lang = lang;
        current.textContent = label;
        current.setAttribute("aria-current", "page");
        return current;
      };
      languageSwitch.className = "language-option";
      languageSwitch.textContent = isChinese ? "English" : "中文";

      if (isChinese) {
        options.append(makeCurrentOption("中文", "zh-CN"), languageSwitch);
      } else {
        options.append(languageSwitch, makeCurrentOption("English", "en"));
      }
      menu.append(menuButton, options);
      headerContainer.appendChild(menu);

      document.addEventListener("click", (event) => {
        if (menu.open && !menu.contains(event.target)) {
          menu.removeAttribute("open");
        }
      });
      menu.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && menu.open) {
          menu.removeAttribute("open");
          menuButton.focus();
        }
      });
    }
    if (document.querySelector("header .language-menu")) {
      languageSwitch.textContent = isChinese ? "English" : "中文";
    }
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

  const currentFilename = decodeURIComponent(
    window.location.pathname.split("/").pop() || ""
  );
  const categoryBreadcrumb = document.querySelector(".breadcrumbs a[href='index.html']");
  if (categoryBreadcrumb && isChinese) {
    categoryBreadcrumb.href = "index.zh.html";
  }
  const catalogMatch = Object.entries(noteCatalog).find(([, entries]) =>
    entries.some((entry) => entry.zh === currentFilename || entry.en === currentFilename)
  );
  if (article && catalogMatch) {
    const [, entries] = catalogMatch;
    const currentIndex = entries.findIndex(
      (entry) => entry.zh === currentFilename || entry.en === currentFilename
    );
    const languageKey = isChinese ? "zh" : "en";
    const titleKey = isChinese ? "zhTitle" : "enTitle";
    const labels = isChinese
      ? { previous: "上一篇", next: "下一篇", all: "全部笔记", home: "主页" }
      : { previous: "Previous", next: "Next", all: "All notes", home: "Home" };
    const pagination = document.createElement("nav");
    pagination.className = "note-pagination";
    pagination.setAttribute("aria-label", isChinese ? "笔记导航" : "Note navigation");

    const makeNeighbor = (entry, direction) => {
      if (!entry) {
        const placeholder = document.createElement("span");
        placeholder.className = `note-neighbor note-neighbor--${direction} is-empty`;
        placeholder.setAttribute("aria-hidden", "true");
        return placeholder;
      }
      const link = document.createElement("a");
      link.className = `note-neighbor note-neighbor--${direction}`;
      link.href = entry[languageKey];
      const relation = document.createElement("span");
      relation.className = "note-neighbor__relation";
      relation.textContent = direction === "previous"
        ? `← ${labels.previous}`
        : `${labels.next} →`;
      const linkedTitle = document.createElement("span");
      linkedTitle.className = "note-neighbor__title";
      linkedTitle.textContent = entry[titleKey];
      link.append(relation, linkedTitle);
      return link;
    };

    const exits = document.createElement("div");
    exits.className = "note-pagination__exits";
    const allNotes = document.createElement("a");
    allNotes.href = isChinese ? "../../notes.zh.html" : "../../notes.html";
    allNotes.textContent = labels.all;
    const home = document.createElement("a");
    home.href = "../../index.html";
    home.textContent = labels.home;
    exits.append(allNotes, home);

    pagination.append(
      makeNeighbor(entries[currentIndex - 1], "previous"),
      exits,
      makeNeighbor(entries[currentIndex + 1], "next")
    );
    article.appendChild(pagination);
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
