import pandas as pd
import os
from datetime import datetime

#load data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED = os.path.join(BASE_DIR,"data","processed")
ANALYSIS =os.path.join(BASE_DIR,"data","analysis")

df= pd.read_csv(os.path.join(PROCESSED,"funding_rounds.csv"))
df["date"]=pd.to_datetime(df["date"],errors="coerce")
df["amount_usd"]=pd.to_numeric(df["amount_usd"],errors="coerce").fillna(0)

#1.build one row per startup

REFERENCE_DATE = df["date"].max()
startup = (df.groupby("startup_name")
            .agg(
               sector    = ("sector",   "first"),
               city      = ("city",     "first"),
               total_raised = ("amount_usd",    "sum"),
               total_rounds =("date",   "count"),
               first_raise=("date",    "min"),
               last_raise=("date",  "max"),
               avg_round =("amount_usd",    "mean"),
            )
            .reset_index())

#2. Calculate raw signals

startup["months_since_raise"]=(
    (REFERENCE_DATE-startup["last_raise"])/pd.Timedelta(days=30)
).round(1)

startup["funding_lifespan_months"]=(
    (startup["last_raise"]-startup['first_raise'])/pd.Timedelta(days=30)
).round(1)

STAGE_MAP = {
    "Angel"     : 1,
    "Pre-Series A": 2,
    "Seed"      : 2,
    "Series A"  : 3,
    "Series B"  : 4,
    "Series C"  : 5,
    "Series D"  : 6,
    "Series E"  : 7,
    "Private Equity" : 6,
    "Debt"      : 4,
    "Venture"   : 3,
    "Other"     : 2,
}

latest_round = (df.sort_values("date")
                    .groupby("startup_name")["round_type"]
                    .last()
                    .reset_index())
latest_round.columns = ["startup_name","latest_round"]
startup = startup.merge(latest_round, on="startup_name",how="left")
startup["stage_score"] = startup["latest_round"].map(STAGE_MAP).fillna(1)

def normalise(series,reverse=False):
    """Scale any series to 0-100. Reverse=True means lower raw = higher score"""
    mn, mx = series.min(),series.max()
    if mx == mn :
        return pd.Series([50]*len(series),index=series.index)
    scaled = (series - mn)/(mx-mn)*100
    return (100 - scaled) if reverse else scaled

startup["recency_score"] = normalise(startup["months_since_raise"],reverse=True)

startup["momentum_score"] = normalise(startup["total_rounds"])

startup["scale_score"] = normalise(startup["total_raised"])

startup["stage_score_norm"] = normalise(startup["stage_score"])

#4.weighted final score
# Recency = 35% (dead startups stop raising)
# Momentum = 25% (multiple rounds = investor conviction)
# Scale    = 20% (absolute size matters)
# Stage    = 20% (Series B > Seed all else equal)

startup["health_score"] = (
    startup["recency_score"]*0.35 +
    startup["momentum_score"]*0.25 +
    startup["scale_score"]*0.20 +
    startup["stage_score_norm"]*0.20
).round(1)

#5.assign risk flags

def risk_flag(row):
    if row["months_since_raise"] > 24:
        return "HIGH RISK - No raise in 24+ months"
    elif row["months_since_raise"] > 18:
        return "MEDIUM RISK - No raise in 18+ months"
    elif row["total_rounds"] == 1 and row["months_since_raise"]>12:
        return "WATCH - Single round, going cold"
    elif row["health_score"]>=70:
        return "HEALTHY"
    elif row["health_score"]>=40:
        return "STABLE"
    else:
        return "WEAK"
    
startup["risk_flag"] = startup.apply(risk_flag,axis=1)

#6.save results

output_cols= [
    "startup_name", "sector" , "city",
    "total_raised" , "total_rounds","latest_round",
    "last_raise","months_since_raise",
    "recency_score","momentum_score","scale_score","stage_score_norm",
    "health_score","risk_flag"
]

result = startup[output_cols].sort_values("health_score", ascending=False)
result.to_csv(os.path.join(ANALYSIS,"health_scores.csv"),index=False)

#7.print summary

print("=" * 60)
print("STARTUP FINANCIAL HEALTH SCORES")
print("="*60)

print("\n TOP 10 HEALTHIEST STARTUPS :")
print(result[["startup_name","sector","health_score","months_since_raise","risk_flag"]].to_string(index=False))

print("\n RISK DISTRIBUTION :")
print(result["risk_flag"].value_counts().to_string())

print(f"\n Scores saved to data/analysis/health_scores.csv")
print(f" Total startups scored: {len(result)}")
      
      
