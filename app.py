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
# DARK MODE + SIDEBAR STYLE
# =============================
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    [data-testid="stSidebar"] {
        background-color: #1a1f2b;
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
st.caption("A:I Operasional & L:Q Ringkasan Bulanan | Dark Mode")

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

fig = px.bar(
    sampel_param,
    x="Parameter",
    y="Sampel",
    color="Parameter",
    text="Sampel",
    color_discrete_sequence=px.colors.qualitative.Bold,
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

# KPI
k5, k6, k7 = st.columns(3)
k5.metric("Total MU", fmt(df_lq["MU"].sum()))
k6.metric("Jumlah Gedung", df_lq["Gedung"].nunique())
k7.metric("Jumlah Alat", df_lq["Alat.1"].nunique())

# =============================
# TOTAL MU PER BULAN
# =============================
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
mu_bulanan = mu_bulanan[mu_bulanan["MU"] > 0]

# HIGHLIGHT NILAI TERTINGGI
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
        "Peak": "#FFD700",    # emas
        "Normal": "#7B61FF"   # ungu
    },
    title="Total MU per Bulan (Highlight Otomatis)"
)

fig.update_traces(
    textposition="outside",
    cliponaxis=False,
    hovertemplate=
        "<b>Bulan:</b> %{x}<br>"
        "<b>MU:</b> %{y:,}<br>"
        "<extra></extra>"
)

fig.update_layout(
    xaxis_title="Bulan",
    yaxis_title="MU",
    height=450
)

st.plotly_chart(fig, use_container_width=True)

# =============================
# EXPORT
# =============================
st.download_button(
    "⬇️ Download Excel L:Q",
    export_excel(mu_bulanan),
    "data_ringkasan_LQ.xlsx"
)

# =============================
# FOOTER
# =============================
st.caption(
    "© Dashboard Streamlit | Dark Mode • Highlight Peak • Smooth Hover | Free Tier Safe"
)
