# =============================
# IMPORT
# =============================
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Dashboard Laboratorium",
    layout="wide"
)

# =============================
# SIDEBAR STYLE
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
# EXPORT FUNCTIONS
# =============================
def export_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def export_pdf(df, title):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph(title, styles["Heading1"])]

    table_data = [df.columns.tolist()] + df.astype(str).values.tolist()
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONT", (0,0), (-1,0), "Helvetica-Bold")
    ]))

    elements.append(table)
    doc.build(elements)
    return buffer.getvalue()

# =============================
# SIDEBAR FILTER
# =============================
st.sidebar.title("🔎 Filter Dashboard")

# --- A:I ---
st.sidebar.subheader("🔵 Data Operasional (A:I)")
bulan_ai_all = sorted(df["Bulan"].dropna().unique())
bulan_ai = st.sidebar.multiselect(
    "Bulan A:I",
    bulan_ai_all,
    default=bulan_ai_all,
    key="bulan_ai"
)

# --- A:Q ---
st.sidebar.subheader("🟣 Data Ringkasan (A:Q)")
bulan_aq_all = sorted(df["Bulan.1"].dropna().unique())
bulan_aq = st.sidebar.multiselect(
    "Bulan A:Q",
    bulan_aq_all,
    default=bulan_aq_all,
    key="bulan_aq"
)

# =============================
# HEADER
# =============================
st.title("📊 Dashboard Laboratorium")

# ======================================================
# ===================== A:I =============================
# ======================================================
st.markdown("## 🔵 Data Operasional (A:I)")

df_ai = df[df["Bulan"].isin(bulan_ai)]

ai_export = df_ai.groupby("Parameter", as_index=False)[
    ["Sampel", "QC", "CAL", "Confirm"]
].sum()

st.dataframe(ai_export, use_container_width=True)

# EXPORT A:I
format_ai = st.selectbox("Export Data A:I", ["Excel", "PDF"], key="exp_ai")
if format_ai == "Excel":
    st.download_button(
        "⬇️ Download Excel A:I",
        export_excel(ai_export),
        "data_operasional.xlsx"
    )
else:
    st.download_button(
        "⬇️ Download PDF A:I",
        export_pdf(ai_export, "Data Operasional (A:I)"),
        "data_operasional.pdf"
    )

# ======================================================
# ===================== A:Q =============================
# ======================================================
st.markdown("---")
st.markdown("## 🟣 Data Ringkasan (A:Q)")

df_aq = df[df["Bulan.1"].isin(bulan_aq)]

aq_export = df_aq.groupby(
    ["Bulan.1", "Gedung"],
    as_index=False
)["MU"].sum()

# ---------- 3D TREND ----------
st.markdown("### 📊 3D Tren MU Bulanan")

fig = px.scatter_3d(
    aq_export,
    x="Bulan.1",
    y="Gedung",
    z="MU",
    color="Gedung",
    size="MU",
    title="3D Tren MU Bulanan"
)
st.plotly_chart(fig, use_container_width=True)

st.dataframe(aq_export, use_container_width=True)

# EXPORT A:Q
format_aq = st.selectbox("Export Data A:Q", ["Excel", "PDF"], key="exp_aq")
if format_aq == "Excel":
    st.download_button(
        "⬇️ Download Excel A:Q",
        export_excel(aq_export),
        "data_ringkasan.xlsx"
    )
else:
    st.download_button(
        "⬇️ Download PDF A:Q",
        export_pdf(aq_export, "Data Ringkasan (A:Q)"),
        "data_ringkasan.pdf"
    )

# =============================
# FOOTER
# =============================
st.caption("© Dashboard Streamlit | Export Excel & PDF | 3D Trend Aman Free Tier")
