# 📊 Indian Startup Financial Health Dashboard

> An automated business intelligence system that ingests public Indian startup 
> funding data, scores each startup on a Financial Health metric, and generates 
> a formatted weekly briefing — the kind of tool a BA at a VC firm or CFO's 
> office would use daily.

---

## What This Does

Most startup ecosystem analysis is done manually — a BA pulling CSVs, writing 
formulas in Excel, copy-pasting into a PowerPoint. This project automates that 
entire workflow end-to-end.

**Input:** Public Indian startup funding data (Kaggle, 2015–2025)  
**Output:** Live dashboard + automated PDF weekly briefing

---

## System Architecture
Raw CSVs (3 sources)
↓
01_ingest.py       — ETL pipeline: clean, standardise, load
↓
02_transform.py    — 10 SQL-style analytical queries
↓
03_score.py        — Financial Health Scoring model (0–100)
↓
04_briefing.py     — Automated PDF report generator
↓
dashboard/app.py   — Interactive Streamlit dashboard

---

## Key Features

### Financial Health Score (0–100)
Each startup is scored on four weighted components:

| Component | Weight | Logic |
|---|---|---|
| Funding Recency | 35% | How recently did they last raise? |
| Round Momentum | 25% | Number of rounds — investor conviction signal |
| Scale | 20% | Total capital raised |
| Stage Progression | 20% | Seed → Series A → B → C = validation |

### Automated Weekly Briefing
A Python script generates a formatted PDF report every week — top movers, 
risk alerts, sector summary — with zero manual input. Simulates exactly what 
a VC research associate produces manually.

### Risk Flagging System
- 🔴 **HIGH RISK** — No raise in 24+ months
- 🟡 **MEDIUM RISK** — No raise in 18+ months  
- 👀 **WATCH** — Single round, going cold
- 🟢 **HEALTHY / STABLE** — Active funding momentum

---

## Dashboard Features
- Filter by sector, city, funding stage
- Health score leaderboard (2,493 startups scored)
- Funding trend charts (2015–2025)
- Risk distribution breakdown
- Watchlist of anomalous signals

---

## Dataset
- **Source:** Kaggle — Indian Startup Funding (Sudalai Rajkumar)
- **Coverage:** 2015–2025, 4,144 funding rounds
- **Total funding tracked:** $66.1B across 2,493 startups

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data ingestion | Python, Pandas |
| Transformation | Pandas (SQL-style aggregations) |
| Scoring model | Python — weighted business logic |
| Dashboard | Streamlit, Plotly |
| PDF generation | ReportLab |
| Database | CSV → SQLite (pipeline) |

---

## How to Run

```bash
# 1. Install dependencies
pip install pandas streamlit plotly reportlab openpyxl sqlalchemy

# 2. Add CSVs to data/raw/

# 3. Run pipeline in order
python scripts/01_ingest.py
python scripts/02_transform.py
python scripts/03_score.py
python scripts/04_briefing.py

# 4. Launch dashboard
streamlit run dashboard/app.py

# 5. PDF report appears in
reports/weekly_pulse/
```

---

## Project Structure
startup_health_systems/
├── data/
│   ├── raw/           ← source CSVs
│   ├── processed/     ← cleaned data
│   └── analysis/      ← query outputs + health scores
├── scripts/
│   ├── 01_ingest.py
│   ├── 02_transform.py
│   ├── 03_score.py
│   └── 04_briefing.py
├── dashboard/
│   └── app.py
└── reports/
└── weekly_pulse/  ← auto-generated PDFs

---

*Built as a portfolio project demonstrating end-to-end data engineering, 
SQL analytics, scoring model design, and automated reporting — 
the core skillset for a Business Analyst role at a VC firm or strategy team.*