"""
University scrapers package.
"""

from hk_admissions.universities.base import BaseUniversityScraper
from hk_admissions.universities.hku import HKUScraper
from hk_admissions.universities.cuhk import CUHKScraper
from hk_admissions.universities.hkust import HKUSTScraper
from hk_admissions.universities.polyu import PolyUScraper
from hk_admissions.universities.cityu import CityUScraper
from hk_admissions.universities.hkbu import HKBUScraper
from hk_admissions.universities.eduhk import EdUHKScraper
from hk_admissions.universities.lingnan import LingnanScraper
from hk_admissions.universities.hkmu import HKMUScraper

# Registry: university key -> scraper class
SCRAPER_REGISTRY = {
    "hku": HKUScraper,
    "cuhk": CUHKScraper,
    "hkust": HKUSTScraper,
    "polyu": PolyUScraper,
    "cityu": CityUScraper,
    "hkbu": HKBUScraper,
    "eduhk": EdUHKScraper,
    "lingnan": LingnanScraper,
    "hkmu": HKMUScraper,
}

__all__ = [
    "BaseUniversityScraper",
    "SCRAPER_REGISTRY",
    "HKUScraper",
    "CUHKScraper",
    "HKUSTScraper",
    "PolyUScraper",
    "CityUScraper",
    "HKBUScraper",
    "EdUHKScraper",
    "LingnanScraper",
    "HKMUScraper",
]
