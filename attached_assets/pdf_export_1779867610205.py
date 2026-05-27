"""
pdf_export.py — Export the generated study plan as a styled PDF using ReportLab.
"""

import io
from datetime import date


def generate_pdf(plan: list[dict], subject: str, exam_date) -> bytes:
    """
    Returns PDF bytes for the given plan.
    plan: list of day dicts from planner.py
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )

    # Colours
    PRIMARY     = colors.HexColor("#6C63FF")
    ACCENT      = colors.HexColor("#FF6584")
    STUDY_BG    = colors.HexColor("#EEF2FF")
    REVISION_BG = colors.HexColor("#FFF3E0")
    BUFFER_BG   = colors.HexColor("#E8F5E9")
    LIGHT_GRAY  = colors.HexColor("#F5F5F5")
    DARK        = colors.HexColor("#1E1E2E")

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title", parent=styles["Title"],
        fontSize=22, textColor=PRIMARY, spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    sub_style = ParagraphStyle(
        "Sub", parent=styles["Normal"],
        fontSize=11, textColor=colors.HexColor("#666680"), spaceAfter=2,
    )
    date_style = ParagraphStyle(
        "DateLabel", parent=styles["Normal"],
        fontSize=12, textColor=DARK, fontName="Helvetica-Bold",
    )
    topic_style = ParagraphStyle(
        "Topic", parent=styles["Normal"],
        fontSize=10, textColor=DARK, leftIndent=10, spaceAfter=2,
    )
    meta_style = ParagraphStyle(
        "Meta", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#888888"),
    )

    story = []

    # Header
    story.append(Paragraph("📚 AI Study Planner", title_style))
    story.append(Paragraph(f"Subject: <b>{subject}</b>   |   Exam: <b>{exam_date}</b>   |   Total days: <b>{len(plan)}</b>", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=12))

    TYPE_COLORS = {
        "study":    (STUDY_BG,    "📘 Study Day"),
        "revision": (REVISION_BG, "🔄 Revision Day"),
        "buffer":   (BUFFER_BG,   "🎯 Exam Day"),
    }

    for day in plan:
        bg, label = TYPE_COLORS.get(day.get("type", "study"), (LIGHT_GRAY, "📅 Day"))

        # Day header row
        header_data = [[
            Paragraph(f"{day['day']}, {day['date']}", date_style),
            Paragraph(f"{label}   ·   {day['hours']}h", meta_style),
        ]]
        header_table = Table(header_data, colWidths=["60%", "40%"])
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ("ROUNDEDCORNERS", [4]),
        ]))
        story.append(header_table)

        # Topics
        for topic in day.get("topics", []):
            story.append(Paragraph(f"• {topic}", topic_style))

        story.append(Spacer(1, 10))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=8, spaceAfter=4))
    story.append(Paragraph(f"Generated on {date.today().strftime('%B %d, %Y')} · AI-Powered Study Planner", meta_style))

    doc.build(story)
    return buf.getvalue()