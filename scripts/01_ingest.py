#01_ingest.py 
# PURPOSE : Read all three csv files , cclean them and load them into database sqlite

import pandas as pd
import sqlite3
import os
import pathlib

# setting up paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA = os.path.join(BASE_DIR,"data" , "raw")
DB_PATH = os.path.join(BASE_DIR,"database","startups.db")

#  loading 3 CSV's
df_old = pd.read_csv(os.path.join(RAW_DATA,"startup_funding_15-19.csv"),encoding="utf-8-sig")
df_new = pd.read_csv(os.path.join(RAW_DATA,"startup_funding_20-25.csv"), encoding= "utf-8-sig")
df_co = pd.read_excel(os.path.join(RAW_DATA,"India_startup_details.xlsx"))

df_old.columns = df_old.columns.str.strip()
df_new.columns = df_new.columns.str.strip()

#standardize column names in all csvs

RENAME_MAP = { 
    "Startup Name" : "startup_name",
    "Startup"      : "startup_name",

    "Date dd/mm/yyyy" : "date",
    "Date"            : "date",

    "Industry Vertical" : "sector",
    "Industry"          : "sector",

    "SubVertical" : "sub_sector",

    "City  Location" : "city",
    "City"           : "city",

    "Investors Name" : "investors",
    "Investors"      : "investors",

    "InvestmentnType" : "round_type",
    "InvestmentType"  : "round_type",

    "Amount in USD"        : "amount_usd",
    "InvestmentAmount_USD" : "amount_usd",

}

df_old = df_old.rename(columns = RENAME_MAP)
df_new = df_new.rename(columns=RENAME_MAP)

# KEEPING ONLY REQUIRED COLUMNS ON
KEEP_COLS = ["startup_name","date","sector","sub_sector","city","investors","round_type","amount_usd"]

# ONLY KEEPING COLUMNS THAT EXISTS IN EACH DATAFRAME
df_old = df_old[[c for c in KEEP_COLS if c in df_old.columns]]
df_new = df_new[[c for c in KEEP_COLS if c in df_new.columns]]

# COMBINING BOTH FUNDING DATASETS TOGETHER
df_funding = pd.concat([df_old,df_new],ignore_index=True)
print("Columns after concat:", df_funding.columns.tolist())
print(f" Combined funding rows: {len(df_funding)}")

# CLEANING DATA
df_funding["startup_name"] = (df_funding["startup_name"]
                              .astype(str)
                              .str.strip()
                              .str.title())

df_funding["date"] = pd.to_datetime(df_funding["date"],
                                    dayfirst=True,
                                    errors="coerce")

df_funding["amount_usd"] = (df_funding["amount_usd"]
                            .astype(str)
                            .str.replace(",","",regex = False)
                            .str.replace("$","",regex = False)
                            .str.replace("undisclosed","0",case=False,regex=False)
                            .str.strip())
df_funding["amount_usd"] = pd.to_numeric(df_funding["amount_usd"],errors="coerce").fillna(0)

ROUND_MAP = {
    "seed funding"  : "Seed",
    "seed"          : "Seed",
    "seed"          : "Seed",
    "seed funding"  : "Seed",
    "angel"         : "Seed",
    "angel funding" : "Seed",
    "series a"      : "Series A",
    "series b"      : "Series B",
    "series c"      : "Series C",
    "series d"      : "Series D",
    "series e"      : "Series E",
    "pre-series a"  : "Pre-Series A",
    "pre series a"  : "Pre-Series B",
    "debt"          : "Debt",
    "venture"       : "Venture",
    "private equity": "Private Equity",

}
df_funding["round_type"] = (df_funding['round_type']
                            .astype(str)
                            .str.strip()
                            .str.lower()
                            .map(ROUND_MAP)
                            .fillna("Other"))

df_funding = df_funding[df_funding["startup_name"].notna()] #removing rows with no name
df_funding = df_funding[df_funding["startup_name"] != "Nan"]

df_funding["year"] = df_funding["date"].dt.year
df_funding["month"] = df_funding["date"].dt.month

CITY_MAP = {
    "Bangalore"  : "Bengaluru",
    "Banglore"   : "Bengaluru",
    "New Delhi"  : "Delhi",
    "Gurugram"   : "Gurgaon",
}
df_funding["city"] = df_funding["city"].replace(CITY_MAP)

#load into sqlite
print("Writing to files...")

import os
PROCESSED = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROCESSED, exist_ok=True)

df_funding.to_csv(os.path.join(PROCESSED, "funding_rounds.csv"), index=False)
df_co.to_csv(os.path.join(PROCESSED, "company_profiles.csv"), index=False)

print("Done!")
print(f"  funding_rounds : {len(df_funding)} rows")
print(f"  company_profiles : {len(df_co)} rows")
print(f"  Files saved to: {PROCESSED}")

