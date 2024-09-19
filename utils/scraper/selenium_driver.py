from tempfile import mkdtemp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from time import sleep
from settings import DEFAULT_TIMEOUT, DOWNLOAD_FOLDER
from utils.logger import logger


class SeleniumDriver(webdriver.Chrome):
    """Custom wrapper around the Chrome Selenium webdriver to store the downloads folder."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_and_verify_url(self, url: str) -> bool:
        """
        Navigate to the specified URL and verify if the browser is on the desired page.
        Returns True if the URL matches, False otherwise.
        """
        self.get(url)
        sleep(DEFAULT_TIMEOUT)  # Wait for the page to load

        # Verify if the current URL matches the expected one
        if self.current_url != url:
            logger.debug(
                f"Failed to navigate to URL: {url}, current URL: {self.current_url}"
            )
            return False
        return True

    def get_html(self) -> BeautifulSoup | None:
        """Extracts and returns the main HTML content from the page using BeautifulSoup."""
        html_source_code = self.execute_script("return document.body.innerHTML;")
        soup = BeautifulSoup(html_source_code, "html.parser")
        self._remove_unwanted_tags(soup)

        main_content = soup.find("div", class_="main-content")
        return main_content if main_content else None

    @staticmethod
    def _remove_unwanted_tags(soup: BeautifulSoup) -> None:
        """Remove unnecessary tags from the HTML."""
        for tag in ["script", "style", "meta", "noscript"]:
            [x.extract() for x in soup.find_all(tag)]


class SeleniumDriverFactory:
    """Factory class for creating a consistent Selenium driver."""

    @staticmethod
    def create_driver(
        chrome_binary_path: str = "/opt/chrome-headless-shell-linux64/chrome-headless-shell",
        chromedriver_binary_path: str = "/opt/chromedriver-linux64/chromedriver",
    ) -> SeleniumDriver:
        """Creates and returns a Selenium driver with specified options."""

        try:
            options = SeleniumDriverFactory._get_driver_options(chrome_binary_path)
            service = SeleniumDriverFactory._get_driver_service(
                chromedriver_binary_path
            )
            return SeleniumDriver(service=service, options=options)
        except Exception as e:
            logger.error(f"Failed to instantiate webdriver: {e}")
            raise RuntimeError(f"Failed to instantiate webdriver: {e}")

    @staticmethod
    def _get_driver_service(chromedriver_binary_path: str) -> ChromeService:
        """Returns the service instance that runs the Chrome WebDriver."""
        return ChromeService(executable_path=chromedriver_binary_path)

    @staticmethod
    def _get_driver_options(chrome_binary_path: str) -> Options:
        """Returns the options configured for the Selenium Chrome WebDriver."""

        options = Options()
        options.binary_location = chrome_binary_path

        # Add essential options for headless Chrome
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280x1696")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-zygote")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Ephemeral user data and cache to avoid persistence
        temp_dir = mkdtemp()
        options.add_argument(f"--user-data-dir={temp_dir}")
        options.add_argument(f"--disk-cache-dir={temp_dir}")

        # Configure download preferences
        prefs = {
            "download.default_directory": DOWNLOAD_FOLDER,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
        }
        options.add_experimental_option("prefs", prefs)

        return options
