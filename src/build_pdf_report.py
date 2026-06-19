from pathlib import Path
import logging
import textwrap

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Image,
    Table,
    TableStyle,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
SQL_OUTPUTS_DIR = REPORTS_DIR / "sql_outputs"
EDA_OUTPUTS_DIR = REPORTS_DIR / "eda_outputs"
STAT_OUTPUTS_DIR = REPORTS_DIR / "statistical_outputs"

INPUT_MD = REPORTS_DIR / "final_report.md"
OUTPUT_PDF = REPORTS_DIR / "final_report.pdf"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def create_styles():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="TitleCustom",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17365D"),
            spaceAfter=18,
        )
    )

    styles.add(
        ParagraphStyle(
            name="Heading1Custom",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            textColor=colors.HexColor("#17365D"),
            spaceBefore=14,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="Heading2Custom",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#1F4E79"),
            spaceBefore=10,
            spaceAfter=6,
        )
    )

    styles.add(
        ParagraphStyle(
            name="BodyCustom",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        )
    )

    styles.add(
        ParagraphStyle(
            name="BulletCustom",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            leftIndent=14,
            bulletIndent=6,
            spaceAfter=3,
        )
    )

    styles.add(
        ParagraphStyle(
            name="CodeCustom",
            parent=styles["Code"],
            fontName="Courier",
            fontSize=8,
            leading=10,
            backColor=colors.HexColor("#F3F3F3"),
            borderPadding=4,
            spaceAfter=6,
        )
    )

    return styles


def clean_text(text):
    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "`": "",
        "**": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.strip()


def add_markdown_content(story, styles):
    if not INPUT_MD.exists():
        raise FileNotFoundError(f"Report markdown not found: {INPUT_MD}")

    logging.info("Reading report markdown from %s", INPUT_MD)

    lines = INPUT_MD.read_text(encoding="utf-8").splitlines()
    in_code_block = False
    code_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_lines = []
            else:
                in_code_block = False
                code_text = "<br/>".join(clean_text(code_line) for code_line in code_lines)
                if code_text:
                    story.append(Paragraph(code_text, styles["CodeCustom"]))
                    story.append(Spacer(1, 0.15 * cm))
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if not stripped:
            story.append(Spacer(1, 0.12 * cm))
            continue

        if stripped.startswith("# "):
            story.append(Paragraph(clean_text(stripped.replace("# ", "")), styles["TitleCustom"]))
            story.append(Spacer(1, 0.3 * cm))
        elif stripped.startswith("## "):
            story.append(Paragraph(clean_text(stripped.replace("## ", "")), styles["Heading1Custom"]))
        elif stripped.startswith("### "):
            story.append(Paragraph(clean_text(stripped.replace("### ", "")), styles["Heading2Custom"]))
        elif stripped.startswith("- "):
            story.append(
                Paragraph(
                    clean_text(stripped.replace("- ", "")),
                    styles["BulletCustom"],
                    bulletText="•",
                )
            )
        else:
            story.append(Paragraph(clean_text(stripped), styles["BodyCustom"]))


def add_figure_appendix(story, styles):
    if not FIGURES_DIR.exists():
        return

    figure_files = sorted(FIGURES_DIR.glob("*.png"))

    if not figure_files:
        return

    story.append(PageBreak())
    story.append(Paragraph("Appendix B. Figure Gallery", styles["Heading1Custom"]))

    for index, figure_path in enumerate(figure_files, start=1):
        story.append(PageBreak())
        figure_title = figure_path.stem.replace("_", " ").title()
        story.append(Paragraph(f"Figure B.{index}: {figure_title}", styles["Heading2Custom"]))

        try:
            image = Image(str(figure_path))
            image._restrictSize(17 * cm, 21 * cm)
            story.append(image)
        except Exception as error:
            story.append(
                Paragraph(
                    f"Could not load figure {figure_path.name}: {error}",
                    styles["BodyCustom"],
                )
            )


def dataframe_to_table(df):
    
    df = df.head(8).copy()
    df = df.fillna("")


    data = [list(df.columns)] + df.astype(str).values.tolist()

    wrapped_data = []
    for row in data:
        wrapped_row = []
        for value in row:
            wrapped_value = "\n".join(textwrap.wrap(str(value), width=16))
            wrapped_row.append(wrapped_value)
        wrapped_data.append(wrapped_row)

    table = Table(wrapped_data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 5.8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    return table


def add_csv_appendix(story, styles, title, directory, label):
    if not directory.exists():
        return

    csv_files = sorted(directory.glob("*.csv"))

    if not csv_files:
        return

    story.append(PageBreak())
    story.append(Paragraph(title, styles["Heading1Custom"]))

    for index, csv_path in enumerate(csv_files, start=1):
        story.append(PageBreak())
        table_title = csv_path.stem.replace("_", " ").title()

        story.append(Paragraph(f"{label}.{index}: {table_title}", styles["Heading2Custom"]))
        story.append(Paragraph(f"Source file: {csv_path.relative_to(PROJECT_ROOT)}", styles["BodyCustom"]))

        try:
            df = pd.read_csv(csv_path)
            story.append(dataframe_to_table(df))
        except Exception as error:
            story.append(
                Paragraph(
                    f"Could not load table {csv_path.name}: {error}",
                    styles["BodyCustom"],
                )
            )


def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(A4[0] / 2, 1.0 * cm, f"Page {page_num}")


def build_pdf():
    logging.info("Creating PDF report at %s", OUTPUT_PDF)

    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.8 * cm,
    )

    styles = create_styles()
    story = []

    add_markdown_content(story, styles)
    add_figure_appendix(story, styles)

    add_csv_appendix(
        story,
        styles,
        "Appendix C. SQL Output Tables",
        SQL_OUTPUTS_DIR,
        "C",
    )

    add_csv_appendix(
        story,
        styles,
        "Appendix D. EDA Output Tables",
        EDA_OUTPUTS_DIR,
        "D",
    )

    add_csv_appendix(
        story,
        styles,
        "Appendix E. Statistical Output Tables",
        STAT_OUTPUTS_DIR,
        "E",
    )

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)

    logging.info("PDF report created successfully")


def main():
    build_pdf()


if __name__ == "__main__":
    main()