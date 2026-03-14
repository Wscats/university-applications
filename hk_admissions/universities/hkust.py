"""
Scraper for The Hong Kong University of Science and Technology (HKUST) master's programs.

Official source: https://pg.ust.hk/prospective-students/admissions/program-list
"""

import logging
import re
from typing import List, Optional
from urllib.parse import urljoin

from hk_admissions.models import ProgramInfo, HK_UNIVERSITIES
from hk_admissions.universities.base import BaseUniversityScraper

logger = logging.getLogger(__name__)


class HKUSTScraper(BaseUniversityScraper):
    """Scraper for HKUST postgraduate programmes."""

    def __init__(self):
        super().__init__(HK_UNIVERSITIES["hkust"])

    def scrape_programs(self) -> List[ProgramInfo]:
        """
        Scrape HKUST's postgraduate programme list.

        Official URL: https://pg.ust.hk/prospective-students/admissions/program-list
        """
        programs = []
        base_url = self.config.programs_list_url

        soup = self.fetch_page(base_url)
        if not soup:
            logger.error("[HKUST] Failed to fetch programme list page")
            return self._fallback_programs()

        # HKUST programme list page structure
        items = soup.select(
            ".program-item, .views-row, .programme-card, "
            "table tbody tr, .program-list-item, .field-content"
        )

        if not items:
            items = soup.find_all(
                "a", href=re.compile(r"programs?/|admissions?/", re.I)
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

            # Determine degree type
            degree_type = "Master"
            name_upper = name.upper()
            for pattern, dt in [
                ("MBA", "MBA"), ("MSC", "MSc"), ("MA ", "MA"),
                ("MPHIL", "MPhil"), ("MSCI", "MSc"),
            ]:
                if pattern in name_upper:
                    degree_type = dt
                    break

            return self.create_program(
                program_name=name,
                degree_type=degree_type,
                program_url=program_url,
                data_source=base_url,
            )
        except Exception as e:
            logger.debug(f"[HKUST] Error parsing item: {e}")
            return None

    def _fallback_programs(self) -> List[ProgramInfo]:
        """Return fallback entry."""
        return [
            self.create_program(
                program_name="All Postgraduate Programmes",
                program_name_cn="所有研究生课程",
                program_url=self.config.programs_list_url,
                data_source=self.config.programs_list_url,
                remarks=(
                    "Auto-scraping was not successful. Please visit the official "
                    "HKUST PG admissions page for the full programme list."
                ),
            )
        ]
