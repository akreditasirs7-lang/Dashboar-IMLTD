# =============================
# IMPORT
# =============================
import streamlit as st
import pandas as pd
import plotly.express as px

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Dashboard Laboratorium",
    layout="wide"
)

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vShFzH08gzIA2BUP7MUAmrMl8DXh8qGq_QjltBoIPsAyVSgV1XyGJFE2uZ3vntdZNB9Io1EMluKa6Nv/pub?gid=900811511&single=true&output=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    df["Tgl"] = pd.to_datetime(df["Tgl"], errors="coerce")
    return df

df = load_data()

# =============================
# HEADER
# =============================
st.title("📊 Dashboard Laboratorium")
st.caption("Operasional (A:I) & Ringkasan (A:Q) | Streamlit Gratis")

# ======================================================
# ===================== BAGIAN A:I =====================
# ======================================================
st.markdown("## 🔵 Data Operasional (A:I)")

bulan_ai = st.multiselect(
    "Bulan (Operasional)",
    df["Bulan"].dropna().unique()
)

df_ai = df.copy()
if bulan_ai:
    df_ai = df_ai[df_ai["Bulan"].isin(bulan_ai)]

# ---------- CHART A:I ----------
c1, c2 = st.columns(2)

with c1:
    fig = px.bar(
        df_ai,
        x="Parameter",
        y="Sampel",
        color="Parameter",
        title="Sampel per Parameter"
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.bar(
        df_ai,
        x="Parameter",
        y="QC",
        color="Parameter",
        title="QC per Parameter"
    )
    st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    fig = px.bar(
        df_ai,
        x="Parameter",
        y="CAL",
        color="Parameter",
        title="CAL per Parameter"
    )
    st.plotly_chart(fig, use_container_width=True)

with c4:
    fig = px.bar(
        df_ai,
        x="Parameter",
        y="Confirm",
        color="Parameter",
        title="Confirm per Parameter"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------- TREND BATANGAN ----------
st.markdown("### 📈 Tren Sampel per Bulan")

trend_ai = (
    df_ai
    .groupby("Bulan", as_index=False)["Sampel"]
    .sum()
)

fig = px.bar(
    trend_ai,
    x="Bulan",
    y="Sampel",
    title="Tren Sampel Bulanan",
    color="Bulan"
)
st.plotly_chart(fig, use_container_width=True)

# ======================================================
# ===================== BAGIAN A:Q =====================
# ======================================================
st.markdown("---")
st.markdown("## 🟣 Data Ringkasan (A:Q)")

bulan_aq = st.multiselect(
    "Bulan (Ringkasan)",
    df["Bulan.1"].dropna().unique()
)

df_aq = df.copy()
if bulan_aq:
    df_aq = df_aq[df_aq["Bulan.1"].isin(bulan_aq)]

# ---------- CHART A:Q ----------
c5, c6 = st.columns(2)

with c5:
    fig = px.bar(
        df_aq,
        x="Gedung",
        y="MU",
        color="Gedung",
        title="MU per Gedung",
        color_discrete_sequence=px.colors.sequential.Purples
    )
    st.plotly_chart(fig, use_container_width=True)

with c6:
    fig = px.bar(
        df_aq,
        x="Alat.1",
        y="MU",
        color="Alat.1",
        title="MU per Alat",
        color_discrete_sequence=px.colors.sequential.Purples
    )
    st.plotly_chart(fig, use_container_width=True)

# =============================
# FOOTER
# =============================
st.caption("© Dashboard Streamlit | Free Tier Safe")
