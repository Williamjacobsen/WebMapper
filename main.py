from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class Scraper:
    def __init__(self):
        self.current_url = None

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


if __name__ == "__main__":
    scraper = Scraper()
    try:
        scraper.open_page("https://investor.apple.com/sec-filings/default.aspx")
        print("Page loaded...")

        hrefs = scraper.get_all_href_tags()
        print(hrefs)

        print("Logic finished...")
    finally:
        scraper.close()
