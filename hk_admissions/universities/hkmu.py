"""
Scraper for Hong Kong Metropolitan University (HKMU) master's programs.

Official source: https://admissions.hkmu.edu.hk/pg/programmes/
"""

import logging
import re
from typing import List, Optional
from urllib.parse import urljoin

from hk_admissions.models import ProgramInfo, HK_UNIVERSITIES
from hk_admissions.universities.base import BaseUniversityScraper

logger = logging.getLogger(__name__)


class HKMUScraper(BaseUniversityScraper):
    """Scraper for HKMU postgraduate programmes."""

    def __init__(self):
        super().__init__(HK_UNIVERSITIES["hkmu"])

    def scrape_programs(self) -> List[ProgramInfo]:
        """
        Scrape HKMU's postgraduate programme list.

        Official URL: https://admissions.hkmu.edu.hk/pg/programmes/
        """
        programs = []
        base_url = self.config.programs_list_url

        soup = self.fetch_page(base_url)
        if not soup:
            logger.error("[HKMU] Failed to fetch programme list page")
            return self._fallback_programs()

        items = soup.select(
            "table tbody tr, .programme-item, .views-row, "
            ".list-item, .card, a[href*='programme']"
        )

        if not items:
            items = soup.find_all(
                "a", href=re.compile(r"programme|program|master|postgrad", re.I)
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
            logger.debug(f"[HKMU] Error parsing item: {e}")
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
                    "HKMU admissions page for the full programme list."
                ),
            )
        ]

    @staticmethod
    def _extract_degree_type(name: str) -> str:
        name_upper = name.upper()
        for pattern, degree in [
            ("MBA", "MBA"), ("MSC", "MSc"), ("MA ", "MA"),
            ("MED", "MEd"), ("MPHIL", "MPhil"), ("MFA", "MFA"),
        ]:
            if pattern in name_upper:
                return degree
        return "Master"
