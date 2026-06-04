#!/usr/bin/env python3
"""
AI Legal Assistant — Review Markdown to PDF JSON Extractor

Parses a CONTRACT-REVIEW-*.md file and extracts structured data
for use with generate_legal_pdf.py.

Usage:
    python3 extract_review_json.py <review.md> [output.json]
    python3 extract_review_json.py <review.md> | python3 generate_legal_pdf.py /dev/stdin output.pdf
"""

import sys
import re
import json
from datetime import datetime
from pathlib import Path


def extract_score(text):
    """Pull safety score from 'Contract Safety Score: 72/100' line."""
    m = re.search(r'Contract Safety Score[:\s]+(\d+)\s*/\s*100', text, re.IGNORECASE)
    return int(m.group(1)) if m else 0


def extract_grade(text):
    """Pull grade letter and label."""
    m = re.search(r'Grade[:\s]+([A-F][+]?)\s*[—–-]\s*([^\n]+)', text, re.IGNORECASE)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    # Fallback: infer from score
    return "N/A", "Unknown"


def extract_executive_summary(text):
    """Extract executive summary paragraph."""
    m = re.search(
        r'##\s*Executive Summary\s*\n+(.*?)(?=\n##|\Z)',
        text, re.DOTALL | re.IGNORECASE
    )
    if m:
        summary = m.group(1).strip()
        # Remove markdown comment blocks
        summary = re.sub(r'<!--.*?-->', '', summary, flags=re.DOTALL).strip()
        # Remove bracketed placeholder text
        summary = re.sub(r'\[.*?\]', '', summary).strip()
        return summary if summary else "See full report for details."
    return "See full report for details."


def extract_contract_details(text):
    """Extract contract metadata table."""
    details = {}
    field_map = {
        'contract type': 'type',
        'parties': 'parties',
        'effective date': 'effective_date',
        'term': 'term',
        'total value': 'total_value',
        'governing law': 'governing_law',
    }
    for label, key in field_map.items():
        pattern = rf'\|\s*\*{{0,2}}{re.escape(label)}\*{{0,2}}\s*\|\s*([^|\n]+)\s*\|'
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            value = m.group(1).strip()
            value = re.sub(r'\[.*?\]', '', value).strip()
            details[key] = value if value else 'N/A'
        else:
            details[key] = 'N/A'
    return details


def extract_risk_counts(text):
    """Extract high/medium/low risk counts from Risk Dashboard table."""
    risks = {'high': 0, 'medium': 0, 'low': 0,
             'high_clauses': 'None', 'medium_clauses': 'None', 'low_clauses': 'None'}

    patterns = [
        (r'High Risk\s*\|\s*(\d+)\s*\|\s*([^|\n]*)', 'high', 'high_clauses'),
        (r'Medium Risk\s*\|\s*(\d+)\s*\|\s*([^|\n]*)', 'medium', 'medium_clauses'),
        (r'Low Risk\s*\|\s*(\d+)\s*\|\s*([^|\n]*)', 'low', 'low_clauses'),
    ]
    for pattern, count_key, clauses_key in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            risks[count_key] = int(m.group(1))
            clauses = m.group(2).strip().rstrip('|').strip()
            risks[clauses_key] = clauses if clauses and clauses != '—' else 'None'

    return risks


def extract_clauses(text):
    """Extract clause-by-clause analysis blocks."""
    clauses = []

    # Match HIGH/MEDIUM/LOW sections
    sections = re.split(r'###\s*(🔴\s*HIGH RISK|🟡\s*MEDIUM RISK|🟢\s*LOW RISK)', text, flags=re.IGNORECASE)

    risk_level = None
    for i, chunk in enumerate(sections):
        chunk = chunk.strip()
        if re.match(r'🔴|HIGH RISK', chunk, re.IGNORECASE):
            risk_level = 'high'
            continue
        elif re.match(r'🟡|MEDIUM RISK', chunk, re.IGNORECASE):
            risk_level = 'medium'
            continue
        elif re.match(r'🟢|LOW RISK', chunk, re.IGNORECASE):
            risk_level = 'low'
            continue

        if risk_level is None:
            continue

        # Extract individual clause blocks: #### Clause Name — Section X.X
        clause_blocks = re.split(r'####\s+', chunk)
        for block in clause_blocks:
            block = block.strip()
            if not block:
                continue

            # First line = "Clause Name — Section X.X"
            first_line = block.split('\n')[0].strip()
            name_match = re.match(r'(.+?)\s*[—–-]\s*Section\s*([\d.]+)', first_line)
            name = name_match.group(1).strip() if name_match else first_line
            section = name_match.group(2).strip() if name_match else 'N/A'

            def get_field(field_name, block_text):
                m = re.search(
                    rf'\*\*{re.escape(field_name)}[:\*]*\*?\s*(.*?)(?=\n\s*-\s*\*\*|\n##|\Z)',
                    block_text, re.DOTALL | re.IGNORECASE
                )
                if m:
                    val = m.group(1).strip()
                    return re.sub(r'\[.*?\]', '', val).strip()
                return ''

            summary = get_field("What it says", block)
            risk_explanation = get_field("Why it's risky", block) or get_field("Why it matters", block)
            recommendation = get_field("Recommended change", block)

            if name and (summary or risk_explanation):
                clauses.append({
                    'risk': risk_level,
                    'name': name,
                    'section': section,
                    'summary': summary[:400] if summary else '',
                    'risk_explanation': risk_explanation[:400] if risk_explanation else '',
                    'recommendation': recommendation[:400] if recommendation else '',
                })

    return clauses


def extract_negotiation_priorities(text):
    """Extract ranked negotiation priorities."""
    m = re.search(
        r'##\s*Negotiation Priorities\s*\n+(.*?)(?=\n##|\Z)',
        text, re.DOTALL | re.IGNORECASE
    )
    if not m:
        return []

    block = m.group(1).strip()
    items = re.findall(r'^\d+\.\s+(.+)', block, re.MULTILINE)
    cleaned = []
    for item in items:
        item = re.sub(r'\[.*?\]', '', item).strip()
        item = re.sub(r'\*\*', '', item).strip()
        if item:
            cleaned.append(item[:300])
    return cleaned[:7]


def extract_missing_protections(text):
    """Extract missing protections list."""
    m = re.search(
        r'##\s*Missing Protections\s*\n+(.*?)(?=\n##|\Z)',
        text, re.DOTALL | re.IGNORECASE
    )
    if not m:
        return []

    block = m.group(1).strip()
    # Try table format first
    rows = re.findall(r'\|\s*\d+\s*\|\s*([^|]+)\|', block)
    if rows:
        return [re.sub(r'\[.*?\]', '', r).strip() for r in rows if r.strip()]

    # Fallback: bullet list
    items = re.findall(r'^[-*]\s+(.+)', block, re.MULTILINE)
    return [re.sub(r'\[.*?\]', '', i).strip() for i in items if i.strip()][:8]


def extract_next_steps(text):
    """Extract recommended next steps."""
    m = re.search(
        r'##\s*Recommended Next Steps\s*\n+(.*?)(?=\n##|\Z)',
        text, re.DOTALL | re.IGNORECASE
    )
    if not m:
        return []

    block = m.group(1).strip()
    items = re.findall(r'^\d+\.\s+\[?\s*[x ]?\s*\]?\s*(.+)', block, re.MULTILINE)
    cleaned = [re.sub(r'\[.*?\]', '', i).strip() for i in items if i.strip()]
    return cleaned[:8]


def parse_review(md_text):
    """Parse a CONTRACT-REVIEW-*.md into a PDF data dict."""
    score = extract_score(md_text)
    grade, grade_label = extract_grade(md_text)

    # Infer grade from score if not found in text
    if grade == 'N/A':
        if score >= 90:
            grade, grade_label = 'A+', 'Safe'
        elif score >= 80:
            grade, grade_label = 'A', 'Good'
        elif score >= 70:
            grade, grade_label = 'B', 'Fair'
        elif score >= 60:
            grade, grade_label = 'C', 'Caution'
        elif score >= 40:
            grade, grade_label = 'D', 'Risky'
        else:
            grade, grade_label = 'F', 'Dangerous'

    return {
        'score': score,
        'grade': grade,
        'grade_label': grade_label,
        'executive_summary': extract_executive_summary(md_text),
        'details': extract_contract_details(md_text),
        'risks': extract_risk_counts(md_text),
        'clauses': extract_clauses(md_text),
        'negotiation_priorities': extract_negotiation_priorities(md_text),
        'missing_protections': extract_missing_protections(md_text),
        'next_steps': extract_next_steps(md_text),
        'generated_date': datetime.now().strftime('%Y-%m-%d'),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_review_json.py <review.md> [output.json]")
        print()
        print("Examples:")
        print("  python3 extract_review_json.py CONTRACT-REVIEW-2024-01-15.md")
        print("  python3 extract_review_json.py CONTRACT-REVIEW-2024-01-15.md data.json")
        sys.exit(1)

    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print(f"ERROR: File not found: {md_path}")
        sys.exit(1)

    md_text = md_path.read_text(encoding='utf-8')
    data = parse_review(md_text)

    if len(sys.argv) >= 3:
        out_path = Path(sys.argv[2])
        out_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
        print(f"JSON written: {out_path}")
        print(f"Score: {data['score']}/100  Grade: {data['grade']} ({data['grade_label']})")
        print(f"Clauses parsed: {len(data['clauses'])}")
        print(f"Risks — High: {data['risks']['high']}  Med: {data['risks']['medium']}  Low: {data['risks']['low']}")
    else:
        print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
