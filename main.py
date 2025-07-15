import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Variance Level P&L", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("Kitchen_PNL_Data1.xlsx", header=0)

    df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_")
    # st.write(df.columns)
    df["MONTH"] = pd.to_datetime(df["MONTH"], errors="coerce").dt.strftime('%b-%Y')

    # Variance Buckets
    df["VARIANCE_BUCKET"] = pd.cut(df["VARIANCE"], bins=[0, 10000, 20000, 30000, 40000, float("inf")],
                                   labels=["0–10K", "10–20K", "20–30K", "30–40K", "40K+"])
    
    # Revenue Ranges
    df["REVENUE_RANGE"] = pd.cut(df["NET_REVENUE"],
                                 bins=[0, 2000000, 3000000, 4000000, 5000000, float("inf")],
                                 labels=["0–2M", "2–3M", "3–4M", "4–5M", "5M+"])
    return df

df = load_data()

st.sidebar.header("📊 Filters")

# Kitchen EBITDA filter
kitchen_ebitda_range = st.sidebar.slider(
    "Kitchen EBITDA (₹)", 
    float(df["KITCHEN_EBITDA"].min()), 
    float(df["KITCHEN_EBITDA"].max()), 
    (float(df["KITCHEN_EBITDA"].min()), float(df["KITCHEN_EBITDA"].max()))
)

# Net Revenue filter
revenue_range = st.sidebar.slider(
    "Net Revenue (₹)", 
    float(df["NET_REVENUE"].min()), 
    float(df["NET_REVENUE"].max()), 
    (float(df["NET_REVENUE"].min()), float(df["NET_REVENUE"].max()))
)
# Applying filter
df = df[
    (df["KITCHEN_EBITDA"].between(kitchen_ebitda_range[0], kitchen_ebitda_range[1])) &
    (df["NET_REVENUE"].between(revenue_range[0], revenue_range[1]))
]

st.title("📊 Dashboard 2: Variance Level P&L")

tab1, tab2 = st.tabs(["📉 Avg Variance by Revenue Cohort", "📋 Store Count by Month & Revenue"])
with tab1:
    st.subheader("📊 Average Variance % by Revenue Cohort")
    
    avg_variance = df.groupby("REVENUE_COHORT")["VARIANCE"].mean().reset_index()
    fig = px.bar(avg_variance, x="REVENUE_COHORT", y="VARIANCE", color="REVENUE_COHORT",
                 title="Average Variance per Revenue Cohort",
                 labels={"VARIANCE": "Average Variance (₹)", "REVENUE_COHORT": "Revenue Cohort"})
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📋 Store Count by Month and Revenue Range")
    
    # Dropdown for Variance Bucket
    selected_bucket = st.selectbox("Select Variance Bucket", df["VARIANCE_BUCKET"].dropna().unique())

    df_filtered = df[df["VARIANCE_BUCKET"] == selected_bucket]

    # Count of unique stores by MONTH and REVENUE RANGE
    pivot_data = (
        df_filtered.groupby(["MONTH", "REVENUE_RANGE"])["STORE"]
        .nunique()
        .reset_index()
        .pivot(index="MONTH", columns="REVENUE_RANGE", values="STORE")
        .fillna(0)
        .astype(int)
        .sort_index()
    )

    st.markdown(f"### Store Count for Variance Bucket: **{selected_bucket}**")
    st.dataframe(pivot_data, use_container_width=True)

