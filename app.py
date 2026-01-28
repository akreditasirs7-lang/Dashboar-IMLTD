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
# DARK MODE + SIDEBAR STYLE (FIX TEXT)
# =============================
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }

    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #1a1f2b;
    }

    /* Sidebar text */
    [data-testid="stSidebar"] * {
        color: #fafafa !important;
    }

    /* Checkbox & selectbox label */
    label {
        color: #fafafa !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =============================
# LOAD DATA
# =============================
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vShFzH08gzIA2BUP7MUAmrMl8DXh8qGq_QjltBoIPsAyVSgV1XyGJFE2uZ3vntdZNB9Io1EMluKa6Nv/"
    "pub?gid=900811511&single=true&output=csv"
)

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    return df

df = load_data()

# =============================
# UTIL
# =============================
def fmt(n):
    return f"{int(n):,}".replace(",", ".") if pd.notna(n) else "0"

def export_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    return buffer.getvalue()

# =============================
# URUTAN BULAN
# =============================
URUTAN_BULAN = [
    "Jan","Feb","Mar","Apr","Mei","Jun",
    "Jul","Agu","Sep","Okt","Nov","Des"
]

# =============================
# SIDEBAR FILTER
# =============================
st.sidebar.title("🔎 Filter Dashboard")

bulan_available = [b for b in URUTAN_BULAN if b in df["Bulan"].dropna().unique()]
pilih_semua = st.sidebar.checkbox("Pilih Semua Bulan", True)

bulan_filter = bulan_available if pilih_semua else st.sidebar.multiselect(
    "Pilih Bulan",
    bulan_available,
    default=bulan_available
)

# =============================
# HEADER
# =============================
st.title("📊 Dashboard Laboratorium")
st.caption("Dark Mode • Warna Variatif • Data Operasional & Ringkasan")

# ======================================================
# ===================== A:I =============================
# ======================================================
st.markdown("## 🔵 Data Operasional (A:I)")

df_ai = df[df["Bulan"].isin(bulan_filter)]

# KPI
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

# ===== CHART ROW 1 =====
c1, c2 = st.columns(2)
with c1:
    fig = px.bar(
        sampel_param,
        x="Parameter",
        y="Sampel",
        color="Parameter",
        text="Sampel",
        title="Sampel per Parameter",
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.bar(
        qc_param,
        x="Parameter",
        y="QC",
        color="Parameter",
        text="QC",
        title="QC per Parameter",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig, use_container_width=True)

# ===== CHART ROW 2 =====
c3, c4 = st.columns(2)
with c3:
    fig = px.bar(
        cal_param,
        x="Parameter",
        y="CAL",
        color="Parameter",
        text="CAL",
        title="CAL per Parameter",
        color_discrete_sequence=px.colors.qualitative.Dark2
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    fig = px.bar(
        confirm_param,
        x="Parameter",
        y="Confirm",
        color="Parameter",
        text="Confirm",
        title="Confirm per Parameter",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig, use_container_width=True)

# ======================================================
# ===================== L:Q =============================
# ======================================================
st.markdown("---")
st.markdown("## 🟣 Data Ringkasan (L:Q)")

df_lq = df[df["Bulan.1"].isin(bulan_filter)]

# KPI
k5, k6, k7 = st.columns(3)
k5.metric("Total MU", fmt(df_lq["MU"].sum()))
k6.metric("Jumlah Gedung", df_lq["Gedung"].nunique())
k7.metric("Jumlah Alat", df_lq["Alat.1"].nunique())

# TOTAL MU BULANAN
mu_bulanan = (
    df_lq.groupby("Bulan.1", as_index=False)["MU"]
    .sum()
)

mu_bulanan["Bulan.1"] = pd.Categorical(
    mu_bulanan["Bulan.1"],
    categories=URUTAN_BULAN,
    ordered=True
)
mu_bulanan = mu_bulanan.sort_values("Bulan.1")

# HIGHLIGHT PEAK
max_mu = mu_bulanan["MU"].max()
mu_bulanan["Highlight"] = mu_bulanan["MU"].apply(
    lambda x: "Peak" if x == max_mu else "Normal"
)

fig = px.bar(
    mu_bulanan,
    x="Bulan.1",
    y="MU",
    color="Highlight",
    text="MU",
    color_discrete_map={
        "Peak": "#FFD700",
        "Normal": "#9B7BFF"
    },
    title="Total MU per Bulan (Highlight Otomatis)"
)

fig.update_traces(
    textposition="outside",
    cliponaxis=False,
    hovertemplate="<b>Bulan:</b> %{x}<br><b>MU:</b> %{y:,}<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True)

# =============================
# FOOTER
# =============================
st.caption(
    "© Dashboard Streamlit | Dark Mode • Warna Variatif • Sidebar Jelas • Free Tier Safe"
)
