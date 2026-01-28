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
st.set_page_config(page_title="Dashboard Laboratorium", layout="wide")

# =============================
# DARK MODE + SIDEBAR
# =============================
st.markdown(
    """
    <style>
    body, .stApp { background-color: #0e1117; color: #fafafa; }
    [data-testid="stSidebar"] { background-color: #1a1f2b; }
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
    return df

df = load_data()

# =============================
# UTIL
# =============================
def fmt(n):
    return f"{int(n):,}".replace(",", ".") if pd.notna(n) else "0"

# =============================
# URUTAN BULAN
# =============================
URUTAN_BULAN = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]

# =============================
# SIDEBAR FILTER
# =============================
st.sidebar.title("🔎 Filter Dashboard")

bulan_available = [b for b in URUTAN_BULAN if b in df["Bulan"].dropna().unique()]
bulan_filter = bulan_available if st.sidebar.checkbox("Pilih Semua Bulan", True) else st.sidebar.multiselect(
    "Pilih Bulan", bulan_available, default=bulan_available
)

# =============================
# HEADER
# =============================
st.title("📊 Dashboard Laboratorium")
st.caption("Dark Mode • Batang Warna Variasi • Highlight Peak")

# ======================================================
# ===================== A:I =============================
# ======================================================
st.markdown("## 🔵 Data Operasional (A:I)")

df_ai = df[df["Bulan"].isin(bulan_filter)]

sampel_param = df_ai.groupby("Parameter", as_index=False)["Sampel"].sum()

# 🔥 WARNA VARIASI JELAS (SETIAP BATANG BEDA)
fig = px.bar(
    sampel_param,
    x="Parameter",
    y="Sampel",
    color="Parameter",
    text="Sampel",
    color_discrete_sequence=px.colors.qualitative.Vivid,
    title="Sampel per Parameter"
)

fig.update_traces(
    textposition="outside",
    cliponaxis=False,
    hovertemplate="<b>Parameter:</b> %{x}<br><b>Sampel:</b> %{y:,}<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True)

# ======================================================
# ===================== L:Q =============================
# ======================================================
st.markdown("---")
st.markdown("## 🟣 Data Ringkasan (L:Q)")

df_lq = df[df["Bulan.1"].isin(bulan_filter)]

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

# 🔥 HIGHLIGHT PEAK
max_mu = mu_bulanan["MU"].max()
mu_bulanan["Color"] = mu_bulanan["MU"].apply(
    lambda x: "Peak" if x == max_mu else "Normal"
)

# 🔥 WARNA UNGU + EMAS (JELAS)
fig = px.bar(
    mu_bulanan,
    x="Bulan.1",
    y="MU",
    color="Color",
    text="MU",
    color_discrete_map={
        "Peak": "#FFD700",     # emas
        "Normal": "#9B7BFF"    # ungu terang
    },
    title="Total MU per Bulan"
)

fig.update_traces(
    textposition="outside",
    cliponaxis=False,
    hovertemplate="<b>Bulan:</b> %{x}<br><b>MU:</b> %{y:,}<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True)
