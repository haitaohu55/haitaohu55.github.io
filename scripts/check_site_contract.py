#!/usr/bin/env python3
"""检查个人主页 v1 的页面结构、链接和共享样式。"""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ROOT_PAGES = {
    "index.html",
    "notes.html",
    "publications.html",
}
FORBIDDEN_ROOT_PAGES = {"contact.html"}
HOME_NAV = ["notes.html", "publications.html", "#contact"]
HOME_SECTIONS = ["about", "notes", "publications", "contact"]
PROFILE_LINES = [
    "Haitao Hu",
    "Ph.D. in Condensed Matter Physics",
    "University of Science and Technology of China",
]
PRESERVED_RESEARCH_ITEMS = [
    "Anderson localization in quasiperiodic systems",
    "Electronic structure and band topology of 2D materials",
]
SHORT_NOTE_DESCRIPTIONS = [
    "Short notes on first-principles calculations.",
    "Short notes on tight-binding calculations.",
    "Other short notes.",
]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.stylesheets: list[str] = []
        self.section_ids: list[str] = []
        self.nav_depth = 0
        self.nav_hrefs: list[str] = []
        self.profile_depth = 0
        self.profile_text: list[str] = []
        self.all_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        if tag == "nav":
            self.nav_depth += 1
        if "profile-card" in classes:
            self.profile_depth += 1
        if tag == "a" and attributes.get("href"):
            href = attributes["href"] or ""
            self.hrefs.append(href)
            if self.nav_depth:
                self.nav_hrefs.append(href)
        if tag == "link" and attributes.get("rel") == "stylesheet":
            href = attributes.get("href")
            if href:
                self.stylesheets.append(href)
        if tag == "section" and attributes.get("id"):
            self.section_ids.append(attributes["id"] or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav" and self.nav_depth:
            self.nav_depth -= 1
        if tag in {"aside", "section"} and self.profile_depth:
            self.profile_depth -= 1

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if value:
            self.all_text.append(value)
        if self.profile_depth:
            if value:
                self.profile_text.append(value)


def parse(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


def local_target(page: Path, href: str) -> Path | None:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or href.startswith(("mailto:", "#", "{{")):
        return None
    raw_path = unquote(parsed.path)
    if not raw_path:
        return None
    if raw_path.startswith("/"):
        return ROOT / raw_path.lstrip("/")
    return page.parent / raw_path


def main() -> int:
    failures: list[str] = []

    for relative in sorted(REQUIRED_ROOT_PAGES):
        if not (ROOT / relative).is_file():
            failures.append(f"缺少独立页面：{relative}")
    for relative in sorted(FORBIDDEN_ROOT_PAGES):
        if (ROOT / relative).exists():
            failures.append(f"不应保留独立页面：{relative}")

    home = parse(ROOT / "index.html")
    if home.nav_hrefs != HOME_NAV:
        failures.append(f"首页导航应为 {HOME_NAV}，实际为 {home.nav_hrefs}")
    if home.section_ids != HOME_SECTIONS:
        failures.append(f"首页区块应为 {HOME_SECTIONS}，实际为 {home.section_ids}")
    if home.profile_text != PROFILE_LINES:
        failures.append(f"左侧身份信息不符：{home.profile_text}")
    home_text = " ".join(home.all_text)
    for item in PRESERVED_RESEARCH_ITEMS:
        if item not in home_text:
            failures.append(f"首页 About me 丢失原研究内容：{item}")
    if "Current projects" in home_text:
        failures.append("首页 About me 不应保留 Current projects")
    if "Condensed Matter Physics · USTC" not in home_text:
        failures.append("顶栏缺少研究方向与学校标识")

    notes_text = " ".join(parse(ROOT / "notes.html").all_text)
    for description in SHORT_NOTE_DESCRIPTIONS:
        if description not in home_text:
            failures.append(f"首页 Notes 文案不符：{description}")
        if description not in notes_text:
            failures.append(f"独立 Notes 页文案不符：{description}")

    publications_source = (ROOT / "publications.html").read_text(encoding="utf-8")
    if publications_source.count('class="publication-detail"') != 3:
        failures.append("独立 Publications 页应展示 3 篇详细条目")
    if publications_source.count('class="publication-abstract"') != 3:
        failures.append("独立 Publications 页每篇文章都应包含摘要")
    for doi in ("rl1f-ptzq", "2rfb-j778", "pk8h-xlld"):
        if doi not in publications_source:
            failures.append(f"独立 Publications 页缺少 DOI：{doi}")

    actual_pages = [ROOT / "index.html"]
    actual_pages.extend(
        ROOT / relative
        for relative in sorted(REQUIRED_ROOT_PAGES - {"index.html"})
        if (ROOT / relative).is_file()
    )
    actual_pages.extend(sorted((ROOT / "notes").rglob("*.html")))
    actual_pages.append(ROOT / "templates" / "note_page.html")
    for page in actual_pages:
        parsed = parse(page)
        relative = page.relative_to(ROOT)
        if page.name == "note_page.html" and page.parent.name == "templates":
            if "../../assets/site.css" not in parsed.stylesheets:
                failures.append("笔记模板未引用生成页面所需的共享样式")
        elif not any(href.endswith("assets/site.css") for href in parsed.stylesheets):
            failures.append(f"未引用共享样式：{relative}")

        links_to_check = parsed.hrefs + parsed.stylesheets
        if page == ROOT / "templates" / "note_page.html":
            links_to_check = parsed.hrefs
        for href in links_to_check:
            target = local_target(page, href)
            if target is not None and not target.resolve().is_file():
                failures.append(f"断开的本地链接：{relative} -> {href}")

    css = ROOT / "assets" / "site.css"
    if not css.is_file():
        failures.append("缺少共享样式：assets/site.css")
    else:
        source = css.read_text(encoding="utf-8")
        for marker in (
            "--color-header",
            "--font-body",
            ".home-layout",
            ".profile-card",
            ".profile-school",
            ".site-context",
            "white-space: nowrap",
            ":focus-visible",
            "@media (max-width: 760px)",
            "prefers-reduced-motion",
        ):
            if marker not in source:
                failures.append(f"共享样式缺少：{marker}")

    if failures:
        print("SITE CONTRACT: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"SITE CONTRACT: PASS ({len(actual_pages)} HTML pages checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
