"""Programmatic PDF Report Generator.

Compiles executive-grade A4 PDF dossiers using ReportLab:
- Professional header banner with metadata
- Two-pass automatic page numbering ('Page X of Y') and footer notes
- Styled report sections (Executive Summary, Dynamics, Outlook)
- Formatted tabular grid for Pandas summary statistics
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)

from crew.tools.financial_parser import get_summary_dataframe, get_raw_dataframe


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically calculate and render 'Page X of Y' and footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))  # Slate grey

        width, height = A4
        margin = 36  # 0.5 inch margin

        # Draw Top Header Banner Rule on subsequent pages
        if self._pageNumber > 1:
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(margin, height - 30, width - margin, height - 30)
            self.drawString(margin, height - 25, "MARKET RESEARCH INTELLIGENCE DOSSIER | CrewAI + Gemini")
            self.drawRightString(width - margin, height - 25, datetime.now().strftime("%B %d, %Y"))

        # Draw Bottom Footer Rule & Page Numbering
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(margin, 35, width - margin, 35)

        footer_text = "CONFIDENTIAL & PROPRIETARY — Multi-Agent Research Engine"
        self.drawString(margin, 22, footer_text)

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(width - margin, 22, page_str)

        self.restoreState()


def _build_styles() -> Dict[str, ParagraphStyle]:
    """Build and customize typographic styles."""
    styles = getSampleStyleSheet()

    custom_styles = {
        "BannerTitle": ParagraphStyle(
            "BannerTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#FFFFFF"),
            alignment=0,
        ),
        "BannerSubtitle": ParagraphStyle(
            "BannerSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#93C5FD"),  # Light blue accent
            alignment=0,
        ),
        "BannerMeta": ParagraphStyle(
            "BannerMeta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#E2E8F0"),
        ),
        "SectionHeading": ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1E3A8A"),  # Deep Navy
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "SubSectionHeading": ParagraphStyle(
            "SubSectionHeading",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#0F766E"),  # Dark Teal
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "BodyDark": ParagraphStyle(
            "BodyDark",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#1E293B"),
            spaceAfter=6,
        ),
        "BulletItem": ParagraphStyle(
            "BulletItem",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13.5,
            textColor=colors.HexColor("#334155"),
            leftIndent=15,
            spaceAfter=3,
        ),
        "TableHead": ParagraphStyle(
            "TableHead",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#FFFFFF"),
            alignment=1,
        ),
        "TableCell": ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor("#0F172A"),
            alignment=1,
        ),
        "TableLabel": ParagraphStyle(
            "TableLabel",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1E293B"),
            alignment=0,
        ),
    }

    return custom_styles


def _create_kpi_cards(csv_path: str, styles: Dict[str, ParagraphStyle], printable_width: float) -> Optional[Table]:
    """Generates an executive KPI metrics card row for the PDF report."""
    try:
        df = get_raw_dataframe(csv_path)
        col_w = printable_width / 4.0

        # Extract representative metrics safely
        rev_val = f"${df['Revenue_B'].median():.1f}B" if "Revenue_B" in df.columns else "N/A"
        margin_val = f"{df['Net_Margin_Pct'].mean():.1f}%" if "Net_Margin_Pct" in df.columns else "N/A"
        pe_val = f"{df['PE_Ratio'].median():.1f}x" if "PE_Ratio" in df.columns else "N/A"
        fcf_val = f"${df['Free_Cash_Flow_B'].mean():.1f}B" if "Free_Cash_Flow_B" in df.columns else "N/A"

        lbl_style = ParagraphStyle(
            "KPILabel",
            fontName="Helvetica-Bold",
            fontSize=7,
            leading=8.5,
            textColor=colors.HexColor("#94A3B8"),
            alignment=1,
        )
        val_style = ParagraphStyle(
            "KPIVal",
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#38BDF8"),  # Bright sky cyan
            alignment=1,
        )

        card1 = [Spacer(1, 2), Paragraph("MEDIAN REVENUE", lbl_style), Spacer(1, 2), Paragraph(rev_val, val_style), Spacer(1, 2)]
        card2 = [Spacer(1, 2), Paragraph("AVG NET MARGIN", lbl_style), Spacer(1, 2), Paragraph(margin_val, val_style), Spacer(1, 2)]
        card3 = [Spacer(1, 2), Paragraph("MEDIAN P/E MULTIPLE", lbl_style), Spacer(1, 2), Paragraph(pe_val, val_style), Spacer(1, 2)]
        card4 = [Spacer(1, 2), Paragraph("AVG FREE CASH FLOW", lbl_style), Spacer(1, 2), Paragraph(fcf_val, val_style), Spacer(1, 2)]

        kpi_table = Table([[card1, card2, card3, card4]], colWidths=[col_w] * 4)
        kpi_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0F172A")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1E293B")),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        return kpi_table
    except Exception:
        return None


def _create_header_banner(query: str, styles: Dict[str, ParagraphStyle], printable_width: float) -> Table:
    """Creates the modern executive header banner with document metadata."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    left_content = [
        Paragraph("MARKET INTELLIGENCE DOSSIER", styles["BannerTitle"]),
        Spacer(1, 4),
        Paragraph(f"Query: {query.upper()}", styles["BannerSubtitle"]),
    ]

    right_content = [
        Paragraph(f"<b>Date:</b> {now_str}", styles["BannerMeta"]),
        Paragraph("<b>Classification:</b> Institutional Advisory", styles["BannerMeta"]),
        Paragraph("<b>Orchestration:</b> CrewAI Hierarchical Team", styles["BannerMeta"]),
        Paragraph("<b>Core Engine:</b> Google Gemini API", styles["BannerMeta"]),
    ]

    banner_data = [[left_content, right_content]]
    col_w1 = printable_width * 0.62
    col_w2 = printable_width * 0.38

    banner_table = Table(banner_data, colWidths=[col_w1, col_w2])
    banner_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0F172A")),  # Dark Slate Blue
            ("PADDING", (0, 0), (-1, -1), 12),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
            ("TOPPADDING", (0, 0), (-1, -1), 14),
        ])
    )
    return banner_table


def _create_pandas_summary_table(
    csv_path: str, styles: Dict[str, ParagraphStyle], printable_width: float
) -> Table:
    """Builds an elegant ReportLab Table displaying Pandas summary statistics."""
    summary_df = get_summary_dataframe(csv_path)

    # Prepare table headers and rows
    columns = list(summary_df.columns)
    headers = ["Metric"] + [c.replace("_", " ") for c in columns]
    header_paragraphs = [Paragraph(h, styles["TableHead"]) for h in headers]

    table_data = [header_paragraphs]

    metrics_labels = {
        "count": "Sample Count",
        "mean": "Mean Average",
        "std": "Std. Deviation",
        "min": "Minimum",
        "25%": "25th Percentile",
        "50%": "Median (50%)",
        "75%": "75th Percentile",
        "max": "Maximum",
    }

    for idx, row in summary_df.iterrows():
        label = metrics_labels.get(str(idx), str(idx).upper())
        row_cells = [Paragraph(label, styles["TableLabel"])]
        for col in columns:
            val = row[col]
            formatted_val = f"{val:,.2f}" if isinstance(val, (int, float)) else str(val)
            row_cells.append(Paragraph(formatted_val, styles["TableCell"]))
        table_data.append(row_cells)

    num_cols = len(headers)
    metric_col_w = printable_width * 0.22
    data_col_w = (printable_width - metric_col_w) / (num_cols - 1) if num_cols > 1 else printable_width
    col_widths = [metric_col_w] + [data_col_w] * (num_cols - 1)

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),  # Navy Header
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]

    # Alternating row colors
    for i in range(1, len(table_data)):
        bg = colors.HexColor("#F8FAFC") if i % 2 == 1 else colors.HexColor("#FFFFFF")
        style_commands.append(("BACKGROUND", (0, i), (-1, i), bg))

    t.setStyle(TableStyle(style_commands))
    return t


def generate_pdf_report(
    markdown_content: str,
    output_pdf_path: str,
    query: str,
    csv_path: Optional[str] = None,
) -> str:
    """Compiles the report copy and Pandas summary table into an A4 PDF document.

    Args:
        markdown_content (str): Report draft from Content Writer agent.
        output_pdf_path (str): Destination path for the compiled PDF.
        query (str): Research query title.
        csv_path (str, optional): Financial dataset CSV path.

    Returns:
        str: Absolute path to the generated PDF.
    """
    out_path = Path(output_pdf_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Document Geometry
    margin = 36  # 0.5 inch
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin + 6,
        bottomMargin=margin + 6,
    )

    printable_width = A4[0] - (2 * margin)
    styles = _build_styles()
    story = []

    # 1. Header Banner & Executive KPI Metrics Row
    story.append(_create_header_banner(query, styles, printable_width))
    story.append(Spacer(1, 8))

    if csv_path and Path(csv_path).is_file():
        kpi_table = _create_kpi_cards(csv_path, styles, printable_width)
        if kpi_table:
            story.append(kpi_table)
            story.append(Spacer(1, 10))
    else:
        story.append(Spacer(1, 6))

    # 2. Parse Markdown Sections
    lines = markdown_content.split("\n")
    skip_table_block = False

    for line in lines:
        stripped = line.strip()

        # Handle Markdown Table omission if raw markdown tables were emitted
        if stripped.startswith("|"):
            skip_table_block = True
            continue
        elif skip_table_block and not stripped:
            skip_table_block = False
            continue

        if not stripped:
            story.append(Spacer(1, 4))
            continue

        # Headings
        if stripped.startswith("# "):
            title_text = stripped[2:].strip()
            # If it's a title, render as section banner
            story.append(Paragraph(title_text, styles["SectionHeading"]))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=8))
        elif stripped.startswith("## "):
            heading_text = stripped[3:].strip()
            story.append(Spacer(1, 6))
            story.append(Paragraph(heading_text, styles["SectionHeading"]))
            story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#93C5FD"), spaceAfter=6))
            
            # If this is the Financial Analysis section, inject the Pandas Summary Table!
            if "financial" in heading_text.lower() or "statistic" in heading_text.lower():
                if csv_path and Path(csv_path).is_file():
                    story.append(Paragraph("<b>Table 1: Descriptive Financial Statistics & Summary Matrix (Pandas Engine)</b>", styles["SubSectionHeading"]))
                    story.append(Spacer(1, 4))
                    story.append(_create_pandas_summary_table(csv_path, styles, printable_width))
                    story.append(Spacer(1, 8))
        elif stripped.startswith("### "):
            sub_text = stripped[4:].strip()
            story.append(Paragraph(sub_text, styles["SubSectionHeading"]))
        elif stripped.startswith(("- ", "* ", "• ")):
            bullet_text = stripped[2:].strip()
            # Clean markdown bold
            bullet_html = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", bullet_text)
            story.append(Paragraph(f"• {bullet_html}", styles["BulletItem"]))
        else:
            # Regular paragraph text
            clean_html = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", stripped)
            story.append(Paragraph(clean_html, styles["BodyDark"]))

    # Always ensure the summary table is appended if not triggered in headings
    table_rendered = any(
        isinstance(item, Table) and len(item._cellvalues) > 1 for item in story[1:]
    )
    if not table_rendered and csv_path and Path(csv_path).is_file():
        story.append(Spacer(1, 10))
        story.append(
            Paragraph("<b>Table 1: Corporate Financial Statistics & Summary Grid (Pandas Engine)</b>", styles["SectionHeading"])
        )
        story.append(Spacer(1, 4))
        story.append(_create_pandas_summary_table(csv_path, styles, printable_width))

    # Build PDF with custom two-pass NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    return str(out_path)
