"""
Base scraper class for university admission information collection.

All university-specific scrapers should inherit from BaseUniversityScraper
and implement the `scrape_programs()` method.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from hk_admissions.models import ProgramInfo, UniversityConfig

logger = logging.getLogger(__name__)


class BaseUniversityScraper(ABC):
    """
    Abstract base class for university-specific scrapers.

    Each university scraper must implement `scrape_programs()` to collect
    master's program admission information from the university's official website.
    """

    # Default request settings
    DEFAULT_TIMEOUT = 30
    DEFAULT_RETRY_COUNT = 3
    DEFAULT_RETRY_DELAY = 2  # seconds
    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    }

    def __init__(self, config: UniversityConfig):
        """
        Initialize the scraper with university configuration.

        Args:
            config: UniversityConfig instance with official URLs and metadata.
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        self._collected_programs: List[ProgramInfo] = []

    @property
    def university_name(self) -> str:
        return self.config.name

    @property
    def abbreviation(self) -> str:
        return self.config.abbreviation

    @abstractmethod
    def scrape_programs(self) -> List[ProgramInfo]:
        """
        Scrape master's program admission information from the university's
        official website.

        Returns:
            A list of ProgramInfo objects with admission details.

        Raises:
            ScrapingError: If the scraping process fails.
        """
        pass

    def fetch_page(
        self,
        url: str,
        timeout: Optional[int] = None,
        retry_count: Optional[int] = None,
    ) -> Optional[BeautifulSoup]:
        """
        Fetch a web page and return a BeautifulSoup object.

        Args:
            url: The URL to fetch.
            timeout: Request timeout in seconds.
            retry_count: Number of retry attempts.

        Returns:
            BeautifulSoup object if successful, None otherwise.
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        retry_count = retry_count or self.DEFAULT_RETRY_COUNT

        for attempt in range(1, retry_count + 1):
            try:
                logger.info(
                    f"[{self.abbreviation}] Fetching: {url} (attempt {attempt}/{retry_count})"
                )
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                response.encoding = response.apparent_encoding or "utf-8"
                soup = BeautifulSoup(response.text, "lxml")
                return soup

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"[{self.abbreviation}] Failed to fetch {url}: {e}"
                )
                if attempt < retry_count:
                    time.sleep(self.DEFAULT_RETRY_DELAY * attempt)
                else:
                    logger.error(
                        f"[{self.abbreviation}] All {retry_count} attempts failed for {url}"
                    )
                    return None

    def fetch_json(
        self,
        url: str,
        timeout: Optional[int] = None,
        retry_count: Optional[int] = None,
    ) -> Optional[dict]:
        """
        Fetch a JSON API response.

        Args:
            url: The API URL.
            timeout: Request timeout in seconds.
            retry_count: Number of retry attempts.

        Returns:
            Parsed JSON dict if successful, None otherwise.
        """
        timeout = timeout or self.DEFAULT_TIMEOUT
        retry_count = retry_count or self.DEFAULT_RETRY_COUNT

        for attempt in range(1, retry_count + 1):
            try:
                logger.info(
                    f"[{self.abbreviation}] Fetching JSON: {url} (attempt {attempt}/{retry_count})"
                )
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                return response.json()

            except (requests.exceptions.RequestException, ValueError) as e:
                logger.warning(
                    f"[{self.abbreviation}] Failed to fetch JSON {url}: {e}"
                )
                if attempt < retry_count:
                    time.sleep(self.DEFAULT_RETRY_DELAY * attempt)
                else:
                    logger.error(
                        f"[{self.abbreviation}] All {retry_count} attempts failed for {url}"
                    )
                    return None

    def create_program(self, **kwargs) -> ProgramInfo:
        """
        Create a ProgramInfo instance pre-filled with university details.

        Args:
            **kwargs: Fields to set on the ProgramInfo.

        Returns:
            A ProgramInfo instance.
        """
        program = ProgramInfo(
            university_name=self.config.name,
            university_name_cn=self.config.name_cn,
            university_abbreviation=self.config.abbreviation,
            last_updated=datetime.now().strftime("%Y-%m-%d"),
        )
        for key, value in kwargs.items():
            if hasattr(program, key):
                setattr(program, key, value)
            else:
                logger.warning(f"[{self.abbreviation}] Unknown field: {key}")
        return program

    def collect(self) -> List[ProgramInfo]:
        """
        Main entry point: scrape programs and validate results.

        Returns:
            List of validated ProgramInfo objects.
        """
        logger.info(f"[{self.abbreviation}] Starting collection for {self.university_name}")
        try:
            programs = self.scrape_programs()
            validated = []
            for p in programs:
                missing = p.validate()
                if missing:
                    logger.warning(
                        f"[{self.abbreviation}] Program missing required fields {missing}: "
                        f"{p.program_name or 'Unknown'}"
                    )
                validated.append(p)

            self._collected_programs = validated
            logger.info(
                f"[{self.abbreviation}] Collected {len(validated)} programs from {self.university_name}"
            )
            return validated

        except Exception as e:
            logger.error(
                f"[{self.abbreviation}] Error collecting from {self.university_name}: {e}",
                exc_info=True,
            )
            return []

    def close(self):
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


class ScrapingError(Exception):
    """Custom exception for scraping failures."""
    pass
