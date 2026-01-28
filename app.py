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
# DARK MODE + SIDEBAR STYLE
# =============================
st.markdown(
    """
    <style>
    body, .stApp { background-color: #0e1117; color: #fafafa; }
    [data-testid="stSidebar"] { background-color: #1a1f2b; }
    [data-testid="stSidebar"] * { color: #fafafa !important; }
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
    return pd.read_csv(CSV_URL)

df = load_data()

# =============================
# UTIL
# =============================
def fmt(n):
    return f"{int(n):,}".replace(",", ".") if pd.notna(n) else "0"

# =============================
# URUTAN BULAN (FINAL)
# =============================
URUTAN_BULAN = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]

# =============================
# SIDEBAR FILTER (KHUSUS A:I)
# =============================
st.sidebar.title("🔎 Filter Dashboard")

bulan_ai_available = [b for b in URUTAN_BULAN if b in df["Bulan"].dropna().unique()]

pilih_semua = st.sidebar.checkbox("Pilih Semua Bulan (A:I)", True)

bulan_filter_ai = bulan_ai_available if pilih_semua else st.sidebar.multiselect(
    "Pilih Bulan (A:I)",
    bulan_ai_available,
    default=bulan_ai_available
)

# =============================
# HEADER
# =============================
st.title("📊 Dashboard Laboratorium")
st.caption("A:I Operasional • L:Q Ringkasan MU | Dark Mode")

# ======================================================
# ===================== A:I =============================
# ======================================================
st.markdown("## 🔵 Data Operasional (A:I)")

df_ai = df[df["Bulan"].isin(bulan_filter_ai)]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Sampel", fmt(df_ai["Sampel"].sum()))
k2.metric("Total QC", fmt(df_ai["QC"].sum()))
k3.metric("Total CAL", fmt(df_ai["CAL"].sum()))
k4.metric("Total Confirm", fmt(df_ai["Confirm"].sum()))

# =============================
# ===================== L:Q =============================
# =============================
st.markdown("---")
st.markdown("## 🟣 Data Ringkasan (L:Q)")

# 🔴 PENTING: TIDAK DI-FILTER DENGAN BULAN A:I
df_lq = df.copy()

k5, k6, k7 = st.columns(3)
k5.metric("Total MU", fmt(df_lq["MU"].sum()))
k6.metric("Jumlah Gedung", df_lq["Gedung"].nunique())
k7.metric("Jumlah Alat", df_lq["Alat.1"].nunique())

# =============================
# MU BULANAN (SUM BENAR)
# =============================
mu_bulanan = (
    df_lq
    .groupby("Bulan.1", as_index=False)["MU"]
    .sum()
)

mu_bulanan["Bulan.1"] = pd.Categorical(
    mu_bulanan["Bulan.1"],
    categories=URUTAN_BULAN,
    ordered=True
)

mu_bulanan = mu_bulanan.sort_values("Bulan.1")

# ❌ JANGAN PAKSA BULAN 0
mu_bulanan = mu_bulanan[mu_bulanan["MU"].notna() & (mu_bulanan["MU"] > 0)]

# =============================
# HIGHLIGHT PEAK
# =============================
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
    title="Total MU per Bulan (Urut Jan–Des)"
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
    "© Dashboard Streamlit | Desember FIX • Urutan Benar • Dark Mode • Free Tier Safe"
)
