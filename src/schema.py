from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class QuarterlyMetric(BaseModel):
    quarter: str = Field(..., description="Quarter name e.g. Q2FY26, Q2FY25, Q1FY26")
    revenue: str = Field("—", description="Revenue / Total Income (in Rs. Mn or Bn)")
    ebitda: str = Field("—", description="EBITDA / Core Operating Profit")
    ebitda_margin: str = Field("—", description="EBITDA Margin % / Operating Margin %")
    pat: str = Field("—", description="Profit After Tax (PAT)")
    pat_margin: str = Field("—", description="PAT Margin %")
    eps: str = Field("—", description="Earnings Per Share (EPS)")
    extra_metric: Optional[str] = Field("—", description="Banking metric e.g. NIM / GNPA % if applicable")

class AnnualFinancialRow(BaseModel):
    metric: str
    year_1: str = "—"
    year_2: str = "—"
    year_3: str = "—"
    year_4: str = "—"

class RecHistoryRow(BaseModel):
    date: str
    rating: str
    target_price: str = "—"
    cmp: str = "—"

class ReportData(BaseModel):
    company_name: str = "Company Name"
    ticker: str = "TICKER"
    sector: str = "Diversified"
    recommendation: str = "NOT RATED"
    target_price: str = "—"
    cmp: str = "—"
    upside_downside: str = "—"
    market_cap: str = "—"
    fifty_two_week_high_low: str = "—"
    shares_outstanding: str = "—"
    bse_code: str = "—"
    nse_code: str = "—"
    bloomberg_code: str = "—"
    report_date: str = "September 2026"
    analyst_name: str = "Research Analyst"
    is_banking: bool = False

    # Narrative Content
    executive_summary: str = "Executive summary not provided."
    key_highlights: List[str] = Field(default_factory=list)
    outlook: str = "Outlook summary not provided."
    estimate_change_notes: str = "No changes to estimates."

    # Tables & Structured Financials
    quarterly_financials: List[QuarterlyMetric] = Field(default_factory=list)
    income_statement: List[AnnualFinancialRow] = Field(default_factory=list)
    balance_sheet: List[AnnualFinancialRow] = Field(default_factory=list)
    cash_flow: List[AnnualFinancialRow] = Field(default_factory=list)
    key_ratios: List[AnnualFinancialRow] = Field(default_factory=list)
    recommendation_history: List[RecHistoryRow] = Field(default_factory=list)

    # Disclosures
    disclosures: str = (
        "Geojit Financial Services Ltd. (GFSL) is a SEBI registered Research Analyst. "
        "This report is prepared for informational purposes only and does not constitute an offer to buy or sell securities. "
        "Opinions expressed are subject to change without notice. GFSL and its affiliates may have positions in the securities mentioned."
    )
