from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from urllib.parse import ParseResult, urljoin, urlparse
import os


class Scraper:
    def __init__(self):
        # Set up Chrome options
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.binary_location = "/run/current-system/sw/bin/chromium"
        # self.chrome_options.page_load_strategy = "eager"  # Don't wait for images

        # Optional: Add arguments to make it less detectable
        self.chrome_options.add_argument(
            "--disable-blink-features=AutomationControlled"
        )
        self.chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-automation"]
        )
        self.chrome_options.add_experimental_option("useAutomationExtension", False)

        # Use system chromedriver
        service = Service(executable_path="/run/current-system/sw/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

        self.current_url = None

        self.file_extensions = {
            # Documents
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".txt",
            ".csv",
            ".rtf",
            ".odt",
            ".ods",
            ".odp",
            # Images
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".svg",
            ".webp",
            ".ico",
            # Archives
            ".zip",
            ".rar",
            ".tar",
            ".gz",
            ".7z",
            ".bz2",
            # Media
            ".mp4",
            ".avi",
            ".mov",
            ".wmv",
            ".flv",
            ".mp3",
            ".wav",
            ".ogg",
            # Code/Data
            ".json",
            ".xml",
            ".yaml",
            ".yml",
            ".sql",
            # Other
            ".exe",
            ".dmg",
            ".apk",
            ".jar",
        }

        self.non_discoverable_patterns = [
            "javascript:",
            "mailto:",
            "tel:",
            "ftp:",
            "file:",
            "#",  # Fragment-only links
        ]

        self.skip_paths = [
            "/logout",
            "/signout",
            "/sign-out",
            "/login",
            "/signin",
            "/sign-in",
            "/register",
            "/signup",
            "/sign-up",
        ]

    def open_page(self, url):
        self.current_url = url
        self.driver.get(url)

    def close(self):
        if self.driver:
            self.driver.quit()

    def wait_until_loaded(self, by, tag):
        self.wait.until(EC.presence_of_all_elements_located((by, tag)))

    def remove_duplicates(self, array):
        return set(array)

    def get_all_href_tags(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        except Exception:
            print("  Warning: No anchor tags found on page")
            return set()

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        anchor_tags = soup.find_all("a", href=True)

        hrefs = []
        for anchor in anchor_tags:
            href = anchor.get("href")
            if isinstance(href, str):
                hrefs.append(href)

        current_url = self.driver.current_url
        absolute_hrefs = [urljoin(current_url, href) for href in hrefs]

        return self.remove_duplicates(absolute_hrefs)

    def isFile(self, url):
        parsed = urlparse(url)

        path = parsed.path

        _, ext = os.path.splitext(path)

        return ext.lower() in self.file_extensions

    def get_file_links(self, links):
        return [url for url in links if self.isFile(url)]

    def isDiscoverable(self, url):
        parsed = urlparse(url)

        if self.isFile(url):
            return False

        url_lower = url.lower()
        for pattern in self.non_discoverable_patterns:
            if url_lower.startswith(pattern):
                return False

        path_lower = parsed.path.lower()
        for skip in self.skip_paths:
            if skip in path_lower:
                return False

        if parsed.scheme and parsed.scheme not in ["http", "https"]:
            return False

        return True

    def get_discoverable_links(self, links):
        return [url for url in links if self.isDiscoverable(url)]

    def run(self, url, depth=0):
        all_urls = set()
        to_discover_urls = set([url])
        has_discovered_urls = set()
        current_depth = 0

        while to_discover_urls and current_depth <= depth:
            urls_at_current_level = list(to_discover_urls)
            to_discover_urls.clear()

            for current_url_to_discover in urls_at_current_level:
                if current_url_to_discover in has_discovered_urls:
                    continue

                print(f"Discovering (depth {current_depth}): {current_url_to_discover}")

                try:
                    self.open_page(current_url_to_discover)
                    has_discovered_urls.add(current_url_to_discover)

                    local_urls = self.get_all_href_tags()
                    all_urls.update(local_urls)

                    discoverable_urls = self.get_discoverable_links(local_urls)
                    for local_url in discoverable_urls:
                        if local_url not in has_discovered_urls:
                            to_discover_urls.add(local_url)
                except Exception as e:
                    print(f"Error discovering {current_url_to_discover}: {e}")

            current_depth += 1

        return all_urls


if __name__ == "__main__":
    scraper = Scraper()

    try:
        urls = scraper.run(
            "https://www.google.com/search?q=apple+annual+report+2005", depth=1
        )
        print(urls)
    finally:
        scraper.close()
