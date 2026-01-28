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
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vShFzH08gzIA2BUP7MUAmrMl8DXh8qGq_QjltBoIPsAyVSgV1XyGJFE2uZ3vntdZNB9Io1EMluKa6Nv/"
    "pub?gid=900811511&single=true&output=csv"
)

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)

    # pastikan kolom tanggal aman
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
# URUTAN BULAN (PENTING)
# =============================
URUTAN_BULAN = [
    "Jan","Feb","Mar","Apr","Mei","Jun",
    "Jul","Agu","Sep","Okt","Nov","Des"
]

# =============================
# SIDEBAR FILTER (GLOBAL)
# =============================
st.sidebar.title("🔎 Filter Dashboard")

if st.sidebar.button("🔄 Reset Filter"):
    st.session_state.clear()
    st.experimental_rerun()

st.sidebar.subheader("🔵 Filter Bulan (Global)")

bulan_ai_all = [b for b in URUTAN_BULAN if b in df["Bulan"].dropna().unique()]

pilih_semua = st.sidebar.checkbox("Pilih Semua Bulan", True)

if pilih_semua:
    bulan_filter = bulan_ai_all
else:
    bulan_filter = st.sidebar.multiselect(
        "Pilih Bulan",
        bulan_ai_all,
        default=bulan_ai_all
    )

# =============================
# HEADER
# =============================
st.title("📊 Dashboard Laboratorium")
st.caption("A:I (Operasional) & L:Q (Ringkasan Bulanan) | Streamlit Gratis")

# ======================================================
# ===================== A:I =============================
# ======================================================
st.markdown("## 🔵 Data Operasional (A:I)")

df_ai = df[df["Bulan"].isin(bulan_filter)]

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

# CHART A:I
c1, c2 = st.columns(2)
with c1:
    fig = px.bar(
        sampel_param,
        x="Parameter",
        y="Sampel",
        text="Sampel",
        title="Sampel per Parameter"
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.bar(
        qc_param,
        x="Parameter",
        y="QC",
        text="QC",
        title="QC per Parameter"
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig, use_container_width=True)

# TREND BULAN A:I
trend_ai = (
    df_ai.groupby("Bulan", as_index=False)["Sampel"]
    .sum()
)

trend_ai["Bulan"] = pd.Categorical(
    trend_ai["Bulan"],
    categories=URUTAN_BULAN,
    ordered=True
)
trend_ai = trend_ai.sort_values("Bulan")

fig = px.bar(
    trend_ai,
    x="Bulan",
    y="Sampel",
    text="Sampel",
    title="Tren Sampel Bulanan"
)
fig.update_traces(textposition="outside", cliponaxis=False)
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

# 🔴 PENTING: L:Q pakai Bulan.1
df_lq = df[df["Bulan.1"].isin(bulan_filter)]

# KPI L:Q
k5, k6, k7 = st.columns(3)
k5.metric("Total MU", fmt(df_lq["MU"].sum()))
k6.metric("Jumlah Gedung", df_lq["Gedung"].nunique())
k7.metric("Jumlah Alat", df_lq["Alat.1"].nunique())

# =============================
# TOTAL MU PER BULAN (SUM)
# =============================
mu_bulanan = (
    df_lq
    .groupby("Bulan.1", as_index=False)["MU"]
    .sum()
)

# urutkan bulan dengan benar
mu_bulanan["Bulan.1"] = pd.Categorical(
    mu_bulanan["Bulan.1"],
    categories=URUTAN_BULAN,
    ordered=True
)
mu_bulanan = mu_bulanan.sort_values("Bulan.1")

# hapus bulan MU = 0 (biar gak ada bulan hantu)
mu_bulanan = mu_bulanan[mu_bulanan["MU"] > 0]

# =============================
# BAR CHART L:Q
# =============================
fig = px.bar(
    mu_bulanan,
    x="Bulan.1",
    y="MU",
    text="MU",
    title="Total MU per Bulan"
)

fig.update_traces(
    textposition="outside",
    cliponaxis=False
)

fig.update_layout(
    xaxis_title="Bulan",
    yaxis_title="MU",
    height=420
)

st.plotly_chart(fig, use_container_width=True)

# EXPORT L:Q
st.download_button(
    "⬇️ Download Excel L:Q",
    export_excel(mu_bulanan),
    "data_ringkasan_LQ.xlsx"
)

# =============================
# FOOTER
# =============================
st.caption(
    "© Dashboard Streamlit | A:I Operasional & L:Q Ringkasan Bulanan | "
    "Akurat • Tidak Ada Bulan Palsu • Free Tier Safe"
)
