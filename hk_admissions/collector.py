"""
Main collector orchestrator for Hong Kong university admissions data.

Coordinates all university scrapers and manages the data collection pipeline.
"""

import logging
from typing import List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from hk_admissions.models import ProgramInfo, HK_UNIVERSITIES
from hk_admissions.universities import SCRAPER_REGISTRY

logger = logging.getLogger(__name__)


class HKAdmissionsCollector:
    """
    Main collector that orchestrates scraping across all Hong Kong universities.

    Usage:
        collector = HKAdmissionsCollector()
        programs = collector.collect_all()
    """

    def __init__(self, max_workers: int = 3):
        """
        Initialize the collector.

        Args:
            max_workers: Maximum number of concurrent scraper threads.
        """
        self.max_workers = max_workers
        self._programs: List[ProgramInfo] = []

    @property
    def supported_universities(self) -> Dict[str, str]:
        """Get dict of supported university keys to names."""
        return {
            key: config.name
            for key, config in HK_UNIVERSITIES.items()
        }

    def collect_all(self) -> List[ProgramInfo]:
        """
        Collect admission data from all supported Hong Kong universities.

        Returns:
            List of ProgramInfo objects from all universities.
        """
        logger.info("Starting collection from all Hong Kong universities...")
        all_programs = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for uni_key, scraper_class in SCRAPER_REGISTRY.items():
                future = executor.submit(self._collect_single, uni_key, scraper_class)
                futures[future] = uni_key

            for future in as_completed(futures):
                uni_key = futures[future]
                try:
                    programs = future.result()
                    all_programs.extend(programs)
                    logger.info(
                        f"Completed {uni_key}: {len(programs)} programs collected"
                    )
                except Exception as e:
                    logger.error(f"Error collecting from {uni_key}: {e}")

        # Sort by university name then program name
        all_programs.sort(
            key=lambda p: (p.university_name, p.faculty, p.program_name)
        )

        self._programs = all_programs
        logger.info(f"Total: {len(all_programs)} programs collected from all universities")
        return all_programs

    def collect_university(self, university_key: str) -> List[ProgramInfo]:
        """
        Collect admission data from a specific university.

        Args:
            university_key: The university key (e.g., 'hku', 'cuhk').

        Returns:
            List of ProgramInfo objects.

        Raises:
            ValueError: If university_key is not supported.
        """
        university_key = university_key.lower().strip()

        if university_key not in SCRAPER_REGISTRY:
            available = ", ".join(SCRAPER_REGISTRY.keys())
            raise ValueError(
                f"Unknown university: '{university_key}'. "
                f"Available: {available}"
            )

        scraper_class = SCRAPER_REGISTRY[university_key]
        programs = self._collect_single(university_key, scraper_class)
        self._programs = programs
        return programs

    def collect_multiple(self, university_keys: List[str]) -> List[ProgramInfo]:
        """
        Collect admission data from multiple specified universities.

        Args:
            university_keys: List of university keys.

        Returns:
            Combined list of ProgramInfo objects.
        """
        all_programs = []
        for key in university_keys:
            programs = self.collect_university(key)
            all_programs.extend(programs)

        all_programs.sort(
            key=lambda p: (p.university_name, p.faculty, p.program_name)
        )
        self._programs = all_programs
        return all_programs

    @staticmethod
    def _collect_single(uni_key: str, scraper_class) -> List[ProgramInfo]:
        """Run a single university scraper."""
        try:
            with scraper_class() as scraper:
                return scraper.collect()
        except Exception as e:
            logger.error(f"Failed to collect from {uni_key}: {e}", exc_info=True)
            return []

    def get_summary(self) -> Dict:
        """
        Get a summary of collected data.

        Returns:
            Dictionary with summary statistics.
        """
        if not self._programs:
            return {"total_programs": 0, "universities": {}}

        uni_counts = {}
        for p in self._programs:
            name = p.university_name or "Unknown"
            uni_counts[name] = uni_counts.get(name, 0) + 1

        return {
            "total_programs": len(self._programs),
            "universities": uni_counts,
            "universities_count": len(uni_counts),
        }
