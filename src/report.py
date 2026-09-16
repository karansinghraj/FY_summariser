import io
import os
from typing import List, Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from src.schema import ReportData
from src.chart_generator import (
    generate_price_performance_chart,
    generate_quad_charts_page2,
    generate_recommendation_history_chart
)

# Colors matching Geojit Reference Report
GEOJIT_GREEN = colors.HexColor("#005A36")
GEOJIT_TEAL = "#008B8B"
HEADER_GRAY = colors.HexColor("#005A36")
BG_LIGHT_GREEN = colors.HexColor("#F0FDF4")
NAVY_TITLE = colors.HexColor("#000000")
TEXT_DARK = colors.HexColor("#000000")
TEXT_MUTED = colors.HexColor("#333333")
BORDER_COLOR = colors.HexColor("#CBD5E1")
TABLE_HEADER_BG = colors.HexColor("#005A36")
TABLE_ALT_BG = colors.HexColor("#F8FAFC")

class NumberedCanvas(canvas.Canvas):
    """Custom canvas drawing top header banner and page numbers."""
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
        # Top banner color block
        self.setFillColor(GEOJIT_GREEN)
        self.rect(0, 815, 595.27, 26.89, fill=1, stroke=0)

        # Bottom footer line
        self.setStrokeColor(GEOJIT_GREEN)
        self.setLineWidth(1)
        self.line(18, 25, 577, 25)

        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#005A36"))
        self.drawString(18, 14, "www.geojit.com")

        self.restoreState()

def create_geojit_pdf(report_data: ReportData, output_path: str = None) -> bytes:
    """Generates an exact pixel-aligned 4-page Geojit Equity Research PDF report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        output_path or buffer,
        pagesize=A4,
        leftMargin=18,
        rightMargin=18,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Typography Styles
    style_retail = ParagraphStyle('Retail', fontName='Helvetica-Bold', fontSize=14, textColor=GEOJIT_GREEN, leading=16)
    style_comp_title = ParagraphStyle('CompTitle', fontName='Helvetica-Bold', fontSize=22, textColor=NAVY_TITLE, leading=24)
    style_sector = ParagraphStyle('Sector', fontName='Helvetica', fontSize=9, textColor=TEXT_DARK, leading=11)
    style_headline = ParagraphStyle('Headline', fontName='Helvetica-Bold', fontSize=12, textColor=GEOJIT_GREEN, leading=14, spaceAfter=4)
    style_section = ParagraphStyle('SecHead', fontName='Helvetica-Bold', fontSize=10, textColor=GEOJIT_GREEN, leading=12, spaceBefore=4, spaceAfter=2)
    style_body = ParagraphStyle('Body', fontName='Helvetica', fontSize=8, textColor=TEXT_DARK, leading=10, spaceAfter=4)
    style_bullet = ParagraphStyle('Bullet', fontName='Helvetica', fontSize=7.5, textColor=TEXT_DARK, leading=9.5, leftIndent=8, spaceAfter=3)

    st_hdr = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=6.5, textColor=colors.white, alignment=1)
    st_cell_l = ParagraphStyle('TCL', fontName='Helvetica', fontSize=6.5, textColor=TEXT_DARK, leading=7.5)
    st_cell_c = ParagraphStyle('TCC', fontName='Helvetica', fontSize=6.5, textColor=TEXT_DARK, leading=7.5, alignment=1)
    st_cell_b_c = ParagraphStyle('TCBC', fontName='Helvetica-Bold', fontSize=6.5, textColor=TEXT_DARK, leading=7.5, alignment=1)

    story = []

    # ==========================================
    # PAGE 1: RESEARCH OVERVIEW & HIGHLIGHTS
    # ==========================================

    # 1. Top Header Row
    top_header_table = Table([
        [
            Paragraph(f"<b>Retail Equity Research</b><br/><font size=16 color='#000000'><b>{report_data.company_name}</b></font><br/><font size=8 color='#333333'>Sector: {report_data.sector}</font>", ParagraphStyle('HLeft', fontName='Helvetica', fontSize=8, leading=10)),
            Paragraph(f"<font color='#005A36' size=14><b>G GEOJIT</b></font><br/><font size=6 color='#333333'>PEOPLE YOU PROSPER WITH</font><br/><br/><font size=8 color='#000000'><b>{report_data.report_date}</b></font>", ParagraphStyle('HRight', fontName='Helvetica', fontSize=8, leading=10, alignment=2))
        ]
    ], colWidths=[360, 199])
    top_header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(top_header_table)
    story.append(Spacer(1, 4))

    # 2. Key Changes & Rating Banner Grid
    rating_color = GEOJIT_GREEN if report_data.recommendation in ["BUY", "ACCUMULATE"] else colors.HexColor("#475569")
    banner_row1 = [
        Paragraph("<b>Key Changes</b>", st_cell_c),
        Paragraph("Target ▲" if report_data.target_change=="UP" else "Target ▼", st_cell_c),
        Paragraph("Rating ▼" if report_data.rating_change=="DOWNGRADE" else "Rating ▲", st_cell_c),
        Paragraph("Earnings ▼", st_cell_c),
        Paragraph(f"<font color='white'><b>{report_data.recommendation}</b></font>", ParagraphStyle('RB', fontName='Helvetica-Bold', fontSize=10, textColor=colors.white, alignment=1)),
        Paragraph(f"Target: <b>{report_data.target_price}</b><br/>CMP: <b>{report_data.cmp}</b><br/>Return: <b>{report_data.return_pct}</b>", st_cell_l)
    ]
    banner_t = Table([banner_row1], colWidths=[70, 60, 60, 60, 120, 189])
    banner_t.setStyle(TableStyle([
        ('BACKGROUND', (4, 0), (4, 0), rating_color),
        ('BACKGROUND', (5, 0), (5, 0), BG_LIGHT_GREEN),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(banner_t)
    story.append(Spacer(1, 4))

    # 3. Stock Metadata Bar
    stock_bar = [
        [
            Paragraph(f"<b>Stock Type:</b> {report_data.stock_type}", st_cell_l),
            Paragraph(f"<b>Bloomberg Code:</b> {report_data.bloomberg_code}", st_cell_l),
            Paragraph(f"<b>Sensex:</b> {report_data.sensex}", st_cell_l),
            Paragraph(f"<b>NSE Code:</b> {report_data.nse_code}", st_cell_l),
            Paragraph(f"<b>BSE Code:</b> {report_data.bse_code}", st_cell_l),
            Paragraph(f"<b>Time Frame:</b> {report_data.time_frame}", st_cell_l)
        ]
    ]
    stock_t = Table(stock_bar, colWidths=[90, 100, 85, 90, 95, 99])
    stock_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), TABLE_ALT_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(stock_t)
    story.append(Spacer(1, 4))

    # 4. Page 1 Main Two-Column Layout (Left Panel: 190pt | Right Panel: 360pt)
    left_flow = []
    right_flow = []

    # Left Column: Company Data Table
    left_flow.append(Paragraph("<b>Company Data</b>", ParagraphStyle('CDH', fontName='Helvetica-Bold', fontSize=7, textColor=colors.white, backColor=GEOJIT_GREEN, alignment=0)))
    cd_rows = [
        [Paragraph("Market Cap (Rs.cr)", st_cell_l), Paragraph(report_data.market_cap_cr, st_cell_c)],
        [Paragraph("52 Week High — Low (Rs.)", st_cell_l), Paragraph(report_data.fifty_two_wk_high_low, st_cell_c)],
        [Paragraph("Enterprise Value (Rs. cr)", st_cell_l), Paragraph(report_data.enterprise_value_cr, st_cell_c)],
        [Paragraph("Outstanding Shares (cr)", st_cell_l), Paragraph(report_data.shares_outstanding_cr, st_cell_c)],
        [Paragraph("Free Float (%)", st_cell_l), Paragraph(report_data.free_float_pct, st_cell_c)],
        [Paragraph("Dividend Yield (%)", st_cell_l), Paragraph(report_data.dividend_yield_pct, st_cell_c)],
        [Paragraph("6m average volume (cr)", st_cell_l), Paragraph(report_data.six_m_avg_vol_cr, st_cell_c)],
        [Paragraph("Beta", st_cell_l), Paragraph(report_data.beta, st_cell_c)],
        [Paragraph("Face value (Rs. )", st_cell_l), Paragraph(report_data.face_value_rs, st_cell_c)]
    ]
    cd_t = Table(cd_rows, colWidths=[120, 65])
    cd_t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
    ]))
    left_flow.append(cd_t)
    left_flow.append(Spacer(1, 4))

    # Left Column: Shareholding Table
    left_flow.append(Paragraph("<b>Shareholding (%)</b>", ParagraphStyle('SHH', fontName='Helvetica-Bold', fontSize=7, textColor=colors.white, backColor=GEOJIT_GREEN, alignment=0)))
    sh_data = [[Paragraph("Category", st_cell_l)] + [Paragraph(f"<b>{h}</b>", st_cell_c) for h in report_data.shareholding_headers]]
    for r in report_data.shareholding_table:
        sh_data.append([Paragraph(r.category, st_cell_l), Paragraph(r.q1, st_cell_c), Paragraph(r.q2, st_cell_c), Paragraph(r.q3, st_cell_c)])
    sh_t = Table(sh_data, colWidths=[80, 35, 35, 35])
    sh_t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
    ]))
    left_flow.append(sh_t)
    left_flow.append(Spacer(1, 4))

    # Left Column: Price Performance Table
    left_flow.append(Paragraph("<b>Price Performance</b>", ParagraphStyle('PPH', fontName='Helvetica-Bold', fontSize=7, textColor=colors.white, backColor=GEOJIT_GREEN, alignment=0)))
    pp_data = [[Paragraph("Period", st_cell_l), Paragraph("3 Month", st_cell_c), Paragraph("6 Month", st_cell_c), Paragraph("1 Year", st_cell_c)]]
    for r in report_data.price_perf_table:
        pp_data.append([Paragraph(r.period, st_cell_l), Paragraph(r.absolute_return, st_cell_c), Paragraph(r.sensex_return, st_cell_c), Paragraph(r.relative_return, st_cell_c)])
    pp_t = Table(pp_data, colWidths=[65, 40, 40, 40])
    pp_t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
    ]))
    left_flow.append(pp_t)
    left_flow.append(Spacer(1, 4))

    # Left Column: Price Performance Chart
    p_chart_buf = generate_price_performance_chart(report_data)
    left_flow.append(Image(p_chart_buf, width=185, height=90))
    left_flow.append(Spacer(1, 4))

    # Left Column: Y.E March Summary Table
    left_flow.append(Paragraph("<b>Y.E March (cr)</b>", ParagraphStyle('YEH', fontName='Helvetica-Bold', fontSize=7, textColor=colors.white, backColor=GEOJIT_GREEN, alignment=0)))
    ye_data = [[Paragraph("Metric", st_cell_l)] + [Paragraph(f"<b>{h}</b>", st_cell_c) for h in report_data.ye_march_headers]]
    for r in report_data.ye_march_summary:
        ye_data.append([Paragraph(r.metric, st_cell_l), Paragraph(r.fy_actual, st_cell_c), Paragraph(r.fy_est1, st_cell_c), Paragraph(r.fy_est2, st_cell_c)])
    ye_t = Table(ye_data, colWidths=[80, 35, 35, 35])
    ye_t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
    ]))
    left_flow.append(ye_t)

    # Right Column: Narrative & Quarterly Table
    right_flow.append(Paragraph(report_data.headline, style_headline))
    right_flow.append(Paragraph(report_data.company_description, style_body))
    
    for bullet in report_data.key_bullets:
        right_flow.append(Paragraph(f"• &nbsp; {bullet}", style_bullet))
    right_flow.append(Spacer(1, 4))

    right_flow.append(Paragraph("Outlook & Valuation", style_section))
    right_flow.append(Paragraph(report_data.outlook_valuation, style_body))
    right_flow.append(Spacer(1, 4))

    right_flow.append(Paragraph("Quarterly Financials Consolidated", style_section))
    qc_data = [[Paragraph("<b>Rs.cr</b>", st_hdr)] + [Paragraph(f"<b>{h}</b>", st_hdr) for h in report_data.quarterly_consolidated_headers]]
    for r in report_data.quarterly_consolidated_table:
        qc_data.append([
            Paragraph(r.metric, st_cell_l),
            Paragraph(r.q1_current, st_cell_c),
            Paragraph(r.q1_previous, st_cell_c),
            Paragraph(r.yoy_growth, st_cell_c),
            Paragraph(r.q4_previous, st_cell_c),
            Paragraph(r.qoq_growth, st_cell_c)
        ])
    qc_t = Table(qc_data, colWidths=[90, 52, 52, 56, 52, 57])
    qc_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GEOJIT_GREEN),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, TABLE_ALT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    right_flow.append(qc_t)

    # Assemble Page 1 Two-Column Table
    page1_grid = Table([[left_flow, right_flow]], colWidths=[190, 369])
    page1_grid.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (1, 0), (1, 0), 8),
        ('RIGHTPADDING', (0, 0), (0, 0), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(page1_grid)

    # Page 1 Break
    story.append(PageBreak())

    # ==========================================
    # PAGE 2: KEY HIGHLIGHTS & QUAD CHARTS
    # ==========================================
    story.append(Paragraph("Key highlights", style_section))
    for hl in report_data.page2_highlights:
        story.append(Paragraph(f"• &nbsp; {hl}", style_bullet))
    story.append(Spacer(1, 6))

    # Quad Chart Grid Image
    quad_buf = generate_quad_charts_page2(report_data)
    story.append(Image(quad_buf, width=559, height=280))
    story.append(Spacer(1, 8))

    # Change in Estimates Table
    story.append(Paragraph("Change in Estimates", style_section))
    est_headers = [
        Paragraph("<b>Year / Rs cr</b>", st_hdr),
        Paragraph("<b>Old FY26E</b>", st_hdr),
        Paragraph("<b>Old FY27E</b>", st_hdr),
        Paragraph("<b>New FY26E</b>", st_hdr),
        Paragraph("<b>New FY27E</b>", st_hdr),
        Paragraph("<b>Change % FY26E</b>", st_hdr),
        Paragraph("<b>Change % FY27E</b>", st_hdr)
    ]
    est_rows = [est_headers]
    for r in report_data.change_in_estimates:
        est_rows.append([
            Paragraph(r.metric, st_cell_l),
            Paragraph(r.old_fy1, st_cell_c),
            Paragraph(r.old_fy2, st_cell_c),
            Paragraph(r.new_fy1, st_cell_c),
            Paragraph(r.new_fy2, st_cell_c),
            Paragraph(r.change_fy1, st_cell_c),
            Paragraph(r.change_fy2, st_cell_c)
        ])
    est_t = Table(est_rows, colWidths=[115, 74, 74, 74, 74, 74, 74])
    est_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GEOJIT_GREEN),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, TABLE_ALT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(est_t)

    # Page 2 Break
    story.append(PageBreak())

    # ==========================================
    # PAGE 3: CONSOLIDATED FINANCIAL STATEMENTS (4 TABLES)
    # ==========================================
    story.append(Paragraph("Consolidated Financials", style_comp_title))
    story.append(Spacer(1, 4))

    def make_5y_table(title: str, rows: List[Any]) -> Table:
        hdr = [Paragraph(f"<b>{title} (Rs Cr)</b>", st_hdr)] + [Paragraph(f"<b>{h}</b>", st_hdr) for h in report_data.years_5y_headers]
        t_data = [hdr]
        for r in rows:
            t_data.append([
                Paragraph(r.metric, st_cell_l),
                Paragraph(r.fy1, st_cell_c),
                Paragraph(r.fy2, st_cell_c),
                Paragraph(r.fy3, st_cell_c),
                Paragraph(r.fy4, st_cell_c),
                Paragraph(r.fy5, st_cell_c)
            ])
        t = Table(t_data, colWidths=[120, 31, 31, 31, 31, 31])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), GEOJIT_GREEN),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, TABLE_ALT_BG]),
            ('TOPPADDING', (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ]))
        return t

    pl_table = make_5y_table("Profit & Loss", report_data.profit_loss_5y)
    bs_table = make_5y_table("Balance Sheet", report_data.balance_sheet_5y)
    cf_table = make_5y_table("Cashflow", report_data.cashflow_5y)
    ratio_table = make_5y_table("Ratio", report_data.ratios_5y)

    grid_p3 = Table([
        [pl_table, bs_table],
        [cf_table, ratio_table]
    ], colWidths=[275, 275])
    grid_p3.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(grid_p3)

    # Page 3 Break
    story.append(PageBreak())

    # ==========================================
    # PAGE 4: RECOMMENDATION TRACK RECORD & DISCLOSURES
    # ==========================================
    story.append(Paragraph("Recommendation Summary - (last 3 years)", style_section))
    
    # Rec History Chart & Table Grid
    rec_chart_buf = generate_recommendation_history_chart(report_data)
    rec_img = Image(rec_chart_buf, width=280, height=130)

    rh_headers = [Paragraph("<b>Dates</b>", st_hdr), Paragraph("<b>Rating</b>", st_hdr), Paragraph("<b>Target</b>", st_hdr)]
    rh_rows = [rh_headers]
    for rh in report_data.recommendation_history:
        rh_rows.append([Paragraph(rh.date, st_cell_c), Paragraph(rh.rating, st_cell_c), Paragraph(rh.target_price, st_cell_c)])
    rh_t = Table(rh_rows, colWidths=[90, 80, 80])
    rh_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GEOJIT_GREEN),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, TABLE_ALT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))

    story.append(Table([[rec_img, rh_t]], colWidths=[285, 274]))
    story.append(Spacer(1, 6))

    # Rating Criteria Table
    story.append(Paragraph("Investment Rating Criteria", style_section))
    matrix_data = [
        [Paragraph("<b>Ratings</b>", st_hdr), Paragraph("<b>Large caps</b>", st_hdr), Paragraph("<b>Midcaps</b>", st_hdr), Paragraph("<b>Small Caps</b>", st_hdr)],
        [Paragraph("Buy", st_cell_l), Paragraph("Upside is above 10%", st_cell_l), Paragraph("Upside is above 15%", st_cell_l), Paragraph("Upside is above 20%", st_cell_l)],
        [Paragraph("Accumulate", st_cell_l), Paragraph("-", st_cell_l), Paragraph("Upside is between 10%-15%", st_cell_l), Paragraph("Upside is between 10%-20%", st_cell_l)],
        [Paragraph("Hold", st_cell_l), Paragraph("Upside is between 0% - 10%", st_cell_l), Paragraph("Upside is between 0%-10%", st_cell_l), Paragraph("Upside is between 0%-10%", st_cell_l)],
        [Paragraph("Reduce/sell", st_cell_l), Paragraph("Downside is more than 0%", st_cell_l), Paragraph("Downside is more than 0%", st_cell_l), Paragraph("Downside is more than 0%", st_cell_l)]
    ]
    matrix_t = Table(matrix_data, colWidths=[100, 153, 153, 153])
    matrix_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GEOJIT_GREEN),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, TABLE_ALT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(matrix_t)
    story.append(Spacer(1, 6))

    # Disclosures & Regulatory Text
    story.append(Paragraph("DISCLAIMER & DISCLOSURES", ParagraphStyle('DisHead', fontName='Helvetica-Bold', fontSize=8, textColor=GEOJIT_GREEN)))
    story.append(Paragraph(report_data.disclosures_text, ParagraphStyle('DisBody', fontName='Helvetica', fontSize=6.5, leading=8.5, textColor=TEXT_MUTED)))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    
    if output_path:
        return output_path
    
    buffer.seek(0)
    return buffer.getvalue()
