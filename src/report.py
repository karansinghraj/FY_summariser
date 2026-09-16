import io
import os
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from src.schema import ReportData
from src.chart_generator import generate_financial_chart

# Color Palette Definitions
GEOJIT_GREEN = colors.HexColor("#005A36")
GEOJIT_LIGHT_BG = colors.HexColor("#F0FDF4")
NAVY_HEADER = colors.HexColor("#1E293B")
TEXT_DARK = colors.HexColor("#0F172A")
TEXT_MUTED = colors.HexColor("#475569")
BORDER_COLOR = colors.HexColor("#CBD5E1")
GOLD_ACCENT = colors.HexColor("#D4AF37")
TABLE_BG_ALT = colors.HexColor("#F8FAFC")

class NumberedCanvas(canvas.Canvas):
    """Custom canvas that dynamically adds headers, footers, and page numbers (X of Y)."""
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
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        
        # Header Line & Branding
        self.setStrokeColor(GEOJIT_GREEN)
        self.setLineWidth(1.5)
        self.line(36, 806, 559, 806)

        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(GEOJIT_GREEN)
        self.drawString(36, 812, "GEOJIT EQUITY RESEARCH")

        self.setFont("Helvetica", 8)
        self.setFillColor(TEXT_MUTED)
        self.drawRightString(559, 812, "INSTITUTIONAL & RETAIL RESEARCH")

        # Footer Line & Page Numbers
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.75)
        self.line(36, 45, 559, 45)

        self.setFont("Helvetica", 8)
        self.setFillColor(TEXT_MUTED)
        self.drawString(36, 32, "Geojit Financial Services Ltd. | SEBI Reg: INH200000345")
        self.drawRightString(559, 32, f"Page {self._pageNumber} of {page_count}")

        self.restoreState()

def create_geojit_pdf(report_data: ReportData, output_path: str = None) -> bytes:
    """
    Generates a 4-page Geojit-styled Equity Research PDF report.
    Returns bytes or writes to file if output_path is specified.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        output_path or buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=48,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=NAVY_HEADER,
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=TEXT_MUTED,
        spaceAfter=10
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=GEOJIT_GREEN,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_DARK,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=10,
        spaceAfter=4
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1 # Center
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=TEXT_DARK,
        alignment=0 # Left
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=TEXT_DARK,
        alignment=1 # Center
    )

    story = []

    # ==========================================
    # PAGE 1: RESEARCH OVERVIEW & HIGHLIGHTS
    # ==========================================
    
    # Header Info Block
    story.append(Paragraph(f"<b>{report_data.company_name}</b>", title_style))
    story.append(Paragraph(
        f"Sector: <b>{report_data.sector}</b> &nbsp;|&nbsp; BSE Code: <b>{report_data.bse_code}</b> &nbsp;|&nbsp; NSE Symbol: <b>{report_data.ticker}</b> &nbsp;|&nbsp; Date: <b>{report_date_str(report_data.report_date)}</b>",
        subtitle_style
    ))

    # Rating & Target Price Banner Grid
    rating_color = GEOJIT_GREEN if report_data.recommendation in ["BUY", "ACCUMULATE"] else NAVY_HEADER
    
    banner_data = [
        [
            Paragraph(f"<font color='white'><b>RATING: {report_data.recommendation}</b></font>", ParagraphStyle('R', fontName='Helvetica-Bold', fontSize=10, textColor=colors.white, alignment=1)),
            Paragraph(f"TARGET PRICE: <b>{report_data.target_price}</b>", ParagraphStyle('TP', fontName='Helvetica', fontSize=9, alignment=1)),
            Paragraph(f"CMP: <b>{report_data.cmp}</b>", ParagraphStyle('CMP', fontName='Helvetica', fontSize=9, alignment=1)),
            Paragraph(f"UPSIDE: <b>{report_data.upside_downside}</b>", ParagraphStyle('UP', fontName='Helvetica', fontSize=9, alignment=1))
        ]
    ]
    banner_table = Table(banner_data, colWidths=[130, 130, 130, 133])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), rating_color),
        ('BACKGROUND', (1, 0), (-1, -1), GEOJIT_LIGHT_BG),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 8))

    # Key Data Grid Table
    key_data = [
        [
            Paragraph("<b>Market Cap (Rs)</b>", table_cell_style), Paragraph(report_data.market_cap, table_cell_center),
            Paragraph("<b>52 Wk H / L (Rs)</b>", table_cell_style), Paragraph(report_data.fifty_two_week_high_low, table_cell_center)
        ],
        [
            Paragraph("<b>Shares Outstanding</b>", table_cell_style), Paragraph(report_data.shares_outstanding, table_cell_center),
            Paragraph("<b>Bloomberg Ticker</b>", table_cell_style), Paragraph(report_data.bloomberg_code, table_cell_center)
        ]
    ]
    key_table = Table(key_data, colWidths=[130, 130, 130, 133])
    key_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), TABLE_BG_ALT),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(key_table)
    story.append(Spacer(1, 10))

    # Executive Summary / Thesis Box
    story.append(Paragraph("EXECUTIVE INVESTMENT SUMMARY", section_heading))
    story.append(Paragraph(report_data.executive_summary, body_style))
    story.append(Spacer(1, 6))

    # Key Performance Highlights
    story.append(Paragraph("KEY OPERATIONAL HIGHLIGHTS", section_heading))
    for highlight in report_data.key_highlights:
        story.append(Paragraph(f"• &nbsp; {highlight}", bullet_style))
    story.append(Spacer(1, 8))

    # Financial Performance Visual Chart
    story.append(Paragraph("QUARTERLY PERFORMANCE & MARGIN TRAJECTORY", section_heading))
    chart_buf = generate_financial_chart(report_data)
    story.append(Image(chart_buf, width=523, height=170))
    
    # Page 1 Break
    story.append(PageBreak())

    # ==========================================
    # PAGE 2: QUARTERLY FINANCIALS & OUTLOOK
    # ==========================================
    story.append(Paragraph(f"<b>{report_data.company_name}</b> — Quarterly Analysis & Outlook", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=GEOJIT_GREEN, spaceBefore=4, spaceAfter=8))

    story.append(Paragraph("DETAILED QUARTERLY FINANCIAL PERFORMANCE", section_heading))
    
    # Quarterly Table Header
    q_headers = [
        Paragraph("<b>Quarter</b>", table_header_style),
        Paragraph("<b>Revenue / NII</b>", table_header_style),
        Paragraph("<b>EBITDA / Op.Profit</b>", table_header_style),
        Paragraph("<b>Margin %</b>", table_header_style),
        Paragraph("<b>PAT</b>", table_header_style),
        Paragraph("<b>PAT Margin %</b>", table_header_style),
        Paragraph("<b>EPS (Rs)</b>", table_header_style)
    ]
    
    q_rows = [q_headers]
    for q in report_data.quarterly_financials:
        q_rows.append([
            Paragraph(f"<b>{q.quarter}</b>", table_cell_center),
            Paragraph(q.revenue, table_cell_center),
            Paragraph(q.ebitda, table_cell_center),
            Paragraph(q.ebitda_margin, table_cell_center),
            Paragraph(q.pat, table_cell_center),
            Paragraph(q.pat_margin, table_cell_center),
            Paragraph(q.eps, table_cell_center)
        ])

    q_table = Table(q_rows, colWidths=[70, 75, 80, 75, 75, 75, 73])
    q_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GEOJIT_GREEN),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, TABLE_BG_ALT]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(q_table)
    story.append(Spacer(1, 12))

    # Business Outlook Section
    story.append(Paragraph("BUSINESS OUTLOOK & STRATEGIC INITIATIVES", section_heading))
    story.append(Paragraph(report_data.outlook, body_style))
    story.append(Spacer(1, 8))

    # Earnings Estimates Notes
    story.append(Paragraph("EARNINGS ESTIMATES & REVISION SUMMARY", section_heading))
    story.append(Paragraph(report_data.estimate_change_notes, body_style))
    story.append(Spacer(1, 12))

    # Callout Box for Banking / Operational Focus
    box_title = "BANKING & CREDIT QUALITY HIGHLIGHTS" if report_data.is_banking else "MANUFACTURING & OPERATIONAL EFFICIENCY"
    box_content = (
        "Strong liability profile with high CASA ratio, prudent provision coverage ratio (>80%), and robust CET-1 capital framework."
        if report_data.is_banking else
        "Disciplined raw material hedging, expanding domestic distribution reach, and increasing value-added chemical recycling export market share."
    )
    
    callout_data = [[
        Paragraph(f"<b>{box_title}</b><br/><br/>{box_content}", ParagraphStyle('Callout', parent=body_style, textColor=NAVY_HEADER))
    ]]
    callout_table = Table(callout_data, colWidths=[523])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), GEOJIT_LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, GEOJIT_GREEN),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(callout_table)

    # Page 2 Break
    story.append(PageBreak())

    # ==========================================
    # PAGE 3: ANNUAL FINANCIAL STATEMENTS
    # ==========================================
    story.append(Paragraph(f"<b>{report_data.company_name}</b> — Financial Statements & Ratios", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=GEOJIT_GREEN, spaceBefore=4, spaceAfter=8))

    # Helper function to render annual financial table
    def render_annual_table(title: str, rows_data: List[Any], headers: List[str] = None):
        story.append(Paragraph(title, section_heading))
        h_list = headers or ["Metric (Rs Mn)", "FY24", "FY25", "FY26E", "FY27E"]
        table_rows = [[Paragraph(f"<b>{h}</b>", table_header_style if i==0 or i>0 else table_header_style) for i, h in enumerate(h_list)]]
        
        for r in rows_data:
            table_rows.append([
                Paragraph(f"<b>{r.metric}</b>", table_cell_style),
                Paragraph(r.year_1, table_cell_center),
                Paragraph(r.year_2, table_cell_center),
                Paragraph(r.year_3, table_cell_center),
                Paragraph(r.year_4, table_cell_center)
            ])
            
        t = Table(table_rows, colWidths=[203, 80, 80, 80, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), GEOJIT_GREEN),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, TABLE_BG_ALT]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        return t

    # 1. Income Statement
    if report_data.income_statement:
        story.append(render_annual_table("CONSOLIDATED PROFIT & LOSS STATEMENT", report_data.income_statement))
        story.append(Spacer(1, 10))

    # 2. Balance Sheet
    if report_data.balance_sheet:
        story.append(render_annual_table("CONSOLIDATED BALANCE SHEET SUMMARY", report_data.balance_sheet))
        story.append(Spacer(1, 10))

    # 3. Cash Flow
    if report_data.cash_flow:
        story.append(render_annual_table("CASH FLOW STATEMENT SUMMARY", report_data.cash_flow))
        story.append(Spacer(1, 10))

    # 4. Key Valuation Ratios
    if report_data.key_ratios:
        story.append(render_annual_table("VALUATION METRICS & FINANCIAL RATIOS", report_data.key_ratios))

    # Page 3 Break
    story.append(PageBreak())

    # ==========================================
    # PAGE 4: RECOMMENDATION HISTORY & DISCLOSURES
    # ==========================================
    story.append(Paragraph(f"<b>{report_data.company_name}</b> — Recommendation History & Disclosures", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=GEOJIT_GREEN, spaceBefore=4, spaceAfter=8))

    story.append(Paragraph("RECOMMENDATION HISTORY & TRACK RECORD", section_heading))
    
    rec_headers = [
        Paragraph("<b>Date</b>", table_header_style),
        Paragraph("<b>Rating</b>", table_header_style),
        Paragraph("<b>Target Price (Rs)</b>", table_header_style),
        Paragraph("<b>CMP (Rs)</b>", table_header_style)
    ]
    rec_rows = [rec_headers]
    for rh in report_data.recommendation_history:
        rec_rows.append([
            Paragraph(rh.date, table_cell_center),
            Paragraph(f"<b>{rh.rating}</b>", table_cell_center),
            Paragraph(rh.target_price, table_cell_center),
            Paragraph(rh.cmp, table_cell_center)
        ])
    
    rec_table = Table(rec_rows, colWidths=[130, 130, 130, 133])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY_HEADER),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, TABLE_BG_ALT]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 12))

    # Rating Definition Scale Table
    story.append(Paragraph("GEOJIT RATING DEFINITIONS & METHODOLOGY", section_heading))
    rating_matrix = [
        [Paragraph("<b>Rating</b>", table_header_style), Paragraph("<b>Definition / Upside Expectations</b>", table_header_style)],
        [Paragraph("<b>BUY</b>", table_cell_center), Paragraph("Stock return expected to exceed 15% over a 12-month horizon.", table_cell_style)],
        [Paragraph("<b>ACCUMULATE</b>", table_cell_center), Paragraph("Stock return expected to be between 10% - 15% over a 12-month horizon.", table_cell_style)],
        [Paragraph("<b>HOLD</b>", table_cell_center), Paragraph("Stock return expected to be between 0% - 10% over a 12-month horizon.", table_cell_style)],
        [Paragraph("<b>REDUCE / SELL</b>", table_cell_center), Paragraph("Stock return expected to be negative over a 12-month horizon.", table_cell_style)],
        [Paragraph("<b>NOT RATED</b>", table_cell_center), Paragraph("Coverage under review or institutional context report without explicit TP.", table_cell_style)]
    ]
    rating_table = Table(rating_matrix, colWidths=[130, 393])
    rating_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GEOJIT_GREEN),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, TABLE_BG_ALT]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(rating_table)
    story.append(Spacer(1, 14))

    # Regulatory Disclosures & Analyst Disclaimer Box
    story.append(Paragraph("ANALYST CERTIFICATION & REGULATORY DISCLOSURES", section_heading))
    story.append(Paragraph(report_data.disclosures, ParagraphStyle('Disc', parent=body_style, fontSize=7.5, leading=10, textColor=TEXT_MUTED)))
    story.append(Spacer(1, 10))

    disclaimer_box = [[
        Paragraph(
            "<b>DISCLAIMER:</b> Geojit Financial Services Ltd. (GFSL) is a SEBI registered Research Analyst holding registration number INH200000345. "
            "This report is prepared for private distribution only and does not constitute financial advice. Investors are advised to consult their certified financial advisor before investing.",
            ParagraphStyle('DiscBox', parent=body_style, fontSize=7, leading=9.5, textColor=NAVY_HEADER)
        )
    ]]
    disc_table = Table(disclaimer_box, colWidths=[523])
    disc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), TABLE_BG_ALT),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('PADDING', (0, 0), (-1, -1), 8)
    ]))
    story.append(disc_table)

    # Build PDF with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    
    if output_path:
        return output_path
    
    buffer.seek(0)
    return buffer.getvalue()

def report_date_str(val: str) -> str:
    return val if val and val != "—" else "November 2025"
