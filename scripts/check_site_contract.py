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
PROFILE_PHOTO_SRC = "figs/fig1.jpg"
NOTE_TYPOGRAPHY_MARKERS = [
    ".profile-photo",
    ".notes-directory",
    ".notes-category h2",
    ".notes-preview-list h3",
    ".notes-more",
    ".toc a",
    ".note-card h3",
    ".note-card :not(pre) > code",
    ".note-card table",
    ".note-card blockquote",
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
NOTES_PREVIEW_LIMIT = 3
NOTES_CATEGORIES = {
    "dft": Path("notes/dft/index.html"),
    "tb": Path("notes/tb/index.html"),
    "other": Path("notes/other/index.html"),
}
PUBLICATIONS_INTRO = "Selected work in quasiperiodic systems and localization, with brief abstracts."
GOOGLE_SCHOLAR_URL = "https://scholar.google.com.hk/citations?hl=zh-CN&user=51eUsJkAAAAJ"
APS_PUBLICATION_URLS = [
    "https://journals.aps.org/prl/abstract/10.1103/rl1f-ptzq",
    "https://journals.aps.org/prb/abstract/10.1103/2rfb-j778",
    "https://journals.aps.org/prb/abstract/10.1103/pk8h-xlld",
]
DOI_LINK_URLS = [
    "https://doi.org/10.1103/rl1f-ptzq",
    "https://doi.org/10.1103/2rfb-j778",
    "https://doi.org/10.1103/pk8h-xlld",
]
EXPECTED_PALETTE = {
    "--color-header": "#f5f5f7",
    "--color-header-ink": "#1d1d1f",
    "--color-header-muted": "#6e6e73",
    "--color-paper": "#ffffff",
    "--color-canvas": "#f5f5f7",
    "--color-ink": "#1d1d1f",
    "--color-secondary-ink": "#515154",
    "--color-muted": "#6e6e73",
    "--color-line": "#d2d2d7",
    "--color-accent": "#0066cc",
    "--color-accent-dark": "#004a99",
    "--color-header-line": "#d2d2d7",
}
EXPECTED_SHADOW = "--shadow-paper: 0 8px 24px rgba(29, 29, 31, 0.05);"
EXPECTED_PROFILE_CROP_DECLARATIONS = [
    "grid-template-columns: 280px minmax(0, 1fr);",
    "width: min(100%, 136px);",
    "aspect-ratio: 1 / 1;",
    "object-position: 55% 100%;",
    "border-radius: 50%;",
    "@media (max-width: 900px)",
    "grid-template-columns: 104px minmax(0, 1fr);",
    "font-size: clamp(24px, 2.1vw, 26px);",
]
FORBIDDEN_PALETTE_COLORS = {
    "#e8f0f2",
    "#1f343b",
    "#596c73",
    "#f4f6f6",
    "#242b30",
    "#66727a",
    "#dce4e6",
    "#206a7a",
    "#174f5b",
    "#cbd9dd",
    "#69a7b7",
    "#4f5c63",
    "#f7f9fa",
    "#f6f8fa",
}
CONTRAST_CASES = [
    ("主文字 / 白色表面", "#1d1d1f", "#ffffff", 4.5),
    ("次文字 / 白色表面", "#515154", "#ffffff", 4.5),
    ("弱文字 / 白色表面", "#6e6e73", "#ffffff", 4.5),
    ("弱文字 / 中性画布", "#6e6e73", "#f5f5f7", 4.5),
    ("交互蓝 / 白色表面", "#0066cc", "#ffffff", 4.5),
    ("交互蓝 / 中性画布", "#0066cc", "#f5f5f7", 4.5),
]


def relative_luminance(color: str) -> float:
    channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]

    def linearize(channel: float) -> float:
        if channel <= 0.04045:
            return channel / 12.92
        return ((channel + 0.055) / 1.055) ** 2.4

    red, green, blue = (linearize(channel) for channel in channels)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (relative_luminance(foreground), relative_luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


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
        self.profile_images: list[dict[str, str]] = []
        self.publication_title_hrefs: list[str] = []
        self.heading_level = 0
        self.notes_category: str | None = None
        self.notes_preview_links: dict[str, list[tuple[str, int]]] = {}
        self.notes_more_hrefs: dict[str, list[str]] = {}
        self.images: list[dict[str, str]] = []
        self.all_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        if tag == "nav":
            self.nav_depth += 1
        if "profile-card" in classes:
            self.profile_depth += 1
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.heading_level = int(tag[1])
        if tag == "article" and "notes-category" in classes:
            self.notes_category = attributes.get("data-category") or ""
            self.notes_preview_links.setdefault(self.notes_category, [])
            self.notes_more_hrefs.setdefault(self.notes_category, [])
        if tag == "a" and attributes.get("href"):
            href = attributes["href"] or ""
            self.hrefs.append(href)
            if "publication-title" in classes:
                self.publication_title_hrefs.append(href)
            if self.nav_depth:
                self.nav_hrefs.append(href)
            if self.notes_category and "notes-preview-title" in classes:
                self.notes_preview_links[self.notes_category].append(
                    (href, self.heading_level)
                )
            if self.notes_category and "notes-more" in classes:
                self.notes_more_hrefs[self.notes_category].append(href)
        if tag == "link" and attributes.get("rel") == "stylesheet":
            href = attributes.get("href")
            if href:
                self.stylesheets.append(href)
        if tag == "img":
            image = {
                "src": attributes.get("src") or "",
                "alt": attributes.get("alt") or "",
                "class": attributes.get("class") or "",
            }
            self.images.append(image)
            if self.profile_depth:
                self.profile_images.append(image)
        if tag == "section" and attributes.get("id"):
            self.section_ids.append(attributes["id"] or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav" and self.nav_depth:
            self.nav_depth -= 1
        if tag in {"aside", "section"} and self.profile_depth:
            self.profile_depth -= 1
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.heading_level = 0
        if tag == "article" and self.notes_category is not None:
            self.notes_category = None

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


def managed_note_hrefs(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    start = "<!-- AUTO-NOTES:START -->"
    end = "<!-- AUTO-NOTES:END -->"
    if start not in source or end not in source:
        return []
    managed = source.split(start, 1)[1].split(end, 1)[0]
    parser = PageParser()
    parser.feed(managed)
    parser.close()
    return parser.hrefs


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
    profile_photos = [
        image for image in home.images if "profile-photo" in image["class"].split()
    ]
    profile_card_photos = [
        image for image in home.profile_images if "profile-photo" in image["class"].split()
    ]
    if len(profile_photos) != 1:
        failures.append(f"首页应有且仅有一张 profile-photo，实际为 {len(profile_photos)} 张")
    elif len(profile_card_photos) != 1:
        failures.append("首页照片必须位于左侧 profile-card 内")
    elif profile_photos[0]["src"] != PROFILE_PHOTO_SRC or not profile_photos[0]["alt"].strip():
        failures.append(f"首页照片路径或替代文本不符：{profile_photos[0]}")

    profile_photo = ROOT / PROFILE_PHOTO_SRC
    if not profile_photo.is_file():
        failures.append(f"缺少浏览器兼容的首页照片：{PROFILE_PHOTO_SRC}")
    elif not profile_photo.read_bytes().startswith(b"\xff\xd8\xff"):
        failures.append(f"首页照片不是有效 JPEG：{PROFILE_PHOTO_SRC}")
    home_text = " ".join(home.all_text)
    for item in PRESERVED_RESEARCH_ITEMS:
        if item not in home_text:
            failures.append(f"首页 About me 丢失原研究内容：{item}")
    if "Current projects" in home_text:
        failures.append("首页 About me 不应保留 Current projects")
    if "Condensed Matter Physics · USTC" not in home_text:
        failures.append("顶栏缺少研究方向与学校标识")

    notes = parse(ROOT / "notes.html")
    notes_text = " ".join(notes.all_text)
    for description in SHORT_NOTE_DESCRIPTIONS:
        if description not in home_text:
            failures.append(f"首页 Notes 文案不符：{description}")
        if description in notes_text:
            failures.append(f"独立 Notes 页不应保留重复说明：{description}")
    for category, category_index in NOTES_CATEGORIES.items():
        category_hrefs = managed_note_hrefs(ROOT / category_index)
        expected_preview = [
            (category_index.parent / href).as_posix()
            for href in category_hrefs[:NOTES_PREVIEW_LIMIT]
        ]
        actual_preview = notes.notes_preview_links.get(category, [])
        actual_hrefs = [href for href, _ in actual_preview]
        if actual_hrefs != expected_preview:
            failures.append(
                f"Notes 页 {category} 预览应为 {expected_preview}，实际为 {actual_hrefs}"
            )
        if any(level != 3 for _, level in actual_preview):
            failures.append(f"Notes 页 {category} 的具体笔记标题必须使用三级标题")
        expected_more = (
            [category_index.as_posix()]
            if len(category_hrefs) > NOTES_PREVIEW_LIMIT
            else []
        )
        actual_more = notes.notes_more_hrefs.get(category, [])
        if actual_more != expected_more:
            failures.append(
                f"Notes 页 {category} 的 More … 规则不符：应为 {expected_more}，实际为 {actual_more}"
            )
    if set(notes.notes_preview_links) != set(NOTES_CATEGORIES):
        failures.append(
            f"Notes 页分类不符：{sorted(notes.notes_preview_links)}"
        )

    sync_script = ROOT / "scripts" / "sync_tex_note.py"
    if not sync_script.is_file():
        failures.append("缺少笔记同步脚本：scripts/sync_tex_note.py")
    else:
        sync_source = sync_script.read_text(encoding="utf-8")
        for marker in (
            "NOTES_PREVIEW_LIMIT = 3",
            "def update_notes_overview()",
            "overview_path = update_notes_overview()",
        ):
            if marker not in sync_source:
                failures.append(f"笔记同步脚本缺少总览更新规则：{marker}")

    publications_page = ROOT / "publications.html"
    publications = parse(publications_page)
    publications_source = publications_page.read_text(encoding="utf-8")
    if publications_source.count('class="publication-detail"') != 3:
        failures.append("独立 Publications 页应展示 3 篇详细条目")
    if publications_source.count('class="publication-abstract"') != 3:
        failures.append("独立 Publications 页每篇文章都应包含摘要")
    publications_text = " ".join(publications.all_text)
    if PUBLICATIONS_INTRO in publications_text:
        failures.append("独立 Publications 页不应保留旧导语")
    if GOOGLE_SCHOLAR_URL not in publications.hrefs or "Google Scholar" not in publications_text:
        failures.append("独立 Publications 页缺少 Google Scholar 主页入口")
    unexpected_doi_links = [url for url in DOI_LINK_URLS if url in publications.hrefs]
    if unexpected_doi_links:
        failures.append(f"独立 Publications 页仍保留 DOI 链接：{unexpected_doi_links}")
    if publications.publication_title_hrefs != APS_PUBLICATION_URLS:
        failures.append(f"论文标题 APS 链接不符：{publications.publication_title_hrefs}")

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
        is_note_page = relative == Path("notes.html") or "notes" in relative.parts
        if is_note_page and "fig1" in page.read_text(encoding="utf-8").lower():
            failures.append(f"笔记页不应引用首页照片：{relative}")
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
        source_lower = source.lower()
        if "fig1" in source_lower:
            failures.append("共享样式不应通过背景图等方式向笔记页注入首页照片")
        for marker in (
            "--color-header",
            "--font-body",
            ".home-layout",
            ".profile-card",
            ".profile-school",
            ".site-context",
            ".publication-header",
            ".scholar-link",
            "white-space: nowrap",
            ":focus-visible",
            "@media (max-width: 760px)",
            "prefers-reduced-motion",
        ):
            if marker not in source:
                failures.append(f"共享样式缺少：{marker}")
        for marker in NOTE_TYPOGRAPHY_MARKERS:
            if marker not in source:
                failures.append(f"共享样式缺少照片/笔记排版规则：{marker}")
        if "grid-template-columns: repeat(2, minmax(0, 1fr));" in source:
            failures.append("Notes 总览必须纵向排列，不应继续使用双栏分类网格")
        if ".notes-category:nth-child(3)" in source:
            failures.append("Notes 总览不应再为 Other 分类设置孤立的跨列规则")
        for token, color in EXPECTED_PALETTE.items():
            declaration = f"{token}: {color};"
            if declaration not in source_lower:
                failures.append(f"共享样式色板不符：{declaration}")
        if EXPECTED_SHADOW not in source_lower:
            failures.append(f"共享样式阴影不符：{EXPECTED_SHADOW}")
        for declaration in EXPECTED_PROFILE_CROP_DECLARATIONS:
            if declaration not in source:
                failures.append(f"首页照片裁剪规则不符：{declaration}")
        if "aspect-ratio: 16 / 9;" in source:
            failures.append("移动端首页照片不应继续使用会丢失下半部分的 16:9 裁剪")
        if "width: min(100%, 230px);" in source:
            failures.append("首页圆形头像不应继续使用压过正文的 230px 尺寸")
        for color in sorted(FORBIDDEN_PALETTE_COLORS):
            if color in source_lower:
                failures.append(f"共享样式仍包含旧色：{color}")

    for label, foreground, background, minimum in CONTRAST_CASES:
        ratio = contrast_ratio(foreground, background)
        if ratio < minimum:
            failures.append(f"颜色对比度不足：{label} 为 {ratio:.2f}:1，要求至少 {minimum}:1")

    if failures:
        print("SITE CONTRACT: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"SITE CONTRACT: PASS ({len(actual_pages)} HTML pages checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
