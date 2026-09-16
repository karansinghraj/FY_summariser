from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ShareholdingRow(BaseModel):
    category: str
    q1: str = "—"
    q2: str = "—"
    q3: str = "—"

class PricePerfRow(BaseModel):
    period: str
    absolute_return: str = "—"
    sensex_return: str = "—"
    relative_return: str = "—"

class YEMarchSummaryRow(BaseModel):
    metric: str
    fy_actual: str = "—"
    fy_est1: str = "—"
    fy_est2: str = "—"

class QuarterlyConsolidatedRow(BaseModel):
    metric: str
    q1_current: str = "—"
    q1_previous: str = "—"
    yoy_growth: str = "—"
    q4_previous: str = "—"
    qoq_growth: str = "—"

class EstimateChangeRow(BaseModel):
    metric: str
    old_fy1: str = "—"
    old_fy2: str = "—"
    new_fy1: str = "—"
    new_fy2: str = "—"
    change_fy1: str = "—"
    change_fy2: str = "—"

class Statement5YRow(BaseModel):
    metric: str
    fy1: str = "—"
    fy2: str = "—"
    fy3: str = "—"
    fy4: str = "—"
    fy5: str = "—"

class RecHistoryRow(BaseModel):
    date: str
    rating: str
    target_price: str = "—"
    cmp: str = "—"

class ReportData(BaseModel):
    # Header Metadata
    company_name: str = "Eternal Ltd."
    ticker: str = "ETERNAL"
    sector: str = "Internet & Catalogue Retail"
    report_date: str = "29th July, 2025"
    result_update_period: str = "Q1FY26 Result Update"
    recommendation: str = "HOLD"
    rating_change: str = "DOWNGRADE"  # UPGRADE, NO_CHANGE, DOWNGRADE
    target_change: str = "DOWN"       # UP, DOWN, NO_CHANGE
    earnings_change: str = "DOWN"     # UP, DOWN, NO_CHANGE
    target_price: str = "Rs. 337"
    cmp: str = "Rs. 306"
    return_pct: str = "+10%"
    stock_type: str = "Large Cap"
    bloomberg_code: str = "ETERNAL:IN"
    sensex: str = "81,334"
    nse_code: str = "ETERNAL"
    bse_code: str = "543320"
    time_frame: str = "12 Months"
    data_as_of: str = "29-July-2025, 16:23hrs"
    analyst_name: str = "Gopika Gopan"
    is_banking: bool = False

    # Left Column Sidebar Tables (Page 1)
    market_cap_cr: str = "295,735"
    fifty_two_wk_high_low: str = "314 - 190"
    enterprise_value_cr: str = "294,166"
    shares_outstanding_cr: str = "965.0"
    free_float_pct: str = "71.9"
    dividend_yield_pct: str = "—"
    six_m_avg_vol_cr: str = "6.1"
    beta: str = "1.0"
    face_value_rs: str = "1.0"

    shareholding_headers: List[str] = Field(default_factory=lambda: ["Q3FY25", "Q4FY25", "Q1FY26"])
    shareholding_table: List[ShareholdingRow] = Field(default_factory=list)

    price_perf_table: List[PricePerfRow] = Field(default_factory=list)

    ye_march_headers: List[str] = Field(default_factory=lambda: ["FY25A", "FY26E", "FY27E"])
    ye_march_summary: List[YEMarchSummaryRow] = Field(default_factory=list)

    # Page 1 Main Right Column Content
    headline: str = "Blinkit propels growth; valuation limits upside"
    company_description: str = (
        "Eternal Limited, formerly Zomato Limited, operates as an online food delivery company. "
        "It runs a B2C platform under the Zomato brand. The company also operates Hyperpure and Blinkit, "
        "organises events, provides payment services and engages in investment activities."
    )
    key_bullets: List[str] = Field(default_factory=list)
    outlook_valuation: str = "Eternal Limited is poised for long-term growth and improved profitability..."
    quarterly_consolidated_headers: List[str] = Field(default_factory=lambda: ["Q1FY26", "Q1FY25", "YoY Growth (%)", "Q4FY25", "QoQ Growth (%)"])
    quarterly_consolidated_table: List[QuarterlyConsolidatedRow] = Field(default_factory=list)

    # Page 2 Detailed Content
    page2_highlights: List[str] = Field(default_factory=list)
    change_in_estimates: List[EstimateChangeRow] = Field(default_factory=list)

    # Page 3 5-Year Consolidated Statements (FY23A to FY27E)
    years_5y_headers: List[str] = Field(default_factory=lambda: ["FY23A", "FY24A", "FY25A", "FY26E", "FY27E"])
    profit_loss_5y: List[Statement5YRow] = Field(default_factory=list)
    balance_sheet_5y: List[Statement5YRow] = Field(default_factory=list)
    cashflow_5y: List[Statement5YRow] = Field(default_factory=list)
    ratios_5y: List[Statement5YRow] = Field(default_factory=list)

    # Page 4 Track Record & Disclosures
    recommendation_history: List[RecHistoryRow] = Field(default_factory=list)
    disclosures_text: str = (
        "Certification: I, Gopika Gopan, author of this Report, hereby certify that all the views expressed in this research report "
        "reflect our personal views about any or all of the subject issuer or securities. "
        "Geojit Investments Ltd (GIL) / Geojit Financial Services Ltd. (GFSL) is a SEBI registered Research Entity (INH000019567)."
    )
