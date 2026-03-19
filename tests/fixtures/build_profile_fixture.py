#!/usr/bin/env python3
"""Generate profile.pdf. Run: uv run python tests/fixtures/build_profile_fixture.py"""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

PROFILE_CV = """Jane Doe
jane.doe@example.com
+33 6 12 34 56 78
https://linkedin.com/in/janedoe
https://janedoe.dev
Paris, France

Summary
Senior software engineer focused on backend systems.

Experience
Senior Engineer at Acme Robotics Ltd
Jan 2020 - Present
Situation: Legacy monolith blocked releases.
Task: Lead migration to microservices.
Action: Designed APIs using Python and trained team.
Result: Faster deployments across org.
Maintained Docker and MongoDB.

Developer at Beta Corp
Mar 2017 - Dec 2019
Maintained MySQL infrastructure and FastAPI services.

Education
ENS Paris, MSc Computer Science
2015 - 2017

Skills
Hard Skills
Python, FastAPI, Docker, MongoDB
Soft Skills
Leadership, Communication

Languages
English - Native
French: Professional

Certifications
AWS Solutions Architect - Amazon
"""


def main() -> None:
    root = Path(__file__).resolve().parent
    pdf_path = root / "profile.pdf"
    pdf = FPDF()
    pdf.set_margins(left=12, top=12, right=12)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    usable_w = pdf.w - pdf.l_margin - pdf.r_margin
    for line in PROFILE_CV.split("\n"):
        pdf.multi_cell(usable_w, 5, line, new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(pdf_path))


if __name__ == "__main__":
    main()
