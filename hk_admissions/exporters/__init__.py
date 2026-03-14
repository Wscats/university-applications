"""
Exporters package for outputting admission data in multiple formats.
"""

from hk_admissions.exporters.excel_exporter import ExcelExporter
from hk_admissions.exporters.word_exporter import WordExporter
from hk_admissions.exporters.pdf_exporter import PDFExporter
from hk_admissions.exporters.html_exporter import HTMLExporter
from hk_admissions.exporters.markdown_exporter import MarkdownExporter

from typing import List, Optional
from pathlib import Path

from hk_admissions.models import ProgramInfo


EXPORTER_MAP = {
    "excel": ExcelExporter,
    "word": WordExporter,
    "pdf": PDFExporter,
    "html": HTMLExporter,
    "markdown": MarkdownExporter,
}


def export_all(
    programs: List[ProgramInfo],
    output_dir: str = "./output",
    filename_prefix: str = "hk_master_admissions",
    formats: Optional[List[str]] = None,
) -> dict:
    """
    Export admission data to all (or specified) formats.

    Args:
        programs: List of ProgramInfo objects.
        output_dir: Output directory path.
        filename_prefix: Prefix for output filenames.
        formats: List of format names to export. None = all formats.

    Returns:
        Dictionary mapping format name to output file path.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if formats is None:
        formats = list(EXPORTER_MAP.keys())

    results = {}
    for fmt in formats:
        fmt_lower = fmt.lower().strip()
        if fmt_lower not in EXPORTER_MAP:
            print(f"Warning: Unknown format '{fmt}'. Skipping.")
            continue

        exporter_class = EXPORTER_MAP[fmt_lower]
        exporter = exporter_class()
        try:
            filepath = exporter.export(programs, str(output_path), filename_prefix)
            results[fmt_lower] = filepath
            print(f"✅ Exported {fmt_lower}: {filepath}")
        except Exception as e:
            print(f"❌ Failed to export {fmt_lower}: {e}")
            results[fmt_lower] = None

    return results


__all__ = [
    "ExcelExporter",
    "WordExporter",
    "PDFExporter",
    "HTMLExporter",
    "MarkdownExporter",
    "export_all",
    "EXPORTER_MAP",
]
