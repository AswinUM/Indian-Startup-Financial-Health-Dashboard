# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os

#page config
st.set_page_config(
    page_title = "Startup Financial Health System",
    page_icon=" ",
    layout="wide"
)

#Load data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(BASE_DIR,"data","analysis")

@st.cache_data
def load_data():
    scores =pd.read_csv(os.path.join(ANALYSIS,"health_scores.csv"))
    funding=pd.read_csv(os.path.join(ANALYSIS,"q3_funding_by_year.csv"))
    sectors=pd.read_csv(os.path.join(ANALYSIS,"q1_funding_by_sector.csv"))
    cities=pd.read_csv(os.path.join(ANALYSIS,"q2_funding_by_city.csv"))
    rounds=pd.read_csv(os.path.join(ANALYSIS,"q4_funding_by_round.csv"))
    return scores,funding,sectors,cities,rounds

scores,funding,sectors,cities,rounds = load_data()

#sidebar filter
st.sidebar.title("  filters")

all_sectors = ["All"]+ sorted(scores["sector"].dropna().unique().tolist())
selected_sector = st.sidebar.selectbox("Sector",all_sectors)

all_cities = ["All"]+ sorted(scores["city"].dropna().unique().tolist())
selected_city = st.sidebar.selectbox("City",all_cities)

all_stages = ["All"]+ sorted(scores["latest_round"].dropna().unique().tolist())
selected_stage = st.sidebar.selectbox("Funding Stage",all_stages)

score_range=st.sidebar.slider("Health Score Range",0,100,(0,100))

#apply filters
filtered = scores.copy()
if selected_sector !="All":
    filtered = filtered[filtered["sector"]== selected_sector]
if selected_city !="All":
    filtered = filtered[filtered["city"]== selected_city]
if selected_stage !="All":
    filtered= filtered[filtered["latest_round"]== selected_stage]
filtered=filtered[
    (filtered["health_score"]>=score_range[0])&
    (filtered["health_score"]<=score_range[1])
]

#header
st.title(" Startup Financial Health Intelligence System")
st.caption("Indian Startup ecosystem analysis - funding data 2015-2025")

#kpi  cards
col1,col2,col3,col4 = st.columns(4)
col1.metric("Total Startups",f"{len(filtered):,}")
col2.metric("Total Funding",f"${filtered['total_raised'].sum()/1e9:.1f}B")
col3.metric("Avg Health Score",f"{filtered['health_score'].mean():.1f}")
col4.metric("High Risk Startups",len(filtered[filtered["risk_flag"].str.contains("HIGH RISK",na=False)]))
st.divider()

#row1:leadership + risk distribution
col_left,col_right = st.columns(2)
with col_left:
    st.subheader("Health Score Leaderboard")
    display_cols =["startup_name","sector","city","health_score","latest_round","risk_flag"]
    st.dataframe(
        filtered[display_cols]
        .sort_values("health_score",ascending=False)
        .head(50)
        .reset_index(drop=True),
        use_container_width = True,
        height=400
    )

with col_right:
    st.subheader("Risk Distribution")
    risk_counts = filtered["risk_flag"].value_counts().reset_index()
    risk_counts.columns = ["Risk Flag","Count"]
    fig_risk = px.pie(
        risk_counts,
        names="Risk Flag",
        values ="Count",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_risk.update_layout(margin=dict(t=20,b=20))
    st.plotly_chart(fig_risk,use_container_width=True)

st.divider()

#row2: funding trend + top sections 
col_left2,col_right2 = st.columns(2)

with col_left2:
    st.subheader("Funding Trend By Year")
    fig_trend = px.bar(
        funding.dropna(subset=["year"]),
        x="year",y='total_funding',
        labels={"total_funding":"Total_Funding(USD)","year":"Year"},
        color_discrete_sequence=["#636EFA"]
    )
    fig_trend.update_layout(margin=dict(t=20,b=20))
    st.plotly_chart(fig_trend,use_container_width=True)

with col_right2:
    st.subheader("Top 10 Sectors by Funding")
    fig_sector = px.bar(
        sectors.head(10),
        x="total_funding",y="sector",
        orientation ="h",
        labels={"total_funding":"Total Funding(USD)","sector": "Sector"},
        color_discrete_sequence=["#EF553B"]
    )
    fig_sector.update_layout(margin=dict(t=20,b=20),
                             yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig_sector,use_container_width=True)
st.divider()

#row3 : city map + round type breakdown

col_left3, col_right3 =st.columns(2)

with col_left3:
    st.subheader("Top 15 Cities by Funding")
    fig_city = px.bar(
        cities.head(15),
        x="city",y="total_funding",
        labels={"total_funding":"Total Funding(USD)","city":"City"},
        color_discrete_sequence=["#00cc96"]
    )
    fig_city.update_layout(margin=dict(t=20,b=20))
    st.plotly_chart(fig_city,use_container_width=True)

with col_right3:
    st.subheader("Funding by Round Type")
    fig_round = px.bar(
        rounds[rounds["total_funding"]>0],
        x="round_type", y="total_funding",
        labels={"total_funding" : "Total Funding (USD)", "round_type" : "Round"},
        color_discrete_sequence=["#AB63FA"]
    )
    fig_round.update_layout(margin=dict(t=20,b=20))
    st.plotly_chart(fig_round,use_container_width=True)
st.divider()
    

#row4: Watchlist

st.subheader("Watchlist - Anomalous Signals")
st.caption("Startups with HIGH or MEDIUM risk flags - raised significant capital but no recent follow-on")

watchlist = (filtered[filtered["risk_flag"].str.contains("RISK",na=False)]
             .sort_values("total_raised",ascending=True)
             [["startup_name","sector","city","total_raised","months_since_raise","latest_round","health_score","risk_flag"]].head(30))

st.dataframe(watchlist.reset_index(drop=True),use_container_width=True)

st.divider()

#footer
st.caption("Built with Pytho . Pandas . Streamlit . Plotly | Data : Kaggle Indian Startup Funding Dataset")