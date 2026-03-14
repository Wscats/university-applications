"""
Data models for Hong Kong university master's program admission information.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List
from datetime import date


@dataclass
class ProgramInfo:
    """Represents a single master's program admission information."""

    # University info
    university_name: str = ""
    university_name_cn: str = ""
    university_abbreviation: str = ""

    # Faculty / School
    faculty: str = ""
    faculty_cn: str = ""

    # Program info
    program_name: str = ""
    program_name_cn: str = ""
    degree_type: str = ""  # e.g., MSc, MA, MPhil, MBA, MEd, LLM, etc.

    # Tuition
    tuition_fee: str = ""  # e.g., "HKD 150,000" or "HKD 50,000 per year"
    tuition_currency: str = "HKD"
    tuition_remarks: str = ""

    # Application dates
    application_open_date: str = ""  # e.g., "2025-09-01" or "September 2025"
    application_deadline: str = ""  # e.g., "2026-04-30" or "April 30, 2026"
    application_deadline_remarks: str = ""  # e.g., "Early round: Jan 15; Main round: Apr 30"

    # English requirements
    english_requirement: str = ""  # e.g., "IELTS 6.5 (no sub-score below 5.5) or TOEFL iBT 80"
    english_requirement_details: str = ""

    # Program details
    duration: str = ""  # e.g., "1 year full-time", "2 years part-time"
    mode: str = ""  # "Full-time", "Part-time", "Full-time / Part-time"
    program_description: str = ""

    # Official link
    program_url: str = ""

    # Additional info
    remarks: str = ""
    data_source: str = ""  # The exact official URL where data was scraped from
    last_updated: str = ""  # When the data was last collected

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    def validate(self) -> List[str]:
        """Validate required fields. Returns list of missing field names."""
        required = ["university_name", "program_name", "program_url"]
        missing = [f for f in required if not getattr(self, f, "")]
        return missing


@dataclass
class UniversityConfig:
    """Configuration for a university scraper."""

    name: str = ""
    name_cn: str = ""
    abbreviation: str = ""
    base_url: str = ""
    admissions_url: str = ""
    graduate_school_url: str = ""
    programs_list_url: str = ""
    description: str = ""


# ============================================================
# Official Hong Kong University Configurations
# ============================================================

HK_UNIVERSITIES = {
    "hku": UniversityConfig(
        name="The University of Hong Kong",
        name_cn="香港大学",
        abbreviation="HKU",
        base_url="https://www.hku.hk",
        admissions_url="https://admissions.hku.hk/tpg",
        graduate_school_url="https://www.gradsch.hku.hk",
        programs_list_url="https://admissions.hku.hk/tpg/programme-list",
        description="Founded in 1911, HKU is the oldest tertiary institution in Hong Kong.",
    ),
    "cuhk": UniversityConfig(
        name="The Chinese University of Hong Kong",
        name_cn="香港中文大学",
        abbreviation="CUHK",
        base_url="https://www.cuhk.edu.hk",
        admissions_url="https://admissions.gs.cuhk.edu.hk",
        graduate_school_url="https://www.gs.cuhk.edu.hk",
        programs_list_url="https://admissions.gs.cuhk.edu.hk/admissions/programme-list",
        description="Founded in 1963, CUHK is a comprehensive research university.",
    ),
    "hkust": UniversityConfig(
        name="The Hong Kong University of Science and Technology",
        name_cn="香港科技大学",
        abbreviation="HKUST",
        base_url="https://www.hkust.edu.hk",
        admissions_url="https://pg.ust.hk/prospective-students/admissions",
        graduate_school_url="https://pg.ust.hk",
        programs_list_url="https://pg.ust.hk/prospective-students/admissions/program-list",
        description="Founded in 1991, HKUST is a world-class research university.",
    ),
    "polyu": UniversityConfig(
        name="The Hong Kong Polytechnic University",
        name_cn="香港理工大学",
        abbreviation="PolyU",
        base_url="https://www.polyu.edu.hk",
        admissions_url="https://www.polyu.edu.hk/study/pg",
        graduate_school_url="https://www.polyu.edu.hk/gs/",
        programs_list_url="https://www.polyu.edu.hk/study/pg/taught-postgraduate-programmes",
        description="Founded in 1937, PolyU is known for applied research and professional education.",
    ),
    "cityu": UniversityConfig(
        name="City University of Hong Kong",
        name_cn="香港城市大学",
        abbreviation="CityU",
        base_url="https://www.cityu.edu.hk",
        admissions_url="https://www.admo.cityu.edu.hk/tpg/",
        graduate_school_url="https://www.sgs.cityu.edu.hk",
        programs_list_url="https://www.admo.cityu.edu.hk/tpg/programmes",
        description="Founded in 1984, CityU is a dynamic university in the heart of Hong Kong.",
    ),
    "hkbu": UniversityConfig(
        name="Hong Kong Baptist University",
        name_cn="香港浸会大学",
        abbreviation="HKBU",
        base_url="https://www.hkbu.edu.hk",
        admissions_url="https://gs.hkbu.edu.hk/admission",
        graduate_school_url="https://gs.hkbu.edu.hk",
        programs_list_url="https://gs.hkbu.edu.hk/admission/taught-postgraduate-programmes",
        description="Founded in 1956, HKBU is a leading liberal arts university.",
    ),
    "eduhk": UniversityConfig(
        name="The Education University of Hong Kong",
        name_cn="香港教育大学",
        abbreviation="EdUHK",
        base_url="https://www.eduhk.hk",
        admissions_url="https://www.eduhk.hk/acadprog/postgrad.html",
        graduate_school_url="https://www.eduhk.hk/gradsch/",
        programs_list_url="https://www.eduhk.hk/acadprog/postgrad.html",
        description="EdUHK is a publicly funded university dedicated to education and social sciences.",
    ),
    "lingnan": UniversityConfig(
        name="Lingnan University",
        name_cn="岭南大学",
        abbreviation="LU",
        base_url="https://www.ln.edu.hk",
        admissions_url="https://www.ln.edu.hk/admissions/postgraduate",
        graduate_school_url="https://www.ln.edu.hk/sgs/",
        programs_list_url="https://www.ln.edu.hk/admissions/postgraduate/taught-postgraduate-programmes",
        description="Founded in 1888, Lingnan is the liberal arts university in Hong Kong.",
    ),
    "hkmu": UniversityConfig(
        name="Hong Kong Metropolitan University",
        name_cn="香港都会大学",
        abbreviation="HKMU",
        base_url="https://www.hkmu.edu.hk",
        admissions_url="https://admissions.hkmu.edu.hk/pg/",
        graduate_school_url="https://www.hkmu.edu.hk",
        programs_list_url="https://admissions.hkmu.edu.hk/pg/programmes/",
        description="HKMU (formerly OUHK) is a self-financing university offering diverse programmes.",
    ),
}
