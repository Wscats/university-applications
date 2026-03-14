"""
Scraper for The Chinese University of Hong Kong (CUHK) master's programs.

Official source: https://admissions.gs.cuhk.edu.hk/admissions/programme-list
"""

import logging
import re
from typing import List, Optional
from urllib.parse import urljoin

from hk_admissions.models import ProgramInfo, HK_UNIVERSITIES
from hk_admissions.universities.base import BaseUniversityScraper

logger = logging.getLogger(__name__)


class CUHKScraper(BaseUniversityScraper):
    """Scraper for CUHK taught postgraduate programmes."""

    def __init__(self):
        super().__init__(HK_UNIVERSITIES["cuhk"])

    def scrape_programs(self) -> List[ProgramInfo]:
        """
        Scrape CUHK's taught postgraduate programme list.

        Official URL: https://admissions.gs.cuhk.edu.hk/admissions/programme-list
        """
        programs = []
        base_url = self.config.programs_list_url

        soup = self.fetch_page(base_url)
        if not soup:
            logger.error("[CUHK] Failed to fetch programme list page")
            return self._fallback_programs()

        # CUHK typically lists programmes in a table or card layout
        rows = soup.select(
            "table tbody tr, .programme-item, .views-row, "
            ".program-listing .item, .list-group-item"
        )

        if not rows:
            # Try finding programme links directly
            rows = soup.find_all(
                "a", href=re.compile(r"programme|program|admission", re.I)
            )

        for row in rows:
            program = self._parse_row(row, base_url)
            if program:
                programs.append(program)

        if not programs:
            programs = self._fallback_programs()

        return programs

    def _parse_row(self, row, base_url: str) -> Optional[ProgramInfo]:
        """Parse a programme row from the list."""
        try:
            link = row if row.name == "a" else row.find("a")
            if not link:
                return None

            name = link.get_text(strip=True)
            href = link.get("href", "")

            if not name or not href or len(name) < 3:
                return None

            program_url = urljoin(base_url, href)

            # Extract additional info from table cells if available
            cells = row.find_all("td") if row.name == "tr" else []
            faculty = cells[0].get_text(strip=True) if len(cells) > 1 else ""
            deadline = ""
            if len(cells) > 2:
                deadline = cells[2].get_text(strip=True)

            return self.create_program(
                program_name=name,
                faculty=faculty,
                degree_type=self._extract_degree_type(name),
                application_deadline=deadline,
                program_url=program_url,
                data_source=base_url,
            )
        except Exception as e:
            logger.debug(f"[CUHK] Error parsing row: {e}")
            return None

    def _fallback_programs(self) -> List[ProgramInfo]:
        """Return fallback entry pointing to official page."""
        return [
            self.create_program(
                program_name="All Taught Postgraduate Programmes",
                program_name_cn="所有授课型研究生课程",
                program_url=self.config.programs_list_url,
                data_source=self.config.programs_list_url,
                remarks=(
                    "Auto-scraping was not successful. Please visit the official "
                    "CUHK Graduate School admissions page for the full programme list."
                ),
            )
        ]

    @staticmethod
    def _extract_degree_type(name: str) -> str:
        """Extract degree type from programme name."""
        name_upper = name.upper()
        for pattern, degree in [
            ("MBA", "MBA"), ("LLM", "LLM"), ("MED", "MEd"),
            ("MSC", "MSc"), ("MSW", "MSW"), ("MA ", "MA"),
            ("MASTER OF SCIENCE", "MSc"), ("MASTER OF ARTS", "MA"),
            ("MPHIL", "MPhil"),
        ]:
            if pattern in name_upper:
                return degree
        return "Master"
