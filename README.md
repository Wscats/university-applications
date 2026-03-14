# Hong Kong Universities Master's Admission Information Collector

A comprehensive skill/tool for collecting official master's program admission information from all Hong Kong universities and exporting to multiple formats (Excel, Word, PDF, HTML, Markdown).

## Features

- Collects admission info from **all Hong Kong universities** official websites
- Information includes: tuition fees, application dates, deadlines, English requirements, program details, official links
- Exports to **5 formats**: Excel (.xlsx), Word (.docx), PDF (.pdf), HTML (.html), Markdown (.md)
- Modular and extensible architecture
- Built-in data validation

## Hong Kong Universities Covered

1. The University of Hong Kong (HKU)
2. The Chinese University of Hong Kong (CUHK)
3. The Hong Kong University of Science and Technology (HKUST)
4. The Hong Kong Polytechnic University (PolyU)
5. City University of Hong Kong (CityU)
6. Hong Kong Baptist University (HKBU)
7. The Education University of Hong Kong (EdUHK)
8. Lingnan University (LU)
9. Hong Kong Metropolitan University (HKMU)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Collect all universities and export all formats
python -m hk_admissions.main --output-dir ./output --formats all

# Collect specific university
python -m hk_admissions.main --university hku --formats excel,markdown

# List all supported universities
python -m hk_admissions.main --list-universities
```

### Python API

```python
from hk_admissions.collector import HKAdmissionsCollector
from hk_admissions.exporters import export_all

# Initialize collector
collector = HKAdmissionsCollector()

# Collect all universities' data
programs = collector.collect_all()

# Export to all formats
export_all(programs, output_dir="./output")
```

## Project Structure

```
hk_admissions/
├── __init__.py
├── main.py                 # CLI entry point
├── collector.py            # Main collector orchestrator
├── models.py               # Data models
├── universities/           # Per-university scrapers
│   ├── __init__.py
│   ├── base.py             # Base scraper class
│   ├── hku.py
│   ├── cuhk.py
│   ├── hkust.py
│   ├── polyu.py
│   ├── cityu.py
│   ├── hkbu.py
│   ├── eduhk.py
│   ├── lingnan.py
│   └── hkmu.py
├── exporters/              # Output format exporters
│   ├── __init__.py
│   ├── excel_exporter.py
│   ├── word_exporter.py
│   ├── pdf_exporter.py
│   ├── html_exporter.py
│   └── markdown_exporter.py
└── templates/
    └── report.html         # HTML template
```

## Data Fields

| Field | Description |
|-------|-------------|
| university_name | Name of the university |
| university_name_cn | Chinese name |
| faculty | Faculty/School name |
| program_name | Program name |
| program_name_cn | Chinese program name |
| degree_type | e.g., MSc, MA, MPhil |
| tuition_fee | Tuition fee amount |
| tuition_currency | Currency (HKD) |
| application_open_date | Application opening date |
| application_deadline | Application deadline |
| english_requirement | English language requirements (IELTS/TOEFL) |
| program_url | Official program page URL |
| duration | Program duration |
| mode | Full-time / Part-time |
| remarks | Additional notes |

## Disclaimer

All information is collected from official university websites. Please verify with the respective university's official website for the most up-to-date information. This tool is for reference purposes only.
