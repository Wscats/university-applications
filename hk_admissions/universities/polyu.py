"""
Scraper for The Hong Kong Polytechnic University (PolyU) master's programs.

Official source: https://www.polyu.edu.hk/study/pg/taught-postgraduate-programmes
"""

import logging
import re
from typing import List, Optional
from urllib.parse import urljoin

from hk_admissions.models import ProgramInfo, HK_UNIVERSITIES
from hk_admissions.universities.base import BaseUniversityScraper

logger = logging.getLogger(__name__)


class PolyUScraper(BaseUniversityScraper):
    """Scraper for PolyU taught postgraduate programmes."""

    def __init__(self):
        super().__init__(HK_UNIVERSITIES["polyu"])

    def scrape_programs(self) -> List[ProgramInfo]:
        """
        Scrape PolyU's taught postgraduate programme list.

        Official URL: https://www.polyu.edu.hk/study/pg/taught-postgraduate-programmes
        """
        programs = []
        base_url = self.config.programs_list_url

        soup = self.fetch_page(base_url)
        if not soup:
            logger.error("[PolyU] Failed to fetch programme list page")
            return self._fallback_programs()

        # PolyU programme list structure
        items = soup.select(
            ".programme-item, .programme-card, .program-list-item, "
            "table tbody tr, .views-row, .card, .list-item"
        )

        if not items:
            items = soup.find_all(
                "a", href=re.compile(r"programme|program|study/pg", re.I)
            )

        for item in items:
            program = self._parse_item(item, base_url)
            if program:
                programs.append(program)

        if not programs:
            programs = self._fallback_programs()

        return programs

    def _parse_item(self, item, base_url: str) -> Optional[ProgramInfo]:
        """Parse a programme item."""
        try:
            link = item if item.name == "a" else item.find("a")
            if not link:
                return None

            name = link.get_text(strip=True)
            href = link.get("href", "")
            if not name or not href or len(name) < 3:
                return None

            program_url = urljoin(base_url, href)

            # Extract faculty from parent section
            faculty = ""
            section = item.find_parent(class_=re.compile(r"faculty|department|school"))
            if section:
                header = section.find(re.compile(r"h[2-4]"))
                if header:
                    faculty = header.get_text(strip=True)

            degree_type = self._extract_degree_type(name)

            return self.create_program(
                program_name=name,
                faculty=faculty,
                degree_type=degree_type,
                program_url=program_url,
                data_source=base_url,
            )
        except Exception as e:
            logger.debug(f"[PolyU] Error parsing item: {e}")
            return None

    def _fallback_programs(self) -> List[ProgramInfo]:
        return [
            self.create_program(
                program_name="All Taught Postgraduate Programmes",
                program_name_cn="所有授课型研究生课程",
                program_url=self.config.programs_list_url,
                data_source=self.config.programs_list_url,
                remarks=(
                    "Auto-scraping was not successful. Please visit the official "
                    "PolyU study page for the full programme list."
                ),
            )
        ]

    @staticmethod
    def _extract_degree_type(name: str) -> str:
        name_upper = name.upper()
        for pattern, degree in [
            ("MBA", "MBA"), ("MSC", "MSc"), ("MA ", "MA"),
            ("MED", "MEd"), ("MPHIL", "MPhil"), ("LLM", "LLM"),
        ]:
            if pattern in name_upper:
                return degree
        return "Master"
