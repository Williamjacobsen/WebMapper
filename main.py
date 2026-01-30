from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self):
        # Set up Chrome options
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.binary_location = "/run/current-system/sw/bin/chromium"

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
        self.driver.get(url)

    def close(self):
        if self.driver:
            self.driver.quit()


if __name__ == "__main__":
    scraper = Scraper()
    try:
        scraper.open_page("https://investor.apple.com/sec-filings/default.aspx")
    finally:
        scraper.close()
