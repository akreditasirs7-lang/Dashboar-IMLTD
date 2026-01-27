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
st.caption("Operasional (A:I) & Ringkasan (A:Q) | Streamlit Free Tier")

# ======================================================
# ===================== BAGIAN A:I =====================
# ======================================================
st.markdown("## 🔵 Data Operasional (A:I)")

bulan_ai = st.multiselect(
    "Bulan (Operasional)",
    sorted(df["Bulan"].dropna().unique())
)

df_ai = df.copy()
if bulan_ai:
    df_ai = df_ai[df_ai["Bulan"].isin(bulan_ai)]

# ---------- AGGREGASI ----------
sampel_param = df_ai.groupby("Parameter", as_index=False)["Sampel"].sum()
qc_param = df_ai.groupby("Parameter", as_index=False)["QC"].sum()
cal_param = df_ai.groupby("Parameter", as_index=False)["CAL"].sum()
confirm_param = df_ai.groupby("Parameter", as_index=False)["Confirm"].sum()

# ---------- CHART ROW 1 ----------
c1, c2 = st.columns(2)

with c1:
    fig = px.bar(
        sampel_param,
        x="Parameter",
        y="Sampel",
        title="Sampel per Parameter",
        text="Sampel"
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=420, margin=dict(t=60))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.bar(
        qc_param,
        x="Parameter",
        y="QC",
        title="QC per Parameter",
        text="QC"
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=420, margin=dict(t=60))
    st.plotly_chart(fig, use_container_width=True)

# ---------- CHART ROW 2 ----------
c3, c4 = st.columns(2)

with c3:
    fig = px.bar(
        cal_param,
        x="Parameter",
        y="CAL",
        title="CAL per Parameter",
        text="CAL"
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=420, margin=dict(t=60))
    st.plotly_chart(fig, use_container_width=True)

with c4:
    fig = px.bar(
        confirm_param,
        x="Parameter",
        y="Confirm",
        title="Confirm per Parameter",
        text="Confirm"
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=420, margin=dict(t=60))
    st.plotly_chart(fig, use_container_width=True)

# ---------- TREND BULAN ----------
st.markdown("### 📈 Tren Sampel per Bulan")

trend_ai = df_ai.groupby("Bulan", as_index=False)["Sampel"].sum()

fig = px.bar(
    trend_ai,
    x="Bulan",
    y="Sampel",
    title="Tren Sampel Bulanan",
    text="Sampel",
    color="Bulan"
)
fig.update_traces(textposition="outside", cliponaxis=False)
fig.update_layout(height=420, margin=dict(t=60))
st.plotly_chart(fig, use_container_width=True)

# ======================================================
# ===================== BAGIAN A:Q =====================
# ======================================================
st.markdown("---")
st.markdown("## 🟣 Data Ringkasan (A:Q)")

bulan_aq = st.multiselect(
    "Bulan (Ringkasan)",
    sorted(df["Bulan.1"].dropna().unique())
)

df_aq = df.copy()
if bulan_aq:
    df_aq = df_aq[df_aq["Bulan.1"].isin(bulan_aq)]

# ---------- AGGREGASI ----------
mu_gedung = df_aq.groupby("Gedung", as_index=False)["MU"].sum()
mu_alat = df_aq.groupby("Alat.1", as_index=False)["MU"].sum()

# ---------- CHART A:Q ----------
c5, c6 = st.columns(2)

with c5:
    fig = px.bar(
        mu_gedung,
        x="Gedung",
        y="MU",
        title="MU per Gedung",
        text="MU",
        color="Gedung",
        color_discrete_sequence=px.colors.sequential.Purples
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=420, margin=dict(t=60))
    st.plotly_chart(fig, use_container_width=True)

with c6:
    fig = px.bar(
        mu_alat,
        x="Alat.1",
        y="MU",
        title="MU per Alat",
        text="MU",
        color="Alat.1",
        color_discrete_sequence=px.colors.sequential.Purples
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=420, margin=dict(t=60))
    st.plotly_chart(fig, use_container_width=True)

# =============================
# FOOTER
# =============================
st.caption("© Dashboard Streamlit | Data teragregasi & akurat")
