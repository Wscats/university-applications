"""
Scraper for The Education University of Hong Kong (EdUHK) master's programs.

Official source: https://www.eduhk.hk/acadprog/postgrad.html
"""

import logging
import re
from typing import List, Optional
from urllib.parse import urljoin

from hk_admissions.models import ProgramInfo, HK_UNIVERSITIES
from hk_admissions.universities.base import BaseUniversityScraper

logger = logging.getLogger(__name__)


class EdUHKScraper(BaseUniversityScraper):
    """Scraper for EdUHK postgraduate programmes."""

    def __init__(self):
        super().__init__(HK_UNIVERSITIES["eduhk"])

    def scrape_programs(self) -> List[ProgramInfo]:
        """
        Scrape EdUHK's postgraduate programme list.

        Official URL: https://www.eduhk.hk/acadprog/postgrad.html
        """
        programs = []
        base_url = self.config.programs_list_url

        soup = self.fetch_page(base_url)
        if not soup:
            logger.error("[EdUHK] Failed to fetch programme list page")
            return self._fallback_programs()

        items = soup.select(
            "table tbody tr, .programme-item, .views-row, "
            ".list-item, a[href*='programme'], a[href*='postgrad']"
        )

        if not items:
            items = soup.find_all(
                "a", href=re.compile(r"programme|program|postgrad|master", re.I)
            )

        for item in items:
            program = self._parse_item(item, base_url)
            if program:
                programs.append(program)

        if not programs:
            programs = self._fallback_programs()

        return programs

    def _parse_item(self, item, base_url: str) -> Optional[ProgramInfo]:
        try:
            link = item if item.name == "a" else item.find("a")
            if not link:
                return None

            name = link.get_text(strip=True)
            href = link.get("href", "")
            if not name or not href or len(name) < 3:
                return None

            program_url = urljoin(base_url, href)
            degree_type = self._extract_degree_type(name)

            return self.create_program(
                program_name=name,
                degree_type=degree_type,
                program_url=program_url,
                data_source=base_url,
            )
        except Exception as e:
            logger.debug(f"[EdUHK] Error parsing item: {e}")
            return None

    def _fallback_programs(self) -> List[ProgramInfo]:
        return [
            self.create_program(
                program_name="All Postgraduate Programmes",
                program_name_cn="所有研究生课程",
                program_url=self.config.programs_list_url,
                data_source=self.config.programs_list_url,
                remarks=(
                    "Auto-scraping was not successful. Please visit the official "
                    "EdUHK academic programmes page for the full programme list."
                ),
            )
        ]

    @staticmethod
    def _extract_degree_type(name: str) -> str:
        name_upper = name.upper()
        for pattern, degree in [
            ("MED", "MEd"), ("MSC", "MSc"), ("MA ", "MA"),
            ("MSSCI", "MSSc"), ("MPHIL", "MPhil"),
        ]:
            if pattern in name_upper:
                return degree
        return "Master"
