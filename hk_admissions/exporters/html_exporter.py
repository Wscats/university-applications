"""
HTML exporter for Hong Kong university admission data.

Exports programme data to a styled, responsive HTML page using Jinja2 templates.
"""

import logging
from pathlib import Path
from typing import List
from datetime import datetime

from jinja2 import Template

from hk_admissions.models import ProgramInfo

logger = logging.getLogger(__name__)

# Inline HTML template (self-contained, no external dependencies)
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hong Kong Universities Master's Admissions</title>
    <style>
        :root {
            --primary: #2f5496;
            --primary-light: #4472c4;
            --bg: #f5f7fa;
            --card-bg: #ffffff;
            --text: #333333;
            --text-light: #666666;
            --border: #e0e4e8;
            --success: #28a745;
            --warning: #ffc107;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        header {
            background: linear-gradient(135deg, var(--primary), var(--primary-light));
            color: white;
            padding: 40px 20px;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 12px;
        }
        header h1 { font-size: 2.2em; margin-bottom: 8px; }
        header p { font-size: 1.1em; opacity: 0.9; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: var(--card-bg);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 4px solid var(--primary);
        }
        .stat-card .number { font-size: 2em; font-weight: 700; color: var(--primary); }
        .stat-card .label { font-size: 0.9em; color: var(--text-light); }
        .search-bar {
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .search-bar input, .search-bar select {
            padding: 10px 16px;
            border: 2px solid var(--border);
            border-radius: 8px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }
        .search-bar input:focus, .search-bar select:focus {
            border-color: var(--primary);
        }
        .search-bar input { flex: 1; min-width: 300px; }
        .uni-section {
            background: var(--card-bg);
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            overflow: hidden;
        }
        .uni-header {
            background: var(--primary);
            color: white;
            padding: 18px 24px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .uni-header h2 { font-size: 1.3em; }
        .uni-header .badge {
            background: rgba(255,255,255,0.2);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
        }
        .uni-body { padding: 0; }
        .program-table {
            width: 100%;
            border-collapse: collapse;
        }
        .program-table th {
            background: #f0f4f8;
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--primary);
            border-bottom: 2px solid var(--border);
            position: sticky;
            top: 0;
        }
        .program-table td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            font-size: 0.9em;
            vertical-align: top;
        }
        .program-table tr:hover { background: #f8fafd; }
        .program-table tr:last-child td { border-bottom: none; }
        .program-table a {
            color: var(--primary-light);
            text-decoration: none;
        }
        .program-table a:hover { text-decoration: underline; }
        .tag {
            display: inline-block;
            background: #e8f0fe;
            color: var(--primary);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 500;
        }
        footer {
            text-align: center;
            padding: 30px;
            color: var(--text-light);
            font-size: 0.85em;
        }
        @media (max-width: 768px) {
            header h1 { font-size: 1.5em; }
            .program-table { font-size: 0.8em; }
            .program-table th, .program-table td { padding: 8px; }
        }
        .collapsible-content { display: block; }
        .collapsed .collapsible-content { display: none; }
        .toggle-icon { transition: transform 0.3s; }
        .collapsed .toggle-icon { transform: rotate(-90deg); }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎓 Hong Kong Universities Master's Admissions</h1>
            <p>香港各大学硕士研究生招生信息汇总</p>
            <p style="font-size: 0.85em; margin-top: 8px; opacity: 0.7;">
                Generated on {{ generated_date }} | All data from official university websites
            </p>
        </header>

        <div class="stats">
            <div class="stat-card">
                <div class="number">{{ total_programs }}</div>
                <div class="label">Total Programmes</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ universities|length }}</div>
                <div class="label">Universities</div>
            </div>
            {% for uni_name, data in universities.items() %}
            <div class="stat-card">
                <div class="number">{{ data.count }}</div>
                <div class="label">{{ data.abbr }}</div>
            </div>
            {% endfor %}
        </div>

        <div class="search-bar">
            <input type="text" id="searchInput" placeholder="🔍 Search programmes, universities, degree types...">
            <select id="uniFilter" onchange="filterByUni()">
                <option value="">All Universities</option>
                {% for uni_name in universities.keys() %}
                <option value="{{ uni_name }}">{{ uni_name }}</option>
                {% endfor %}
            </select>
        </div>

        {% for uni_name, uni_programs in grouped_programs.items() %}
        <div class="uni-section" data-university="{{ uni_name }}">
            <div class="uni-header" onclick="toggleSection(this)">
                <h2>
                    <span class="toggle-icon">▼</span>
                    {{ uni_name }}
                    {% if uni_programs and uni_programs[0].university_name_cn %}
                     ({{ uni_programs[0].university_name_cn }})
                    {% endif %}
                </h2>
                <span class="badge">{{ uni_programs|length }} programmes</span>
            </div>
            <div class="uni-body collapsible-content">
                <table class="program-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Programme</th>
                            <th>Degree</th>
                            <th>Faculty</th>
                            <th>Tuition</th>
                            <th>Deadline</th>
                            <th>English Req.</th>
                            <th>Duration</th>
                            <th>Link</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for p in uni_programs %}
                        <tr class="program-row">
                            <td>{{ loop.index }}</td>
                            <td>
                                <strong>{{ p.program_name }}</strong>
                                {% if p.program_name_cn %}<br><small>{{ p.program_name_cn }}</small>{% endif %}
                            </td>
                            <td><span class="tag">{{ p.degree_type or 'Master' }}</span></td>
                            <td>{{ p.faculty or '-' }}</td>
                            <td>{{ p.tuition_fee or 'See website' }}</td>
                            <td>
                                {{ p.application_deadline or 'See website' }}
                                {% if p.application_deadline_remarks %}
                                <br><small>{{ p.application_deadline_remarks }}</small>
                                {% endif %}
                            </td>
                            <td>{{ p.english_requirement or 'See website' }}</td>
                            <td>{{ p.duration or '-' }}</td>
                            <td>
                                {% if p.program_url %}
                                <a href="{{ p.program_url }}" target="_blank" rel="noopener">Official Page ↗</a>
                                {% else %}
                                -
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endfor %}

        <footer>
            <p><strong>Disclaimer:</strong> All information is collected from official university websites.
            Please verify with the respective university's official website for the most up-to-date information.</p>
            <p style="margin-top: 8px;">© {{ year }} HK Admissions Collector</p>
        </footer>
    </div>

    <script>
        // Search functionality
        document.getElementById('searchInput').addEventListener('input', function() {
            const query = this.value.toLowerCase();
            document.querySelectorAll('.program-row').forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
            // Show/hide university sections based on visible rows
            document.querySelectorAll('.uni-section').forEach(section => {
                const visibleRows = section.querySelectorAll('.program-row[style=""],.program-row:not([style])');
                let hasVisible = false;
                visibleRows.forEach(r => { if (r.style.display !== 'none') hasVisible = true; });
                section.style.display = hasVisible ? '' : 'none';
            });
        });

        // University filter
        function filterByUni() {
            const selected = document.getElementById('uniFilter').value;
            document.querySelectorAll('.uni-section').forEach(section => {
                if (!selected || section.dataset.university === selected) {
                    section.style.display = '';
                } else {
                    section.style.display = 'none';
                }
            });
        }

        // Toggle section
        function toggleSection(header) {
            header.parentElement.classList.toggle('collapsed');
        }
    </script>
</body>
</html>"""


class HTMLExporter:
    """Export admission data to a styled HTML page."""

    def export(
        self,
        programs: List[ProgramInfo],
        output_dir: str,
        filename_prefix: str = "hk_master_admissions",
    ) -> str:
        """
        Export programs to an HTML file.

        Args:
            programs: List of ProgramInfo objects.
            output_dir: Directory to save the file.
            filename_prefix: Filename prefix.

        Returns:
            Path to the created HTML file.
        """
        # Group by university
        grouped = {}
        uni_stats = {}
        for p in programs:
            name = p.university_name
            if name not in grouped:
                grouped[name] = []
                uni_stats[name] = {
                    "count": 0,
                    "abbr": p.university_abbreviation,
                    "cn": p.university_name_cn,
                }
            grouped[name].append(p)
            uni_stats[name]["count"] += 1

        # Render template
        template = Template(HTML_TEMPLATE)
        html_content = template.render(
            generated_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            total_programs=len(programs),
            universities=uni_stats,
            grouped_programs=dict(sorted(grouped.items())),
            year=datetime.now().year,
        )

        # Save
        filepath = str(Path(output_dir) / f"{filename_prefix}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"HTML file saved: {filepath}")
        return filepath
