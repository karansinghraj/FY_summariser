# Source Mapping & Extraction Guide

This document outlines how financial context documents (PDF, CSV, TXT, JSON, MD) are extracted and mapped to the **Geojit Equity Research Schema**.

## 1. Schema Mapping Overview

| Geojit Report Section | Target Field | Fallback Extraction Logic | LLM Extraction Target |
| :--- | :--- | :--- | :--- |
| **Header Banner** | `company_name` | Top text line / JSON key `company_name` | `"company_name"` |
| | `ticker` / `bse_code` | Regex `(BSE: \d+ \| NSE: \w+)` | `"ticker"`, `"bse_code"` |
| | `recommendation` | Search terms: `BUY`, `ACCUMULATE`, `HOLD`, `REDUCE`, `SELL` | `"recommendation"` |
| | `target_price` | Regex `Target Price:? (₹?[\d,]+)` | `"target_price"` |
| | `cmp` | Regex `(CMP\|Current Price):? (₹?[\d,]+)` | `"cmp"` |
| **Key Metadata** | `market_cap`, `52W H/L` | Regex patterns `Market Cap`, `52 Wk High` | `"market_cap"`, `"fifty_two_week_high_low"` |
| **Executive Summary** | `executive_summary` | Summary section text or intro paragraph | `"executive_summary"` |
| **Key Highlights** | `key_highlights` | Bullet points or key metrics lines | `"key_highlights"` (Array of strings) |
| **Quarterly Table** | `quarterly_financials` | Table rows matching Q1/Q2/Q3/Q4 pattern | `"quarterly_financials"` (List of objects) |
| **Annual Statements** | `income_statement`, `balance_sheet`, `cash_flow`, `key_ratios` | Financial statement rows or historical JSON tables | `"income_statement"`, `"balance_sheet"`, `"cash_flow"`, `"key_ratios"` |
| **Recommendation History**| `recommendation_history` | Historical rating table or default current entry | `"recommendation_history"` |

## 2. Missing Fields Handling
When any financial metric (e.g. Target Price, 52W High/Low, or specific ratios) is missing in the source context:
- The system gracefully assigns `—` (em-dash).
- The template formats missing values cleanly without breaking table alignment.
