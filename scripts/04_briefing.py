#04_briefing.py

import pandas as pd
import os
from datetime import datetime
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph , Spacer, Table, TableStyle, HRFlowable)

#paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(BASE_DIR,"data","analysis")
REPORTS = os.path.join(BASE_DIR,"reports","weekly_pulse")
os.makedirs(REPORTS,exist_ok=True)

#load data
scores = pd.read_csv(os.path.join(ANALYSIS,"health_scores.csv"))
sectors = pd.read_csv(os.path.join(ANALYSIS,"q1_funding_by_sector.csv"))
cities = pd.read_csv(os.path.join(ANALYSIS,"q2_funding_by_city.csv"))
rounds = pd.read_csv(os.path.join(ANALYSIS,"q4_funding_by_round.csv"))

#report date
today = datetime.today().strftime("%B %d %Y")
filename = datetime.today().strftime("pulse_%Y_%m_%d.pdf")
OUT_PATH = os.path.join(REPORTS,filename)

#Styles
styles = getSampleStyleSheet()

DARK = colors.HexColor("#0D1117")
ACCENT = colors.HexColor("#2563EB")
GREEN = colors.HexColor("#16A34A")
RED = colors.HexColor("#DC3636")
AMBER = colors.HexColor("#D97706")
LIGHT = colors.HexColor("#F8FAFC")
GREY = colors.HexColor("#64748B")

title_style = ParagraphStyle("title",
                             fontSize=22, fontName='Helvetica-Bold',
                             textColor=DARK, spaceAfter=12)

subtitle_style = ParagraphStyle("subtitle",
                                fontSize=10, fontName="Helvetica",
                                textColor=GREY, spaceAfter=20)

section_style = ParagraphStyle("section",
                               fontSize=13, fontName="Helvetica-Bold",
                               textColor=ACCENT, spaceAfter=8, spaceBefore=16)

body_style = ParagraphStyle("body",
                            fontSize=9, fontName='Helvetica',
                            textColor=DARK, spaceAfter=4,leading=14)

kpi_label_style = ParagraphStyle("kpi_label",
                                 fontSize=8, fontName="Helvetica",
                                 textColor=GREY, spaceAfter=2)

kpi_value_style = ParagraphStyle("kpi_value",
                                 fontSize=18, fontName="Helvetica-Bold",
                                 textColor=DARK, spaceAfter=4)


#helper : table style

def base_table_style(header_color=ACCENT):
    return TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), header_color),
        ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,0), 8),
        ("FONTNAME",   (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",   (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS",   (0,0), (-1,-1), [colors.white,LIGHT]),
        ("GRID",   (0,0), (-1,-1),0.3, colors.HexColor("#E2E8F0")),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",   (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("RIGHTPADDING",   (0,0), (-1,-1), 6),
        ("VALIGN",   (0,0), (-1,-1), "MIDDLE"),
    ])

#build content
story = []
W =A4[0] - 4*cm 

#header
story.append(Paragraph("Weekly Startup Pulse",title_style))
story.append(Spacer(1,6))
story.append(Paragraph(f"Indian Startup Ecosystem Intelligence Report : {today}",subtitle_style))
story.append(HRFlowable(width="100%",thickness=1.5, color=ACCENT))
story.append(Spacer(1,12))

#KPI SUMMARY ROW
total_startups = len(scores)
total_funding = scores["total_raised"].sum()
avg_score = scores["health_score"].mean()
high_risk_count = len(scores[scores["risk_flag"].str.contains("HIGH RISK", na=False)])
healthy_count = len(scores[scores["risk_flag"]=="HEALTHY"])

kpi_data = [[
    Paragraph("TOTAL STARTUPS TRACKED", kpi_label_style),
    Paragraph("TOTAL FUNDING (USD)", kpi_label_style),
    Paragraph("AVG HEALTH SCORE", kpi_label_style),
    Paragraph("HIGH RISK FLAGS", kpi_label_style),
],[
    Paragraph(f"{total_startups:,}", kpi_value_style),
    Paragraph(f"${total_funding/1e9:.1f}B", kpi_value_style),
    Paragraph(f"{avg_score:.1f}/100",kpi_value_style),
    Paragraph(f'{high_risk_count:,}',kpi_value_style),
]]

kpi_table = Table(kpi_data,colWidths=[W/4]*4)
kpi_table.setStyle(TableStyle([
    ("BOX",     (0,0),(-1,-1),0.5,colors.HexColor("#E2E8F0")),
    ("LINEBELOW",     (0,0),(-1,0),0.5,colors.HexColor("#E2E8F0")),
    ("BACKGROUND",     (0,0),(-1,-1),LIGHT),
    ("TOPPADDING",     (0,0),(-1,-1),8),
    ("BOTTOMPADDING",     (0,0),(-1,-1),8),
    ("LEFTPADDING",     (0,0),(-1,-1),10),
    ("ALIGN",     (0,0),(-1,-1),"LEFT"),
]))
story.append(kpi_table)
story.append(Spacer(1,16))

#Section 1 : top movers
story.append(Paragraph("Top 10 Healthiest Startups", section_style))
story.append(Paragraph(
    'Startups ranked by Financial health Score - combining funding recency,'
    "round momentum, total scale, and stage progression.",body_style
))

top10 = scores.sort_values("health_score",ascending = False).head(10)
top10_data = [["#","Startup","Sector","City","Health Score","Stage","Status"]]
for i, (_, row) in enumerate(top10.iterrows(),1):
    top10_data.append([
        str(i),
        str(row["startup_name"])[:25],
        str(row["sector"])[:20],
        str(row["city"])[:15],
        f"{row['health_score']:.1f}",
        str(row["latest_round"]),
        str(row["risk_flag"])[:15],
    ])

top10_table = Table(top10_data, colWidths=[0.5*cm, 4*cm , 3.5*cm, 2.5*cm, 2*cm, 2.5*cm, 2*cm])
top10_table.setStyle(base_table_style(GREEN))
story.append(top10_table)
story.append(Spacer(1,16))

#section 2 : risk alerts

story.append(Paragraph("Risk Alerts - High Priority Watchlist", section_style))
story.append(Paragraph(
    "Startups flagged as HIGH RISK : no funding raise in 24+ months despite"
    "significant capital raised. These warrant immediate attention.",body_style
))

high_risk = (scores[scores["risk_flag"].str.contains("HIGH RISK", na=False)]
             .sort_values("total_raised",ascending=False)
             .head(10))

risk_data = [["Startup","Sector","Total Raised","Last Raised","Months Idle","Risk"]]
for _,row in high_risk.iterrows():
    risk_data.append([
        str(row["startup_name"])[:25],
        str(row["sector"])[:20],
        f"${row["total_raised"]/1e6:.1f}",
        str(row["last_raise"])[:10],
        f"{row["months_since_raise"]:0f}",
        "HIGH RISK"
    ])

risk_table = Table(risk_data, colWidths=[4*cm, 3.5*cm, 2.5*cm, 2.5*cm, 2*cm, 2*cm])
risk_table.setStyle(base_table_style(RED))
story.append(risk_table)
story.append(Spacer(1,16))

#section 3: sector summary

story.append(Paragraph("City-wise Funding Distribution", section_style))

city_data = [["Rank", "City", "Total Funding", "Deal Count", "% of Total"]]
total_city_funding = cities["total_funding"].sum()
for i, (_, row) in enumerate(cities.head(8).iterrows(), 1):
    pct = row["total_funding"] / total_city_funding * 100
    city_data.append([
        str(i),
        str(row["city"]),
        f"${row['total_funding']/1e9:.2f}B",
        str(int(row["deal_count"])),
        f"{pct:.1f}%",
    ])

city_table = Table(city_data, colWidths=[1*cm, 4*cm, 3.5*cm, 2.5*cm, 3*cm])
city_table.setStyle(base_table_style(ACCENT))
story.append(city_table)
story.append(Spacer(1, 16))

#section 5 : risk distribution

story.append(Paragraph("Portfolio Risk Distribution",section_style))

risk_dist = scores["risk_flag"].value_counts().reset_index()
risk_dist.columns = ["Risk Category","Count"]
risk_dist["% of Portfolio"] = (risk_dist["Count"]/ len(scores) *100).round(1)

rd_data = [["Risk Category", "Startup Count", "% of Portfolio"]]
for _, row in risk_dist.iterrows():
    rd_data.append([
        str(row["Risk Category"]),
        str(row["Count"]),
        f"{row['% of Portfolio']}%",
    ])

rd_table = Table(rd_data, colWidths=[8*cm, 4*cm, 4*cm])
rd_table.setStyle(base_table_style(AMBER))
story.append(rd_table)
story.append(Spacer(1,20))

#footer
story.append(HRFlowable(width="100%", thickness = 0.5, color= GREY))
story.append(Spacer(1,6))
story.append(Paragraph(
    f"Generated automatically by Startup Financial Health Intelligence System  . {today}  . "
    f"Data : Kaggle Indian Startup Funding Datasets 2015-2025",
    ParagraphStyle("footer", fontSize= 7, textColor=GREY, alignment =1)
))

#build pdf

doc= SimpleDocTemplate(
    OUT_PATH,
    pagesize =A4,
    leftMargin=2*cm,rightMargin=2*cm,
    topMargin=2*cm,bottomMargin=2*cm
)
doc.build(story)

print(f" Weekly Pulse report generated: ")
print(f" {OUT_PATH}")