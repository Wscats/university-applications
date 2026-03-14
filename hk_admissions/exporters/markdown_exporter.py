"""
Markdown exporter for Hong Kong university admission data.

Exports programme data to .md format.
"""

import logging
from pathlib import Path
from typing import List
from datetime import datetime

from hk_admissions.models import ProgramInfo

logger = logging.getLogger(__name__)


class MarkdownExporter:
    """Export admission data to Markdown (.md) format."""

    def export(
        self,
        programs: List[ProgramInfo],
        output_dir: str,
        filename_prefix: str = "hk_master_admissions",
    ) -> str:
        """
        Export programs to a Markdown file.

        Args:
            programs: List of ProgramInfo objects.
            output_dir: Directory to save the file.
            filename_prefix: Filename prefix.

        Returns:
            Path to the created Markdown file.
        """
        lines = []

        # Title
        lines.append("# 🎓 Hong Kong Universities Master's Programme Admissions")
        lines.append("")
        lines.append("**香港各大学硕士研究生招生信息汇总**")
        lines.append("")
        lines.append(f"> Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
                      f"All data from official university websites")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Table of Contents
        lines.append("## 📋 Table of Contents")
        lines.append("")

        universities = {}
        for p in programs:
            key = p.university_name
            if key not in universities:
                universities[key] = []
            universities[key].append(p)

        lines.append("- [Summary](#summary)")
        for uni_name in sorted(universities.keys()):
            anchor = uni_name.lower().replace(" ", "-").replace("(", "").replace(")", "")
            abbr = universities[uni_name][0].university_abbreviation if universities[uni_name] else ""
            lines.append(f"- [{uni_name} ({abbr})](#{anchor})")
        lines.append("")

        # Summary
        lines.append("## 📊 Summary")
        lines.append("")
        lines.append("| University | Chinese Name | Abbr. | Programmes |")
        lines.append("|:-----------|:------------|:-----:|:----------:|")

        for uni_name, uni_programs in sorted(universities.items()):
            cn = uni_programs[0].university_name_cn if uni_programs else ""
            abbr = uni_programs[0].university_abbreviation if uni_programs else ""
            lines.append(f"| {uni_name} | {cn} | {abbr} | {len(uni_programs)} |")

        lines.append(f"| **TOTAL** | | | **{len(programs)}** |")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Per-university sections
        for uni_name, uni_programs in sorted(universities.items()):
            cn = uni_programs[0].university_name_cn if uni_programs else ""
            abbr = uni_programs[0].university_abbreviation if uni_programs else ""

            lines.append(f"## {uni_name} ({abbr})")
            if cn:
                lines.append(f"**{cn}**")
            lines.append("")

            # Programme table
            lines.append("| # | Programme | Degree | Faculty | Tuition | Deadline | English Req. | Duration | Link |")
            lines.append("|:-:|:----------|:------:|:--------|:--------|:---------|:-------------|:---------|:-----|")

            for idx, p in enumerate(uni_programs, 1):
                name = p.program_name.replace("|", "\\|")
                faculty = (p.faculty or "-").replace("|", "\\|")
                tuition = (p.tuition_fee or "See website").replace("|", "\\|")
                deadline = (p.application_deadline or "See website").replace("|", "\\|")
                english = (p.english_requirement or "See website").replace("|", "\\|")
                duration = (p.duration or "-").replace("|", "\\|")
                degree = (p.degree_type or "Master").replace("|", "\\|")

                if p.program_url:
                    link = f"[Official]({p.program_url})"
                else:
                    link = "-"

                lines.append(
                    f"| {idx} | {name} | {degree} | {faculty} | "
                    f"{tuition} | {deadline} | {english} | {duration} | {link} |"
                )

            lines.append("")

            # Detailed entries (expandable)
            lines.append("<details>")
            lines.append(f"<summary>📖 Detailed View ({len(uni_programs)} programmes)</summary>")
            lines.append("")

            for idx, p in enumerate(uni_programs, 1):
                lines.append(f"### {idx}. {p.program_name}")
                if p.program_name_cn:
                    lines.append(f"**{p.program_name_cn}**")
                lines.append("")

                details = [
                    ("🎓 Degree Type", p.degree_type),
                    ("🏛️ Faculty", p.faculty),
                    ("💰 Tuition Fee", p.tuition_fee or "Please refer to official website"),
                    ("📅 Application Open", p.application_open_date or "Please refer to official website"),
                    ("⏰ Application Deadline", p.application_deadline or "Please refer to official website"),
                    ("📝 Deadline Remarks", p.application_deadline_remarks),
                    ("🌐 English Requirement", p.english_requirement or "Please refer to official website"),
                    ("⏱️ Duration", p.duration or "Please refer to official website"),
                    ("📋 Mode", p.mode),
                    ("🔗 Official URL", f"[{p.program_url}]({p.program_url})" if p.program_url else ""),
                    ("💬 Remarks", p.remarks),
                ]

                for label, value in details:
                    if value:
                        lines.append(f"- **{label}**: {value}")

                lines.append("")

            lines.append("</details>")
            lines.append("")
            lines.append("---")
            lines.append("")

        # Disclaimer
        lines.append("## ⚠️ Disclaimer")
        lines.append("")
        lines.append(
            "> All information is collected from official university websites. "
            "Please verify with the respective university's official website for the most "
            "up-to-date information. This document is for reference purposes only."
        )
        lines.append("")
        lines.append(f"*© {datetime.now().year} HK Admissions Collector*")

        # Write file
        content = "\n".join(lines)
        filepath = str(Path(output_dir) / f"{filename_prefix}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Markdown file saved: {filepath}")
        return filepath
