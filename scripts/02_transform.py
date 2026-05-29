
#02_tranform.py
# convert the clean csv file to sqlite

import pandas as pd
import os

#load clean data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED = os.path.join(BASE_DIR,"data","processed")
ANALYSIS = os.path.join(BASE_DIR,"data","analysis")
os.makedirs(ANALYSIS,exist_ok=True)

df = pd.read_csv(os.path.join(PROCESSED,"funding_rounds.csv"))
df["date"] = pd.to_datetime(df["date"],errors="coerce")
df["amount_usd"] = pd.to_numeric(df["amount_usd"],errors="coerce").fillna(0)

print(f"loaded {len(df)} rows\n")

#query 1: total funding by sector
q1 = (df.groupby("sector")
        .agg(total_funding=("amount_usd","sum"),
            deal_count=("amount_usd","count"))
        .reset_index()
        .sort_values("total_funding",ascending=False))

q1.to_csv(os.path.join(ANALYSIS,"q1_funding_by_sector.csv"),index=False)
print("Q1 - Top 5 sectors by funding: ")
print(q1.head())

#q2 : total funding by city
q2 = (df.groupby("city")
        .agg(total_funding=("amount_usd","sum"),
            deal_count=("amount_usd","count"))
        .reset_index()
        .sort_values("total_funding",ascending=False))

q2.to_csv(os.path.join(ANALYSIS,"q2_funding_by_city.csv"),index=False)
print("Q2 - Top % cities by funding : ")
print(q2.head())

#q3 : funding by year
q3 = (df.groupby("year")
        .agg(total_funding=("amount_usd","sum"),
            deal_count=("amount_usd","count"))
        .reset_index()
        .sort_values("year"))

q3.to_csv(os.path.join(ANALYSIS,"q3_funding_by_year.csv"),index=False)
print("\n Q# - Funding by year : ")
print(q3.to_string(index=False))

#q4 : funding by round type
q4 = (df.groupby("round_type")
        .agg(total_funding=("amount_usd","sum"),
            deal_count=("amount_usd","count"))
        .reset_index()
        .sort_values("total_funding",ascending=False))

q4.to_csv(os.path.join(ANALYSIS,"q4_funding_by_round.csv"),index=False)
print("\n Q4 - Funding by round type : " )
print(q4.to_string(index=False))

#q5 : top 20 most funded startups
q5 = (df.groupby("startup_name")
        .agg(total_raised=("amount_usd","sum"),
             deal_count=("amount_usd","count"))
        .reset_index()
        .sort_values("total_raised",ascending=False)
        .head(20))

q5.to_csv(os.path.join(ANALYSIS,"q5_top_startups.csv"),index=False)
print("\n Q5 - Top 20 most funded startups : ")
print(q5.head(20).to_string(index=False))

#q6 - most active investors
q6 = (df["investors"]
        .str.split(",")
        .explode()
        .str.strip()
        .value_counts()
        .reset_index()
        .head(20))
q6.columns = ["investor","deals"]

q6.to_csv(os.path.join(ANALYSIS,"q6_top_investors.csv"),index=False)
print("\n Q6 - Top 10 investors by deal count : ")
print(q6.head(10).to_string(index=False))

#q7 : avg deal size  by round type

q7 = (df[df["amount_usd"]>0]
        .groupby("round_type")
        .agg(avg_deal_size=("amount_usd","mean"),
             median_deal_size=("amount_usd","median"))
        .reset_index()
        .sort_values("avg_deal_size",ascending=False))

q7.to_csv(os.path.join(ANALYSIS,"q7_avg_deal_by_round_type.csv"),index=False)
print("\n Q7 - Average Deal Size by round type : ")
print(q7.to_string(index=False))

#q8 : funding trend by sector and year

q8 = (df.groupby(["sector","year"])
        .agg(total_funding = ("amount_usd","sum"))
        .reset_index()
        .sort_values(["sector","year"]))

q8.to_csv(os.path.join(ANALYSIS,"q8_sector_year_trend.csv"),index=False)
print("\n Q8 - Sector x Year trend(sample) : ")
print(q8.head(10).to_string(index=False))

#q9 : startups with multiple rounds 
q9 = (df.groupby("startup_name")
        .agg(total_rounds=("date","count"),
             first_round=("date","min"),
             last_round=("date","max"),
             total_raised=("amount_usd","sum"))
        .reset_index()
        .query("total_rounds>1")
        .sort_values("total_rounds",ascending=False))

q9.to_csv(os.path.join(ANALYSIS,"q9_multiple_round_startups.csv"),index=False)
print("\n Q9 - Startups with most rounds : ")
print(q9.head(10).to_string(index=False))

#q10 : Risk flag ( havent raised in 18+ months)

latest_date = df["date"].max()
cutoff = latest_date - pd.DateOffset(months=18)

q10 = (df.groupby("startup_name")
        .agg(last_raise=("date","max"),
            sector=("sector","first"),
            city=("city","first"),
            total_raised=("amount_usd","sum"))
        .reset_index())
q10 = q10[q10["last_raise"] < cutoff].sort_values("last_raise")

q10.to_csv(os.path.join(ANALYSIS,"q10_risk_no_recent_raise.csv"),index=False)
print(f"\nQ10 - Startups with no raise in 18+ months : {len(q10)} flagged")
print(q10.head(10).to_string(index=False))

print("\n All queries complete. Files saved to data/analysis/")
