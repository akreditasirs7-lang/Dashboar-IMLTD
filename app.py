import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Dashboard Laboratorium Executive",
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

st.title("📊 Dashboard Monitoring Laboratorium")
st.caption("Streamlit Free Edition | Data Real-time")

# =============================
# SIDEBAR
# =============================
st.sidebar.header("🔎 Filter Dashboard")
kategori = st.sidebar.radio(
    "Pilih Kategori",
    ["Kategori 1 (A:I)", "Kategori 2 (L:Q)"]
)

# =============================
# FUNCTION EXPORT
# =============================
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# =============================
# KATEGORI 1
# =============================
if kategori == "Kategori 1 (A:I)":
    st.subheader("📌 Pemeriksaan & Sampel")

    f1, f2, f3, f4 = st.columns(4)
    alat = f1.multiselect("Alat", df["Alat"].dropna().unique())
    parameter = f2.multiselect("Parameter", df["Parameter"].dropna().unique())
    bulan = f3.multiselect("Bulan", df["Bulan"].dropna().unique())
    tahun = f4.multiselect("Tahun", df["Tahun"].dropna().unique())

    df1 = df.copy()
    if alat: df1 = df1[df1["Alat"].isin(alat)]
    if parameter: df1 = df1[df1["Parameter"].isin(parameter)]
    if bulan: df1 = df1[df1["Bulan"].isin(bulan)]
    if tahun: df1 = df1[df1["Tahun"].isin(tahun)]

    # =============================
    # KPI
    # =============================
    k1, k2, k3, k4 = st.columns(4)

    total_sampel = int(df1["Sampel"].sum())
    total_qc = int(df1["QC"].sum())
    avg_harian = round(df1.groupby("Tanggal")["Sampel"].sum().mean(), 1)
    param_count = df1["Parameter"].nunique()

    k1.metric("Total Sampel", total_sampel)
    k2.metric("Total QC", total_qc)
    k3.metric("Rata-rata Sampel / Hari", avg_harian)
    k4.metric("Jumlah Parameter", param_count)

    # =============================
    # ALERT
    # =============================
    if (df1["QC"] == 0).any():
        st.warning("⚠️ Ditemukan QC = 0 pada data terfilter")

    if total_sampel > 1000:
        st.error("🚨 Lonjakan Sampel Tinggi")

    # =============================
    # CHART
    # =============================
    c1, c2 = st.columns(2)

    with c1:
        fig = px.bar(df1, x="Parameter", y="Sampel", color="Alat",
                     title="Jumlah Sampel per Parameter")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.line(df1.sort_values("Tanggal"),
                      x="Tanggal", y="Sampel",
                      color="Parameter",
                      title="Tren Sampel Harian")
        st.plotly_chart(fig, use_container_width=True)

    st.plotly_chart(
        px.pie(df1, names="Alat", title="Distribusi Alat"),
        use_container_width=True
    )

    st.download_button(
        "⬇️ Download Excel",
        to_excel(df1),
        "kategori1.xlsx"
    )

    st.dataframe(df1, use_container_width=True)

# =============================
# KATEGORI 2
# =============================
else:
    st.subheader("📌 MU & Gedung")

    f1, f2, f3, f4 = st.columns(4)
    gedung = f1.multiselect("Gedung", df["Gedung"].dropna().unique())
    alat2 = f2.multiselect("Alat", df["Alat.1"].dropna().unique())
    bulan2 = f3.multiselect("Bulan", df["Bulan.1"].dropna().unique())
    tahun2 = f4.multiselect("Tahun", df["Tahun.1"].dropna().unique())

    df2 = df.copy()
    if gedung: df2 = df2[df2["Gedung"].isin(gedung)]
    if alat2: df2 = df2[df2["Alat.1"].isin(alat2)]
    if bulan2: df2 = df2[df2["Bulan.1"].isin(bulan2)]
    if tahun2: df2 = df2[df2["Tahun.1"].isin(tahun2)]

    k1, k2, k3, k4 = st.columns(4)

    total_mu = int(df2["MU"].sum())
    avg_mu = round(df2["MU"].mean(), 1)

    k1.metric("Total MU", total_mu)
    k2.metric("Rata-rata MU", avg_mu)
    k3.metric("Jumlah Gedung", df2["Gedung"].nunique())
    k4.metric("Jumlah Alat", df2["Alat.1"].nunique())

    if (df2["MU"] > 100).any():
        st.error("🚨 MU melebihi threshold")

    c1, c2 = st.columns(2)

    with c1:
        st.plotly_chart(
            px.line(df2.sort_values("Tgl"),
                    x="Tgl", y="MU", color="Gedung",
                    title="Tren MU"),
            use_container_width=True
        )

    with c2:
        st.plotly_chart(
            px.bar(df2, x="Alat.1", y="MU", color="Gedung",
                   title="MU per Alat"),
            use_container_width=True
        )

    st.download_button(
        "⬇️ Download Excel",
        to_excel(df2),
        "kategori2.xlsx"
    )

    st.dataframe(df2, use_container_width=True)
