# =============================
# IMPORT
# =============================
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Dashboard Laboratorium",
    layout="wide"
)

# =============================
# SIDEBAR STYLE (PINK LEMBUT)
# =============================
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #fde4ec;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =============================
# LOAD DATA
# =============================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vShFzH08gzIA2BUP7MUAmrMl8DXh8qGq_QjltBoIPsAyVSgV1XyGJFE2uZ3vntdZNB9Io1EMluKa6Nv/pub?gid=900811511&single=true&output=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
    df["Tgl"] = pd.to_datetime(df["Tgl"], errors="coerce")
    return df

df = load_data()

# =============================
# UTIL
# =============================
def fmt(n):
    try:
        return f"{int(n):,}".replace(",", ".")
    except:
        return "0"

def export_excel(df):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    return buf.getvalue()

# =============================
# SIDEBAR FILTER
# =============================
st.sidebar.title("🔎 Filter Dashboard")

# RESET FILTER
if st.sidebar.button("🔄 Reset Filter"):
    st.session_state.clear()
    st.experimental_rerun()

# =============================
# FILTER A:I
# =============================
st.sidebar.subheader("🔵 Data Operasional (A:I)")
bulan_ai_all = sorted(df["Bulan"].dropna().unique())

bulan_ai = st.sidebar.multiselect(
    "Pilih Bulan (A:I)",
    bulan_ai_all,
    default=bulan_ai_all,
    key="bulan_ai"
)

# =============================
# FILTER L:Q
# =============================
st.sidebar.subheader("🟣 Data Ringkasan (L:Q)")
bulan_lq_all = sorted(df["Bulan.1"].dropna().unique())

bulan_lq = st.sidebar.multiselect(
    "Pilih Bulan (L:Q)",
    bulan_lq_all,
    default=bulan_lq_all,
    key="bulan_lq"
)

# =============================
# HEADER
# =============================
st.title("📊 Dashboard Laboratorium")
st.caption("Data Operasional (A:I) & Data Ringkasan (L:Q) | Streamlit Gratis")

# ======================================================
# ===================== A:I =============================
# ======================================================
st.markdown("## 🔵 Data Operasional (A:I)")

df_ai = df[df["Bulan"].isin(bulan_ai)]

# KPI A:I
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Sampel", fmt(df_ai["Sampel"].sum()))
k2.metric("Total QC", fmt(df_ai["QC"].sum()))
k3.metric("Total CAL", fmt(df_ai["CAL"].sum()))
k4.metric("Total Confirm", fmt(df_ai["Confirm"].sum()))

# AGGREGASI
sampel_param = df_ai.groupby("Parameter", as_index=False)["Sampel"].sum()
qc_param = df_ai.groupby("Parameter", as_index=False)["QC"].sum()
cal_param = df_ai.groupby("Parameter", as_index=False)["CAL"].sum()
confirm_param = df_ai.groupby("Parameter", as_index=False)["Confirm"].sum()

# CHART
c1, c2 = st.columns(2)
with c1:
    fig = px.bar(sampel_param, x="Parameter", y="Sampel",
                 text="Sampel", title="Sampel per Parameter")
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=420, margin=dict(t=60))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.bar(qc_param, x="Parameter", y="QC",
                 text="QC", title="QC per Parameter")
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=420, margin=dict(t=60))
    st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    fig = px.bar(cal_param, x="Parameter", y="CAL",
                 text="CAL", title="CAL per Parameter")
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=420, margin=dict(t=60))
    st.plotly_chart(fig, use_container_width=True)

with c4:
    fig = px.bar(confirm_param, x="Parameter", y="Confirm",
                 text="Confirm", title="Confirm per Parameter")
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=420, margin=dict(t=60))
    st.plotly_chart(fig, use_container_width=True)

# TREND BULAN A:I
trend_ai = df_ai.groupby("Bulan", as_index=False)["Sampel"].sum()
fig = px.bar(trend_ai, x="Bulan", y="Sampel",
             text="Sampel", title="Tren Sampel Bulanan", color="Bulan")
fig.update_traces(textposition="outside", cliponaxis=False)
fig.update_layout(height=420, margin=dict(t=60))
st.plotly_chart(fig, use_container_width=True)

# EXPORT A:I
st.download_button(
    "⬇️ Download Excel A:I",
    export_excel(
        df_ai.groupby("Parameter", as_index=False)[
            ["Sampel", "QC", "CAL", "Confirm"]
        ].sum()
    ),
    "data_operasional_AI.xlsx"
)

# ======================================================
# ===================== L:Q =============================
# ======================================================
st.markdown("---")
st.markdown("## 🟣 Data Ringkasan (L:Q)")

df_lq = df[df["Bulan.1"].isin(bulan_lq)]

# KPI L:Q
k5, k6, k7 = st.columns(3)
k5.metric("Total MU", fmt(df_lq["MU"].sum()))
k6.metric("Jumlah Gedung", fmt(df_lq["Gedung"].nunique()))
k7.metric("Jumlah Alat", fmt(df_lq["Alat.1"].nunique()))

# AGGREGASI
mu_gedung = df_lq.groupby("Gedung", as_index=False)["MU"].sum()
mu_alat = df_lq.groupby("Alat.1", as_index=False)["MU"].sum()

# CHART
c5, c6 = st.columns(2)
with c5:
    fig = px.bar(mu_gedung, x="Gedung", y="MU",
                 text="MU", title="MU per Gedung",
                 color="Gedung",
                 color_discrete_sequence=px.colors.sequential.Purples)
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=420, margin=dict(t=60))
    st.plotly_chart(fig, use_container_width=True)

with c6:
    fig = px.bar(mu_alat, x="Alat.1", y="MU",
                 text="MU", title="MU per Alat",
                 color="Alat.1",
                 color_discrete_sequence=px.colors.sequential.Purples)
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=420, margin=dict(t=60))
    st.plotly_chart(fig, use_container_width=True)

# EXPORT L:Q
st.download_button(
    "⬇️ Download Excel L:Q",
    export_excel(
        df_lq.groupby(
            ["Bulan.1", "Gedung"],
            as_index=False
        )["MU"].sum()
    ),
    "data_ringkasan_LQ.xlsx"
)

# =============================
# FOOTER
# =============================
st.caption("© Dashboard Streamlit | A:I & L:Q • KPI • Export Excel • Free Tier Safe")
