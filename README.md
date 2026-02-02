# WebMapper

A small, pragmatic web crawler/scraper built with Selenium + BeautifulSoup.

**WebMapper** (the `Scraper` class) navigates pages using a Chromium WebDriver, extracts `<a href>` links, classifies file vs HTML links, and performs breadth-limited discovery to a configurable depth.

---

## Table of Contents

* [Why WebMapper](#why-webmapper)
* [Features](#features)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Quick start](#quick-start)
* [Usage](#usage)
* [Configuration & customization](#configuration--customization)
* [Core methods & behavior](#core-methods--behavior)
* [Best practices & ethical considerations](#best-practices--ethical-considerations)
* [Troubleshooting](#troubleshooting)
* [Extending WebMapper](#extending-webmapper)
* [Contributing](#contributing)
* [License](#license)

---

## Why WebMapper

WebMapper is intentionally simple and focused: it uses a real browser (Chromium) to render JavaScript-driven pages reliably, then parses the rendered HTML with BeautifulSoup to gather links. It's a good starting point for tasks that require JS execution (search results, single-page apps, dynamically-loaded links) where pure HTTP crawlers fall short.

## Features

* Uses Selenium + Chromium for accurate, JavaScript-aware page rendering
* Extracts and normalizes absolute URLs from anchor tags
* Classifies links into "file" (PDFs, images, archives, multimedia, etc.) vs discoverable HTML pages
* Configurable discovery depth (BFS-style traversal)
* Built-in heuristics to skip non-discoverable or sensitive paths (logins, signouts)
* Easily customizable sets for file extensions, skip paths, and non-discoverable schemes

## Prerequisites

* Python 3.8+
* Chromium browser installed
* Chromedriver binary compatible with your Chromium version

Python packages (see `requirements.txt` below):

```
selenium>=4.10
beautifulsoup4>=4.12
undetected-chromedriver>=3.5
lxml
setuptools
```

## Installation

1. Clone the repository

```bash
git clone https://github.com/Williamjacobsen/WebMapper.git
cd WebMapper
```

2. Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Install Chromium and Chromedriver

On NixOS (example used in the code):

* The script expects Chromium at `/run/current-system/sw/bin/chromium` and Chromedriver at `/run/current-system/sw/bin/chromedriver` — update these paths if your environment differs.

On Debian/Ubuntu or other OSes, install chromium/chromedriver via your package manager or download a matching chromedriver, and update the paths in the code or set them via environment variables (recommended).

## Quick start

Run the bundled script directly:

```bash
python main.py
```

(Or run the `Scraper` in your own script. By default the example in `__main__` runs a breadth-1 discovery for `https://www.google.com/search?q=apple+annual+report+2005`.)

## Usage

Example usage from Python:

```python
from WebMapper import Scraper

scraper = Scraper()
try:
    urls = scraper.run("https://example.com", depth=2)
    for u in sorted(urls):
        print(u)
finally:
    scraper.close()
```

## Configuration & customization

The `Scraper` class exposes easy places to customize behavior:

* `self.chrome_options` — modify or add Chrome options (e.g. `--headless=new`, disable images, change user-agent).
* `self.file_extensions` — set of file extensions considered "file links" (default includes `.pdf`, `.docx`, `.jpg`, `.mp4`, etc.)
* `self.non_discoverable_patterns` — URL prefixes to ignore (e.g. `mailto:`, `javascript:`).
* `self.skip_paths` — path fragments that should make pages non-discoverable (login, register, logout, etc.)
* `Service(executable_path=...)` and `chrome_options.binary_location` — adjust these to point at the Chromium/Chromedriver binaries on your system.

Example: run headless and increase implicit wait

```python
scraper = Scraper()
# enable headless at creation
scraper.chrome_options.add_argument("--headless=new")
# reduce timeout
scraper.wait = WebDriverWait(scraper.driver, 10)
```

## Core methods & behavior

* `open_page(url)` — navigates to the URL with Selenium and sets `self.current_url`.
* `get_all_href_tags()` — waits for at least one `<a>` tag, then parses the current page's HTML with BeautifulSoup, extracts all `href` attributes, and returns a de-duplicated set of absolute URLs (resolved via `urljoin`).
* `isFile(url)` — returns `True` when the URL's path ends with a known file extension.
* `get_file_links(links)` — filters a list of links, returning only file links.
* `isDiscoverable(url)` — applies heuristics (scheme, file test, non-discoverable patterns, skip paths) to decide if a link should be queued for further discovery.
* `get_discoverable_links(links)` — filters links with `isDiscoverable`.
* `run(url, depth=0)` — BFS traversal from the start URL up to `depth` levels. Returns a set of all collected absolute URLs.

Notes on `run` behavior:

* `depth=0` visits only the start URL. `depth=1` visits start URL and extracts links from it (but does not navigate the extracted links unless you increase depth).
* The traversal avoids revisiting URLs already in `has_discovered_urls`.

## Troubleshooting

**Chromedriver/Chromium mismatch**

* Error: `session not created: This version of ChromeDriver only supports Chrome version X` — install a chromedriver that matches your Chromium version.

**Binary path errors**

* Update `chrome_options.binary_location` to your Chromium binary. If running in a container or CI, ensure Chromium is installed.

**Timeouts waiting for elements**

* `WebDriverWait` may time out if a page has no anchors or loads slowly. Increase the wait timeout or catch the exception if anchors are optional.

**Running headless in containers**

* In some environments, you may need `--no-sandbox`, `--disable-dev-shm-usage`, or to allocate `/dev/shm`. Use caution and understand security implications.

## License

This project is provided under the **MIT License** — see `LICENSE` for details.

