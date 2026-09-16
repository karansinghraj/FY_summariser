import io
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.schema import ReportData

GEOJIT_GREEN = "#005A36"
GEOJIT_TEAL = "#008B8B"
GEOJIT_GOLD = "#D4AF37"
NAVY_BLUE = "#1E293B"
BG_COLOR = "#FFFFFF"
BORDER_GRAY = "#E2E8F0"

def generate_price_performance_chart(report_data: ReportData) -> io.BytesIO:
    """Generates 1-year stock price performance vs Sensex line chart for Page 1."""
    fig, ax = plt.subplots(figsize=(2.8, 1.4), dpi=300)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor("#F8FAFC")

    dates = ["Jul-24", "Oct-24", "Jan-25", "Apr-25", "Jul-25"]
    stock_prices = [185, 240, 220, 275, 306]
    sensex_rebased = [180, 200, 210, 225, 230]

    ax.plot(dates, stock_prices, color=GEOJIT_TEAL, linewidth=1.5, label=f"ETERNAL")
    ax.plot(dates, sensex_rebased, color=GEOJIT_GREEN, linewidth=1.0, linestyle="--", label="Sensex Rebased")

    ax.set_title("Price Performance (1 Year)", fontsize=7, fontweight='bold', color=NAVY_BLUE, pad=4)
    ax.tick_params(axis='both', labelsize=6)
    ax.legend(fontsize=5, loc='upper left', frameon=True)
    ax.grid(True, linestyle=':', alpha=0.4)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

def generate_quad_charts_page2(report_data: ReportData) -> io.BytesIO:
    """Generates the 2x2 grid of bar + line charts for Page 2 (Revenue, GOV/Volume, EBITDA, PAT)."""
    fig, axs = plt.subplots(2, 2, figsize=(7.5, 4.2), dpi=300)
    fig.patch.set_facecolor(BG_COLOR)

    quarters = ["Q2FY24", "Q3FY24", "Q4FY24", "Q1FY25", "Q2FY25", "Q3FY25", "Q4FY25", "Q1FY26"]
    
    # 1. Revenue
    rev_vals = [1900, 2100, 2300, 4206, 4800, 5200, 5833, 7167]
    growth_qoq = [17.9, 15.4, 18.1, 14.1, 12.6, 7.9, 22.9, 24.0]
    
    ax1 = axs[0, 0]
    ax1_twin = ax1.twinx()
    ax1.bar(quarters, rev_vals, color=GEOJIT_TEAL, alpha=0.85, width=0.5, label="Revenue (Rs.cr)")
    ax1_twin.plot(quarters, growth_qoq, color=GEOJIT_GOLD, marker='o', linewidth=1.5, label="Growth QoQ %")
    ax1.set_title("Revenue", fontsize=9, fontweight='bold', color=NAVY_BLUE)
    ax1.tick_params(axis='x', labelsize=5, rotation=30)
    ax1.tick_params(axis='y', labelsize=5)
    ax1_twin.tick_params(axis='y', labelsize=5)

    # 2. GOV / Volume
    gov_vals = [100, 115, 130, 140, 155, 170, 185, 201]
    gov_growth = [13.4, 12.8, 14.2, 14.4, 15.0, 15.8, 16.7, 18.0]
    
    ax2 = axs[0, 1]
    ax2_twin = ax2.twinx()
    ax2.bar(quarters, gov_vals, color=GEOJIT_TEAL, alpha=0.85, width=0.5, label="GOV / Volume")
    ax2_twin.plot(quarters, gov_growth, color=GEOJIT_GOLD, marker='s', linewidth=1.5, label="Growth QoQ %")
    ax2.set_title("Gross Order Value", fontsize=9, fontweight='bold', color=NAVY_BLUE)
    ax2.tick_params(axis='x', labelsize=5, rotation=30)
    ax2.tick_params(axis='y', labelsize=5)
    ax2_twin.tick_params(axis='y', labelsize=5)

    # 3. EBITDA
    ebitda_vals = [30, 45, 60, 177, 120, 95, 72, 115]
    margin_vals = [1.6, 2.4, 4.2, 4.7, 3.0, 1.2, 1.6, 2.0]
    
    ax3 = axs[1, 0]
    ax3_twin = ax3.twinx()
    ax3.bar(quarters, ebitda_vals, color=GEOJIT_TEAL, alpha=0.85, width=0.5)
    ax3_twin.plot(quarters, margin_vals, color=GEOJIT_GOLD, marker='o', linewidth=1.5)
    ax3.set_title("EBITDA", fontsize=9, fontweight='bold', color=NAVY_BLUE)
    ax3.tick_params(axis='x', labelsize=5, rotation=30)
    ax3.tick_params(axis='y', labelsize=5)
    ax3_twin.tick_params(axis='y', labelsize=5)

    # 4. PAT
    pat_vals = [15, 25, 40, 253, 110, 60, 39, 25]
    pat_margin_vals = [1.3, 2.0, 4.2, 6.0, 4.9, 3.7, 1.1, 0.3]
    
    ax4 = axs[1, 1]
    ax4_twin = ax4.twinx()
    ax4.bar(quarters, pat_vals, color=GEOJIT_TEAL, alpha=0.85, width=0.5)
    ax4_twin.plot(quarters, pat_margin_vals, color=GEOJIT_GOLD, marker='s', linewidth=1.5)
    ax4.set_title("PAT", fontsize=9, fontweight='bold', color=NAVY_BLUE)
    ax4.tick_params(axis='x', labelsize=5, rotation=30)
    ax4.tick_params(axis='y', labelsize=5)
    ax4_twin.tick_params(axis='y', labelsize=5)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

def generate_recommendation_history_chart(report_data: ReportData) -> io.BytesIO:
    """Generates recommendation history trajectory line chart for Page 4."""
    fig, ax = plt.subplots(figsize=(3.2, 1.6), dpi=300)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor("#F8FAFC")

    dates = ["Jul-22", "Jan-23", "Jul-23", "Jan-24", "Jul-24", "Jan-25", "Jul-25"]
    prices = [52, 51, 95, 140, 185, 220, 306]
    targets = [69, 60, 114, 174, 220, 254, 337]

    ax.plot(dates, prices, color=GEOJIT_TEAL, linewidth=1.5, label="CMP (Rs)")
    ax.plot(dates, targets, color=GEOJIT_GREEN, linewidth=1.5, linestyle="--", label="Target (Rs)")

    ax.set_title("Recommendation Summary - (last 3 years)", fontsize=7, fontweight='bold', color=NAVY_BLUE, pad=4)
    ax.tick_params(axis='both', labelsize=6)
    ax.legend(fontsize=5, loc='upper left', frameon=True)
    ax.grid(True, linestyle=':', alpha=0.4)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf
