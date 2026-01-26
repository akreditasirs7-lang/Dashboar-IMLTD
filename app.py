import numpy as np

st.markdown("## 🟣 Dashboard MU & Gedung (Executive)")

# =============================
# KPI
# =============================
k1, k2, k3, k4 = st.columns(4)

total_mu = int(df2["MU"].sum())
avg_mu = round(df2["MU"].mean(), 1)
gedung_count = df2["Gedung"].nunique()
alat_count = df2["Alat.1"].nunique()

k1.metric("Total MU", total_mu)
k2.metric("Rata-rata MU", avg_mu)
k3.metric("Jumlah Gedung", gedung_count)
k4.metric("Jumlah Alat", alat_count)

# =============================
# CHART ROW 1
# =============================
c1, c2 = st.columns(2)

with c1:
    fig = px.bar(
        df2,
        x="Gedung",
        y="MU",
        color="Gedung",
        title="Total MU per Gedung",
        color_discrete_sequence=px.colors.sequential.Purples
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.bar(
        df2,
        x="Alat.1",
        y="MU",
        color="Alat.1",
        title="Total MU per Alat",
        color_discrete_sequence=px.colors.sequential.Purples
    )
    st.plotly_chart(fig, use_container_width=True)

# =============================
# CHART ROW 2
# =============================
c3, c4 = st.columns(2)

with c3:
    fig = px.line(
        df2.sort_values("Tgl"),
        x="Tgl",
        y="MU",
        color="Gedung",
        title="Tren MU per Tanggal",
        color_discrete_sequence=px.colors.sequential.Purples
    )
    st.plotly_chart(fig, use_container_width=True)

with c4:
    fig = px.pie(
        df2,
        names="Gedung",
        values="MU",
        hole=0.5,
        title="Proporsi MU per Gedung",
        color_discrete_sequence=px.colors.sequential.Purples
    )
    st.plotly_chart(fig, use_container_width=True)

# =============================
# MONTH OVER MONTH
# =============================
st.markdown("### 📈 Perbandingan Bulanan (MoM)")

df2["YearMonth"] = df2["Tgl"].dt.to_period("M")

bulan_urut = sorted(df2["YearMonth"].dropna().unique())

if len(bulan_urut) >= 2:
    curr = bulan_urut[-1]
    prev = bulan_urut[-2]

    mu_curr = df2[df2["YearMonth"] == curr]["MU"].sum()
    mu_prev = df2[df2["YearMonth"] == prev]["MU"].sum()

    delta = mu_curr - mu_prev
    delta_pct = (delta / mu_prev * 100) if mu_prev != 0 else 0

    st.metric(
        label=f"MU {curr} vs {prev}",
        value=int(mu_curr),
        delta=f"{round(delta_pct,1)} %"
    )
else:
    st.info("Data belum cukup untuk perbandingan bulanan")

# =============================
# RANKING
# =============================
st.markdown("### 🏆 Ranking")

r1, r2 = st.columns(2)

with r1:
    top_gedung = (
        df2.groupby("Gedung")["MU"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    st.markdown("**Top Gedung berdasarkan MU**")
    st.dataframe(top_gedung, use_container_width=True)

with r2:
    top_alat = (
        df2.groupby("Alat.1")["MU"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    st.markdown("**Top Alat berdasarkan MU**")
    st.dataframe(top_alat, use_container_width=True)
