# Vendor Performance Analysis

Engineered an end-to-end data analytics project that imported retail and inventory data into a database, analyzed sales and purchase data, performed data analysis using Python, and created an interactive Power BI dashboard.

## Objective

Retail and inventory data (purchases, sales, vendor invoices, and pricing) is spread across multiple raw tables. This project consolidates that data to answer key business questions:

- Which vendors and brands drive the most sales and profit?
- Which brands have low sales but high profit margins (candidates for pricing/promotion changes)?
- Does bulk purchasing reduce unit cost, and what's the optimal order size?
- Which vendors are sitting on slow-moving inventory / locked-up capital?
- Is there a statistically significant difference in profit margins between top- and low-performing vendors?

## Tech Stack

- **Python**: `pandas`, `numpy`, `sqlalchemy`, `sqlite3`
- **Statistics**: `scipy.stats` (t-tests, confidence intervals)
- **Visualization**: `matplotlib`, `seaborn`
- **Database**: SQLite (`inventory.db`)
- **BI / Dashboarding**: Power BI (`.pbix`)
- **Logging**: Python `logging` module

## Project Workflow

### 1. Data Ingestion (`ingestion_db.py`, `csv_to_db.ipynb`)
Raw CSV files (purchases, purchase prices, vendor invoices, sales, etc.) are loaded and ingested into a local SQLite database (`inventory.db`) using a reusable `ingest_db()` function built on SQLAlchemy. Every ingestion run is logged (timestamps, table names, total run time) to `logs/ingestion_db.log` for traceability.

### 2. Exploratory Data Analysis & Summary Table Creation (`EDA.ipynb`)
- Connected to `inventory.db` and profiled every table (row counts, sample records) to understand schema and relationships across `purchases`, `purchase_prices`, `vendor_invoice`, and `sales`.
- Since the required metrics were spread across multiple tables, wrote an optimized CTE-based SQL query to join and pre-aggregate:
  - Purchase transactions (quantity, dollars, purchase price) per vendor/brand
  - Sales transactions (quantity, dollars, price, excise tax) per vendor/brand
  - Freight costs per vendor
  - Actual vendor product pricing
- Pre-aggregating this into a single **`vendor_sales_summary`** table avoids expensive repeated joins on large tables and speeds up downstream analysis and dashboarding.

- **Data cleaning**: fixed data types (e.g. `volume` to float), handled nulls, stripped whitespace from vendor names, and removed inconsistent records.
- **Feature engineering** — derived new business metrics:
  - `GrossProfit` = Total Sales $ − Total Purchase $
  - `ProfitMargin` = Gross Profit / Total Sales $
  - `StockTurnOver` = Sales Quantity / Purchase Quantity
  - `SalesToPurchaseRatio` = Total Sales $ / Total Purchase $

- Persisted the final cleaned & enriched table back into the database as `vendor_sales_summary`.

### 3. Vendor Performance Analysis (`Vendor_Performance_Analysis.ipynb`)
- Loaded `vendor_sales_summary` and ran summary statistics, distribution plots, and box plots to detect outliers and invalid records (e.g. negative gross profit, zero sales).
- Filtered out invalid rows (`GrossProfit`, `ProfitMargin`, `TotalSalesQt` ≤ 0) to get a clean analysis base.
- Built a correlation heatmap to understand relationships between pricing, purchases, and profitability.
- **Analysis performed:**
  - Identified brands with **low sales but high profit margins** (bottom 15th percentile sales, top 85th percentile margin) — strong candidates for promotional or pricing adjustments.
  - Ranked **top 10 vendors and brands by sales revenue**.
  - Calculated each vendor's **contribution to total purchase spend**, including cumulative contribution (Pareto-style analysis) to assess dependency risk on top vendors.
  - Analyzed **bulk purchasing impact**: bucketed orders into Small/Medium/Large by quantity and compared average unit purchase price — bulk orders showed a substantial (~72%) reduction in unit cost.
  - Identified vendors with the **lowest inventory (stock) turnover**, signaling excess/slow-moving stock.
  - Quantified **capital locked in unsold inventory** per vendor.
  - Computed **95% confidence intervals** for profit margins of top-performing vs. low-performing vendors.
  - Ran a **two-sample t-test** comparing profit margins of top vs. low vendors.

### 4. Power BI Dashboard (`PowerBI_Dashboard.pbix`, `PowerBI_Dashboard.pbix`)
The final `vendor_sales_summary` table (exported to `vendor_sales_summary.csv`) was used to build an interactive Power BI dashboard for stakeholders to explore vendor sales, purchase contribution, profit margins, and inventory metrics without touching code.

## Key Findings

- **Low-selling vendors earn better profits**: A statistical test showed that vendors with lower sales often have higher profit margins than top-selling vendors. This may be because they sell premium products or have lower operating costs.
- **Buying in bulk reduces costs**: Vendors who purchase products in large quantities usually get lower prices per unit, helping improve profitability.
- **High dependence on a few vendors**: A small number of vendors account for most of the company's purchase spending, which can be risky if one of them faces supply issues.
- **Inventory Inefficiencies**: A significant amount of money is invested in products that have not yet been sold, especially for certain vendors.
- **Opportunity to increase sales**: Some brands have high profit margins but low sales. Promoting these products could increase profits without reducing prices.

## Repository Structure

```
├── logs/
│   └── ingestion_db.log               # Auto-generated ingestion logs
    └── get_vendor_summary.log         # Auto-Creation and Cleaning of Vendor Summary Table 
├── ingestion_db.py                    # Script: CSV -> SQLite ingestion
├── csv_to_db.ipynb                    # Notebook version of the ingestion step
├── EDA.ipynb                          # DB exploration, SQL aggregation, vendor_sales_summary creation
├── Vendor_Performance_Analysis.ipynb  # EDA, business analysis, hypothesis testing
├── vendor_sales_summary.csv           # Exported summary table (used for Power BI)
├── PowerBI_Dashboard.pbix             # Interactive Power BI dashboard
├── PowerBI_Dashboard.pdf              # PDF file of Power BI dashboard
└── README.md
```

## Future Improvements

- Set up the ingestion step to run automatically on a schedule, instead of running it by hand each time.
- Replace SQLite with a database like PostgreSQL or Snowflake to handle larger amounts of data more efficiently.
- Add checks that catch bad or missing data before it gets loaded in.
- Extend the Power BI dashboard with drill-through vendor/brand pages and forecasting.

## Dataset

Kaggle Dataset: [Vendor Performance Dataset](https://www.kaggle.com/datasets/vivekkumarkamat/vendor-performance-analysis)

### Files Included:
- purchases.csv
- sales.csv
- begin_inventory.csv
- end_inventory.csv
- purchase_prices.csv
- vendor_invoice.csv

## Author

**Ayush Kumar**
- GitHub: [RoshniKumari26](https://github.com/RoshniKumari26)
- LinkedIn: [roshnikumari2604](https://linkedin.com/in/roshnikumari2604)


