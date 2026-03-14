"""
Scraper for The University of Hong Kong (HKU) master's programs.

Official source: https://admissions.hku.hk/tpg/programme-list
"""

import logging
import re
from typing import List, Optional
from urllib.parse import urljoin

from hk_admissions.models import ProgramInfo, HK_UNIVERSITIES
from hk_admissions.universities.base import BaseUniversityScraper

logger = logging.getLogger(__name__)


class HKUScraper(BaseUniversityScraper):
    """Scraper for HKU taught postgraduate programmes."""

    def __init__(self):
        super().__init__(HK_UNIVERSITIES["hku"])

    def scrape_programs(self) -> List[ProgramInfo]:
        """
        Scrape HKU's taught postgraduate programme list from the official
        admissions page.

        Official URL: https://admissions.hku.hk/tpg/programme-list
        """
        programs = []
        base_url = self.config.programs_list_url

        soup = self.fetch_page(base_url)
        if not soup:
            logger.error("[HKU] Failed to fetch programme list page")
            return programs

        # HKU's programme list is typically organized by faculty
        # Look for programme links/cards on the page
        programme_sections = soup.select(
            ".programme-item, .views-row, .program-card, "
            "table.views-table tbody tr, .field-content a, "
            ".view-content .views-row"
        )

        if not programme_sections:
            # Fallback: try to find all links that look like programme pages
            programme_sections = soup.find_all(
                "a", href=re.compile(r"/tpg/programme/|/programme/")
            )

        for item in programme_sections:
            program = self._parse_programme_item(item, base_url)
            if program:
                programs.append(program)

        # If direct scraping doesn't yield results, try the API approach
        if not programs:
            logger.info("[HKU] Trying alternative scraping approach...")
            programs = self._scrape_from_faculty_pages()

        if not programs:
            logger.warning(
                "[HKU] Could not scrape programmes automatically. "
                "Please visit the official page manually: %s",
                base_url,
            )
            # Return a placeholder entry pointing to the official page
            programs.append(
                self.create_program(
                    program_name="All Taught Postgraduate Programmes",
                    program_name_cn="所有授课型研究生课程",
                    program_url=base_url,
                    data_source=base_url,
                    remarks=(
                        "Auto-scraping was not successful. Please visit the official "
                        "HKU admissions page for the full programme list."
                    ),
                )
            )

        return programs

    def _parse_programme_item(self, item, base_url: str) -> Optional[ProgramInfo]:
        """Parse a single programme item from the list page."""
        try:
            # Try to extract link and text
            if item.name == "a":
                link = item
            else:
                link = item.find("a")

            if not link:
                return None

            href = link.get("href", "")
            if not href:
                return None

            program_url = urljoin(base_url, href)
            program_name = link.get_text(strip=True)

            if not program_name or len(program_name) < 3:
                return None

            # Try to determine degree type from name
            degree_type = self._extract_degree_type(program_name)

            # Try to find faculty info from parent elements
            faculty = ""
            parent = item.find_parent(class_=re.compile(r"faculty|school|department"))
            if parent:
                faculty_header = parent.find(
                    re.compile(r"h[2-4]"), class_=re.compile(r"faculty|title")
                )
                if faculty_header:
                    faculty = faculty_header.get_text(strip=True)

            program = self.create_program(
                program_name=program_name,
                degree_type=degree_type,
                faculty=faculty,
                program_url=program_url,
                data_source=base_url,
            )

            return program

        except Exception as e:
            logger.debug(f"[HKU] Error parsing programme item: {e}")
            return None

    def _scrape_from_faculty_pages(self) -> List[ProgramInfo]:
        """Alternative approach: scrape from individual faculty pages."""
        programs = []

        # HKU faculties with known graduate programme pages
        faculty_urls = {
            "Faculty of Architecture": "https://www.arch.hku.hk/programmes/postgraduate/",
            "Faculty of Arts": "https://www.arts.hku.hk/taught-postgraduate",
            "Faculty of Business and Economics": "https://www.hkubs.hku.hk/programmes/",
            "Faculty of Dentistry": "https://facdent.hku.hk/postgraduate/",
            "Faculty of Education": "https://web.edu.hku.hk/programme",
            "Faculty of Engineering": "https://engg.hku.hk/Teaching-and-Learning/Taught-Postgraduate-Programmes",
            "Faculty of Law": "https://www.law.hku.hk/postgraduate/",
            "Li Ka Shing Faculty of Medicine": "https://www.med.hku.hk/en/teaching-and-learning/postgraduate",
            "Faculty of Science": "https://www.scifac.hku.hk/postgraduate",
            "Faculty of Social Sciences": "https://www.socsc.hku.hk/postgraduate/",
        }

        for faculty_name, url in faculty_urls.items():
            soup = self.fetch_page(url)
            if not soup:
                continue

            # Find programme links
            links = soup.find_all(
                "a",
                href=re.compile(
                    r"(master|msc|ma|med|mba|llm|march|mphil|postgrad)", re.I
                ),
            )

            for link in links:
                name = link.get_text(strip=True)
                href = link.get("href", "")
                if name and href and len(name) > 5:
                    program_url = urljoin(url, href)
                    programs.append(
                        self.create_program(
                            program_name=name,
                            faculty=faculty_name,
                            degree_type=self._extract_degree_type(name),
                            program_url=program_url,
                            data_source=url,
                        )
                    )

        return programs

    @staticmethod
    def _extract_degree_type(name: str) -> str:
        """Extract degree type from programme name."""
        name_upper = name.upper()
        degree_patterns = [
            ("MBA", "MBA"),
            ("EMBA", "EMBA"),
            ("LLM", "LLM"),
            ("MARCH", "MArch"),
            ("MED", "MEd"),
            ("MSC", "MSc"),
            ("MSW", "MSW"),
            ("MFA", "MFA"),
            ("MA ", "MA"),
            ("MASTER OF ARTS", "MA"),
            ("MASTER OF SCIENCE", "MSc"),
            ("MASTER OF", "Master"),
            ("MPHIL", "MPhil"),
        ]
        for pattern, degree in degree_patterns:
            if pattern in name_upper:
                return degree
        return "Master"
