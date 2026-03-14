"""
PDF exporter for Hong Kong university admission data.

Exports programme data to .pdf format using fpdf2.
"""

import logging
from pathlib import Path
from typing import List

from fpdf import FPDF

from hk_admissions.models import ProgramInfo

logger = logging.getLogger(__name__)


class AdmissionsPDF(FPDF):
    """Custom PDF class with header and footer."""

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(47, 84, 150)
        self.cell(0, 8, "Hong Kong Universities Master's Admissions", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(47, 84, 150)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


class PDFExporter:
    """Export admission data to PDF format."""

    def export(
        self,
        programs: List[ProgramInfo],
        output_dir: str,
        filename_prefix: str = "hk_master_admissions",
    ) -> str:
        """
        Export programs to a PDF file.

        Args:
            programs: List of ProgramInfo objects.
            output_dir: Directory to save the file.
            filename_prefix: Filename prefix.

        Returns:
            Path to the created PDF file.
        """
        pdf = AdmissionsPDF(orientation="L", format="A4")
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin=20)

        # ---- Title Page ----
        pdf.add_page()
        pdf.ln(40)
        pdf.set_font("Helvetica", "B", 28)
        pdf.set_text_color(47, 84, 150)
        pdf.cell(
            0, 15,
            "Hong Kong Universities",
            align="C", new_x="LMARGIN", new_y="NEXT",
        )
        pdf.cell(
            0, 15,
            "Master's Programme Admissions",
            align="C", new_x="LMARGIN", new_y="NEXT",
        )
        pdf.ln(10)
        pdf.set_font("Helvetica", "", 14)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(
            0, 10,
            "Comprehensive Guide to Postgraduate Admissions",
            align="C", new_x="LMARGIN", new_y="NEXT",
        )
        pdf.ln(30)
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(
            0, 8,
            "All information sourced from official university websites",
            align="C", new_x="LMARGIN", new_y="NEXT",
        )

        # ---- Summary Page ----
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(47, 84, 150)
        pdf.cell(0, 10, "Summary", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Summary table
        uni_counts = {}
        for p in programs:
            key = p.university_name
            if key not in uni_counts:
                uni_counts[key] = {"count": 0, "abbr": p.university_abbreviation}
            uni_counts[key]["count"] += 1

        col_widths = [120, 30, 30]
        headers = ["University", "Abbr.", "Programs"]

        # Header
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(47, 84, 150)
        pdf.set_text_color(255, 255, 255)
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, border=1, fill=True, align="C")
        pdf.ln()

        # Data rows
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(0, 0, 0)
        fill = False
        for name, data in sorted(uni_counts.items()):
            if fill:
                pdf.set_fill_color(240, 245, 255)
            else:
                pdf.set_fill_color(255, 255, 255)
            pdf.cell(col_widths[0], 7, name, border=1, fill=True)
            pdf.cell(col_widths[1], 7, data["abbr"], border=1, fill=True, align="C")
            pdf.cell(col_widths[2], 7, str(data["count"]), border=1, fill=True, align="C")
            pdf.ln()
            fill = not fill

        # Total row
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(col_widths[0] + col_widths[1], 8, "TOTAL", border=1, align="R")
        pdf.cell(col_widths[2], 8, str(len(programs)), border=1, align="C")
        pdf.ln()

        # ---- Per-university sections ----
        universities = {}
        for p in programs:
            key = p.university_name
            if key not in universities:
                universities[key] = []
            universities[key].append(p)

        for uni_name, uni_programs in sorted(universities.items()):
            pdf.add_page()
            abbr = uni_programs[0].university_abbreviation if uni_programs else ""

            # University heading
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(47, 84, 150)
            pdf.cell(0, 12, f"{uni_name} ({abbr})", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)

            # Programme table
            prog_cols = [8, 80, 25, 35, 35, 40, 50]
            prog_headers = ["#", "Programme", "Degree", "Tuition", "Deadline", "English Req.", "URL"]

            pdf.set_font("Helvetica", "B", 8)
            pdf.set_fill_color(47, 84, 150)
            pdf.set_text_color(255, 255, 255)
            for i, header in enumerate(prog_headers):
                pdf.cell(prog_cols[i], 7, header, border=1, fill=True, align="C")
            pdf.ln()

            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(0, 0, 0)
            fill = False

            for idx, program in enumerate(uni_programs, 1):
                if fill:
                    pdf.set_fill_color(240, 245, 255)
                else:
                    pdf.set_fill_color(255, 255, 255)

                row_data = [
                    str(idx),
                    program.program_name[:45],
                    program.degree_type,
                    (program.tuition_fee or "See website")[:20],
                    (program.application_deadline or "See website")[:20],
                    (program.english_requirement or "See website")[:25],
                    (program.program_url or "")[:35],
                ]

                for i, value in enumerate(row_data):
                    pdf.cell(prog_cols[i], 6, value, border=1, fill=True)
                pdf.ln()
                fill = not fill

        # Disclaimer
        pdf.ln(10)
        pdf.set_font("Helvetica", "I", 7)
        pdf.set_text_color(150, 150, 150)
        pdf.multi_cell(
            0, 4,
            "Disclaimer: All information is collected from official university websites. "
            "Please verify with the respective university's official website for the most "
            "up-to-date information. This document is for reference purposes only.",
            align="C",
        )

        # Save
        filepath = str(Path(output_dir) / f"{filename_prefix}.pdf")
        pdf.output(filepath)
        logger.info(f"PDF file saved: {filepath}")
        return filepath
