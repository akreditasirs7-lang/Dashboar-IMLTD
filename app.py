import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import numpy as np

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Dashboard MU & Gedung",
    layout="wide"
)

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vShFzH08gzIA2BUP7MUAmrMl8DXh8qGq_QjltBoIPsAyVSgV1XyGJFE2uZ3vntdZNB9Io1EMluKa6Nv/pub?gid=900811511&single=true&output=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df["Tgl"] = pd.to_datetime(df["Tgl"], errors="coerce")
    return df

df = load_data()

# =============================
# HEADER
# =============================
st.markdown("## 🟣 Dashboard MU & Gedung (Executive)")
st.caption("Kategori 2 | Streamlit Free Edition")

# =============================
# FILTER
# =============================
f1, f2, f3, f4 = st.columns(4)

gedung = f1.multiselect("Gedung", df["Gedung"].dropna().unique())
alat = f2.multiselect("Alat", df["Alat.1"].dropna().unique())
bulan = f3.multiselect("Bulan", df["Bulan.1"].dropna().unique())
tahun = f4.multiselect("Tahun", df["Tahun.1"].dropna().unique())

df2 = df.copy()
if gedung: df2 = df2[df2["Gedung"].isin(gedung)]
if alat: df2 = df2[df2["Alat.1"].isin(alat)]
if bulan: df2 = df2[df2["Bulan.1"].isin(bulan)]
if tahun: df2 = df2[df2["Tahun.1"].isin(tahun)]

# =============================
# KPI
# =============================
k1, k2, k3, k4 = st.columns(4)

k1.metric("Total MU", int(df2["MU"].sum()))
k2.metric("Rata-rata MU", round(df2["MU"].mean(), 1))
k3.metric("Jumlah Gedung", df2["Gedung"].nunique())
k4.metric("Jumlah Alat", df2["Alat.1"].nunique())

# =============================
# CHART
# =============================
c1, c2 = st.columns(2)

with c1:
    fig = px.bar(
        df2,
        x="Gedung",
        y="MU",
        color="Gedung",
        title="Total MU per Gedung",
        color_discrete_sequence=px.colors.sequential.Purples
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.line(
        df2.sort_values("Tgl"),
        x="Tgl",
        y="MU",
        color="Gedung",
        title="Tren MU",
        color_discrete_sequence=px.colors.sequential.Purples
    )
    st.plotly_chart(fig, use_container_width=True)

st.dataframe(df2, use_container_width=True)
